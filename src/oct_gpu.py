"""GPU adapters and epoch-boundary partial fine-tuning."""
from pathlib import Path
import time,gc,json,random,math
import numpy as np
import pandas as pd
import torch
from torch import nn
from PIL import Image
from oct_protocol import CLASSES,evaluate_predictions
from oct_experiments import sha,digest,atomic_json,bind_config,save_evaluation

def seed_all(seed):
    random.seed(seed);np.random.seed(seed);torch.manual_seed(seed)
    if torch.cuda.is_available(): torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.benchmark=False
    torch.backends.cudnn.deterministic=True

def sync():
    if torch.cuda.is_available(): torch.cuda.synchronize()

def image_tensor(row,root,mean,std):
    p=Path(root)/row.relative_path
    assert sha(p)==row.file_sha256, f'Imagem diferente da auditada: {row.image_id}'
    with Image.open(p) as im: arr=np.array(im.convert('RGB').resize((224,224),Image.Resampling.BICUBIC),dtype=np.float32)/255.
    arr=(arr-np.asarray(mean,dtype=np.float32))/np.asarray(std,dtype=np.float32)
    return torch.from_numpy(arr.transpose(2,0,1).copy())

class RowsDataset(torch.utils.data.Dataset):
    def __init__(self,rows,root,mean,std): self.rows=rows.reset_index(drop=True);self.root=root;self.mean=mean;self.std=std
    def __len__(self):return len(self.rows)
    def __getitem__(self,i):
        row=self.rows.iloc[i]
        return image_tensor(row,self.root,self.mean,self.std),int(row.class_id),str(row.image_id)

def loader(rows,root,mean,std,batch,shuffle=False,generator=None):
    return torch.utils.data.DataLoader(RowsDataset(rows,root,mean,std),batch_size=batch,shuffle=shuffle,num_workers=0,pin_memory=torch.cuda.is_available(),generator=generator)

class Backbone:
    def __init__(self,name,device,cache,revision,token=None):
        self.name=name;self.device=torch.device(device); self.cache=Path(cache);self.cache.mkdir(parents=True,exist_ok=True)
        if name=='dinov3_vitl16':
            import transformers
            from transformers import AutoImageProcessor,AutoModel
            assert transformers.__version__=='4.56.2','Reinicie o kernel após instalar a versão fixada.'
            assert revision and len(revision)==40,'Fixe o commit DINOv3.'
            repo='facebook/dinov3-vitl16-pretrain-lvd1689m'
            proc=AutoImageProcessor.from_pretrained(repo,revision=revision,token=token,cache_dir=str(cache),use_fast=True)
            self.mean=list(proc.image_mean);self.std=list(proc.image_std)
            assert proc.do_normalize and proc.do_rescale and np.isclose(proc.rescale_factor,1/255)
            self.model=AutoModel.from_pretrained(repo,revision=revision,token=token,cache_dir=str(cache),torch_dtype=torch.float32,attn_implementation='sdpa')
            self.dim=int(self.model.config.hidden_size);assert self.dim==1024
            self.identity={'repo':repo,'revision':revision,'feature':'last_hidden_state[:,0,:] after final norm','processor':proc.to_dict()}
        elif name=='resnet50':
            from torchvision.models import resnet50,ResNet50_Weights
            from urllib.parse import urlparse
            torch.hub.set_dir(str(cache));w=ResNet50_Weights.IMAGENET1K_V2
            self.model=resnet50(weights=w);self.model.fc=nn.Identity();self.dim=2048
            t=w.transforms();self.mean=list(t.mean);self.std=list(t.std)
            weight_path=Path(torch.hub.get_dir())/'checkpoints'/Path(urlparse(w.url).path).name
            self.identity={'weights':'ResNet50_Weights.IMAGENET1K_V2','url':w.url,'weights_sha256':sha(weight_path),'feature':'global_avgpool_flatten_before_fc','geometry_override':'whole-image bicubic224 instead of official resize232 + center crop224'}
        else: raise ValueError(name)
        self.identity=json.loads(json.dumps(self.identity))
        self.model.eval().requires_grad_(False).to(self.device)
        self.preprocessing={'rgb':True,'size':[224,224],'resize':'PIL_BICUBIC_whole_image','crop':False,'aspect_ratio_preserved':False,'mean':self.mean,'std':self.std,'rescale':1/255,'augmentations':False}
    def forward(self,x):
        return self.model(pixel_values=x).last_hidden_state[:,0,:] if self.name=='dinov3_vitl16' else self.model(x)
    def embed(self,rows,root,batch=8):
        outputs=[];ids=[];labels=[]
        self.model.eval()
        with torch.inference_mode():
            for x,y,batch_ids in loader(rows,root,self.mean,self.std,batch):
                with torch.autocast(device_type=self.device.type,dtype=torch.float16,enabled=self.device.type=='cuda'):
                    z=self.forward(x.to(self.device,non_blocking=True))
                outputs.append(z.float().cpu().numpy());ids.extend(batch_ids);labels.extend(y.tolist())
        assert ids==rows.image_id.tolist() and labels==rows.class_id.tolist()
        result=np.concatenate(outputs);assert result.shape==(len(rows),self.dim) and np.isfinite(result).all()
        return result

def benchmark(adapter,rows,root,batches,total_images,folder):
    assert set(rows.split)=={'train'}
    report=[];device=adapter.device
    for batch in batches:
        try:
            adapter.embed(rows.iloc[:min(batch,len(rows))],root,batch);sync()
            if device.type=='cuda':torch.cuda.empty_cache();torch.cuda.reset_peak_memory_stats()
            sync();start=time.perf_counter();z=adapter.embed(rows,root,batch);sync();seconds=time.perf_counter()-start
            # Measure storage separately, to include it in the extrapolation.
            folder=Path(folder);folder.mkdir(parents=True,exist_ok=True);temp=folder/'benchmark_write.npz'
            s=time.perf_counter();np.savez_compressed(temp,embeddings=z);write_seconds=time.perf_counter()-s;temp.unlink()
            allocated=torch.cuda.max_memory_allocated()/2**30 if device.type=='cuda' else None
            reserved=torch.cuda.max_memory_reserved()/2**30 if device.type=='cuda' else None
            total=(seconds+write_seconds)*total_images/len(rows)
            report.append({'batch':batch,'ok':True,'n':len(rows),'seconds':seconds,'write_seconds':write_seconds,'images_per_second':len(rows)/seconds,'peak_allocated_gib':allocated,'peak_reserved_gib':reserved,'estimated_extraction_seconds':total,'budget_with_margin_seconds':total*1.3+600})
        except torch.cuda.OutOfMemoryError:
            gc.collect();torch.cuda.empty_cache();report.append({'batch':batch,'ok':False,'reason':'CUDA OOM'})
        atomic_json(Path(folder)/'benchmark.json',report)
    successful=[r for r in report if r['ok']]
    if device.type=='cuda':
        capacity=torch.cuda.get_device_properties(device).total_memory/2**30
        safe=[r for r in successful if r['peak_reserved_gib']<=.8*capacity]
    else:safe=successful
    if not safe:raise RuntimeError('Sem batch com margem de 20%; testar batches menores.')
    best=max(safe,key=lambda r:r['images_per_second'])
    atomic_json(Path(folder)/'batch_choice.json',best);return report,best['batch']

class PartialDINO(nn.Module):
    def __init__(self,backbone):
        super().__init__();self.backbone=backbone
        assert hasattr(backbone,'layer') and len(backbone.layer)>=2,'Arquitetura inesperada para transformers4.56.2.'
        self.backbone.requires_grad_(False)
        for block in self.backbone.layer[-2:]:block.requires_grad_(True)
        self.head=nn.Linear(backbone.config.hidden_size,8)
    def train(self,mode=True):
        super().train(mode);self.backbone.eval()
        for block in self.backbone.layer[-2:]:block.train(mode)
        self.head.train(mode);return self
    def forward(self,x):return self.head(self.backbone(pixel_values=x).last_hidden_state[:,0,:])

def trainable_state(net):return {n:p.detach().cpu().clone() for n,p in net.named_parameters() if p.requires_grad}
def restore_trainable(net,state):
    expected={n for n,p in net.named_parameters() if p.requires_grad};assert set(state)==expected
    with torch.no_grad():
        for n,p in net.named_parameters():
            if n in state:p.copy_(state[n].to(p.device))
def atomic_torch(path,obj):
    path=Path(path);tmp=path.with_suffix('.tmp');torch.save(obj,tmp);tmp.replace(path)
def optimizer_to(optimizer,device):
    for state in optimizer.state.values():
        for k,v in state.items():
            if torch.is_tensor(v):state[k]=v.to(device)

def probabilities(net,rows,adapter,root,batch):
    net.eval();result=[];ids=[];labels=[]
    with torch.no_grad():
        for x,y,bid in loader(rows,root,adapter.mean,adapter.std,batch):
            with torch.autocast(device_type=adapter.device.type,dtype=torch.float16,enabled=adapter.device.type=='cuda'):
                logits=net(x.to(adapter.device))
            result.append(torch.softmax(logits.float(),1).cpu().numpy());ids.extend(bid);labels.extend(y.tolist())
    assert ids==rows.image_id.tolist() and labels==rows.class_id.tolist()
    frame=pd.DataFrame(np.concatenate(result),columns=['p_'+c for c in CLASSES]);frame.insert(0,'image_id',ids);return frame

def fit_partial(adapter,train,val,root,folder,config):
    assert set(train.split)=={'train'} and set(val.split)=={'val'} and set(train.image_id).isdisjoint(val.image_id)
    seed_all(config['seed']);net=PartialDINO(adapter.model).to(adapter.device)
    folder=bind_config(folder,config);path=folder/'last.pt'
    if (folder/'result.json').exists():
        result=json.loads((folder/'result.json').read_text())
        assert sha(folder/'best.pt')==result['best_sha256']
        return result
    atomic_json(folder/'parameters.json',{'trainable':sum(p.numel() for p in net.parameters() if p.requires_grad),'total':sum(p.numel() for p in net.parameters()),'names':[n for n,p in net.named_parameters() if p.requires_grad]})
    optimizer=torch.optim.AdamW([p for p in net.parameters() if p.requires_grad],lr=config['lr'],weight_decay=config['weight_decay'])
    scaler=torch.amp.GradScaler('cuda',enabled=adapter.device.type=='cuda')
    generator=torch.Generator().manual_seed(config['seed'])
    start_epoch=0;history=[];best_score=-1.;best_state=None;best_epoch=-1;bad_epochs=0;done=False
    if path.exists():
        # Somente checkpoints criados por este projeto; torch pickle é confiado aqui.
        state=torch.load(path,map_location='cpu',weights_only=False)
        assert state['config']==config
        restore_trainable(net,state['trainable']);optimizer.load_state_dict(state['optimizer']);optimizer_to(optimizer,adapter.device);scaler.load_state_dict(state['scaler'])
        torch.set_rng_state(state['torch_rng']);np.random.set_state(state['numpy_rng']);random.setstate(state['python_rng'])
        if adapter.device.type=='cuda':torch.cuda.set_rng_state_all(state['cuda_rng'])
        generator.set_state(state['loader_rng']);start_epoch=state['next_epoch'];history=state['history'];best_score=state['best_score'];best_state=state['best_state'];best_epoch=state['best_epoch'];bad_epochs=state['bad_epochs'];done=state['done']
    for epoch in range(start_epoch,config['epochs']):
        if done:break
        trainloader=loader(train,root,adapter.mean,adapter.std,config['batch'],True,generator)
        net.train();optimizer.zero_grad(set_to_none=True);loss_sum=0.;group_n=0
        if adapter.device.type=='cuda':torch.cuda.reset_peak_memory_stats()
        sync();t=time.perf_counter()
        for step,(x,y,_) in enumerate(trainloader):
            x=x.to(adapter.device);y=y.to(adapter.device)
            with torch.autocast(device_type=adapter.device.type,dtype=torch.float16,enabled=adapter.device.type=='cuda'):
                loss=nn.functional.cross_entropy(net(x),y,reduction='sum')
            if not torch.isfinite(loss):raise FloatingPointError('Loss não finita; retome do checkpoint anterior após investigar.')
            scaler.scale(loss).backward();group_n+=len(y);loss_sum+=float(loss.detach())
            if (step+1)%config['accumulation']==0 or step+1==len(trainloader):
                scaler.unscale_(optimizer)
                for p in net.parameters():
                    if p.grad is not None:p.grad.div_(group_n)
                torch.nn.utils.clip_grad_norm_([p for p in net.parameters() if p.requires_grad],1.)
                scaler.step(optimizer);scaler.update();optimizer.zero_grad(set_to_none=True);group_n=0
        sync();train_seconds=time.perf_counter()-t;t=time.perf_counter()
        pred=probabilities(net,val,adapter,root,config['eval_batch']);sync();val_seconds=time.perf_counter()-t
        metrics,_,_=evaluate_predictions(val,pred);score=metrics['macro_f1']
        improved=score>best_score
        if improved:best_score=score;best_state=trainable_state(net);best_epoch=epoch;bad_epochs=0
        else:bad_epochs+=1
        done=bad_epochs>=config['patience'] or epoch+1==config['epochs']
        history.append({'epoch':epoch+1,'loss':loss_sum/len(train),'val_macro_f1':score,'train_seconds':train_seconds,'validation_seconds':val_seconds,'peak_allocated_gib':torch.cuda.max_memory_allocated()/2**30 if adapter.device.type=='cuda' else None,'improved':improved})
        state={'config':config,'trainable':trainable_state(net),'optimizer':optimizer.state_dict(),'scaler':scaler.state_dict(),'next_epoch':epoch+1,'history':history,'best_score':best_score,'best_state':best_state,'best_epoch':best_epoch,'bad_epochs':bad_epochs,'done':done,'torch_rng':torch.get_rng_state(),'cuda_rng':torch.cuda.get_rng_state_all() if adapter.device.type=='cuda' else [],'numpy_rng':np.random.get_state(),'python_rng':random.getstate(),'loader_rng':generator.get_state()}
        s=time.perf_counter();atomic_torch(path,state);save_seconds=time.perf_counter()-s
        history[-1]['checkpoint_seconds']=save_seconds
        atomic_json(folder/'history.json',history)
        print(history[-1])
    assert best_state is not None
    restore_trainable(net,best_state)
    pred=probabilities(net,val,adapter,root,config['eval_batch']);metrics=save_evaluation(folder,val,pred,'validation')
    atomic_torch(folder/'best.pt',{'config':config,'trainable':best_state,'best_epoch':best_epoch+1})
    result={'best_epoch':best_epoch+1,'validation_macro_f1':metrics['macro_f1'],'epochs_completed':len(history),'limit_reached':len(history)>=config['epochs'],'improved_at_limit':bool(history[-1]['improved'] and len(history)>=config['epochs']),'best_sha256':sha(folder/'best.pt')}
    atomic_json(folder/'result.json',result);return result
