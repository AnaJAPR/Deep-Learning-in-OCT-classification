"""Shared CPU utilities: strict identities, resumable embeddings and linear selection."""
from pathlib import Path
import hashlib,json,time,warnings,os
import numpy as np
import pandas as pd
import joblib
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.exceptions import ConvergenceWarning
from oct_protocol import CLASSES,evaluate_predictions

def sha(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''): h.update(block)
    return h.hexdigest()
def digest(obj): return hashlib.sha256(json.dumps(obj,sort_keys=True,ensure_ascii=False,allow_nan=False).encode()).hexdigest()
def atomic_json(path,obj):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(path.suffix+'.tmp');tmp.write_text(json.dumps(obj,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf-8');tmp.replace(path)
def read_csv(path): return pd.read_csv(path,dtype={'image_id':str},keep_default_na=False)
def bind_config(folder,config):
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True);p=folder/'config.json'
    if p.exists():
        if json.loads(p.read_text())!=config: raise ValueError('Configuração mudou: use nova pasta.')
    else: atomic_json(p,config)
    return folder

def verify_lists(protocol_dir):
    root=Path(protocol_dir); manifest=read_csv(root/'manifest_used.csv')
    h=sha(root/'manifest_used.csv'); registry=json.loads((root/'data/splits/registry.json').read_text())
    assert registry['manifest_sha256']==h
    assert len(manifest)==23850 and manifest.image_id.is_unique and manifest.relative_path.is_unique
    assert manifest.groupby('split').size().to_dict()=={'test':2797,'train':18260,'val':2793}
    assert manifest.class_name.map(dict(zip(CLASSES,range(8)))).eq(manifest.class_id).all()
    assert manifest.read_ok.astype(str).str.lower().eq('true').all()
    for c in ['file_sha256','pixel_sha256']:
        assert manifest[c].str.fullmatch('[0-9a-f]{64}').all() and manifest[c].is_unique
    lookup=manifest.set_index('image_id'); result={}
    cols=['relative_path','class_name','class_id','split','file_sha256','pixel_sha256']
    for key,item in registry['subsets'].items():
        p=root/'data/splits'/item['file'];assert sha(p)==item['sha256'],str(p)
        df=read_csv(p);assert df.image_id.is_unique
        pd.testing.assert_frame_equal(df.set_index('image_id')[cols].sort_index(),lookup.loc[df.image_id,cols].sort_index())
        assert set(df.split)=={key if key in ['val','test'] else 'train'}
        result[key]=df
    for split in ['val','test']: assert set(result[split].image_id)==set(manifest.loc[manifest.split==split,'image_id'])
    for seed in [17,42,2026]:
        previous=set()
        for pct in [1,5,10,25,100]:
            df=result[f'p{pct:02d}_seed{seed}']; ids=set(df.image_id)
            assert previous<=ids;previous=ids
            for cls in range(8):
                n=((manifest.split=='train') & (manifest.class_id==cls)).sum()
                assert (df.class_id==cls).sum()==max(1,int(n)*pct//100)
        assert previous==set(manifest.loc[manifest.split=='train','image_id'])
    return manifest,result,h

def validate_chunk(path,rows,feature_id,dim):
    with np.load(path,allow_pickle=False) as z:
        assert z['feature_id'].item()==feature_id
        assert z['image_id'].tolist()==rows.image_id.tolist()
        assert z['class_id'].tolist()==rows.class_id.tolist()
        assert z['split'].tolist()==rows.split.tolist()
        x=z['embeddings'];assert x.shape==(len(rows),dim) and x.dtype==np.float32 and np.isfinite(x).all()
        return x.copy()

def extract_chunks(frame,folder,config,embed,chunk_size=256,max_new_chunks=None):
    folder=bind_config(folder,config);fid=digest(config); dim=config['dimension']
    frame=frame.sort_values(['split','image_id']).reset_index(drop=True)
    start=time.perf_counter();new=reused=0
    for split,part in frame.groupby('split',sort=True):
        part=part.reset_index(drop=True); sub=folder/split;sub.mkdir(exist_ok=True)
        for a in range(0,len(part),chunk_size):
            rows=part.iloc[a:a+chunk_size];path=sub/f'chunk_{a//chunk_size:05d}.npz'
            meta=path.with_suffix('.json')
            if path.exists():
                if meta.exists(): assert json.loads(meta.read_text())['sha256']==sha(path),'Bloco alterado.'
                validate_chunk(path,rows,fid,dim);reused+=1
            else:
                if max_new_chunks is not None and new>=max_new_chunks:
                    return {'complete':False,'new':new,'reused':reused,'seconds':time.perf_counter()-start}
                x=embed(rows).astype(np.float32)
                assert x.shape==(len(rows),dim) and np.isfinite(x).all()
                tmp=path.with_suffix('.tmp')
                with open(tmp,'wb') as f: np.savez_compressed(f,embeddings=x,image_id=rows.image_id.to_numpy(dtype=str),class_id=rows.class_id.to_numpy(dtype=np.int64),split=rows.split.to_numpy(dtype=str),feature_id=np.array(fid))
                tmp.replace(path);validate_chunk(path,rows,fid,dim);new+=1
            if not meta.exists(): atomic_json(meta,{'sha256':sha(path),'n':len(rows),'feature_id':fid})
            atomic_json(folder/'progress.json',{'last_chunk':str(path.relative_to(folder)),'new_this_call':new,'reused_this_call':reused})
    report={'complete':True,'new':new,'reused':reused,'seconds':time.perf_counter()-start,'feature_id':fid}
    atomic_json(folder/'complete.json',report);return report

def load_split(folder,reference,split):
    folder=Path(folder); cfg=json.loads((folder/'config.json').read_text());fid=digest(cfg)
    expected=reference.loc[reference.split==split].sort_values('image_id').reset_index(drop=True)
    assert len(expected)>0
    files=sorted((folder/split).glob('chunk_*.npz'));expected_n=(len(expected)+cfg['chunk_size']-1)//cfg['chunk_size']
    assert len(files)==expected_n, 'Extração incompleta ou blocos extras.'
    blocks=[]
    for i,p in enumerate(files):
        assert p.name==f'chunk_{i:05d}.npz'
        assert json.loads(p.with_suffix('.json').read_text())['sha256']==sha(p)
        blocks.append(validate_chunk(p,expected.iloc[i*cfg['chunk_size']:(i+1)*cfg['chunk_size']],fid,cfg['dimension']))
    return expected,np.concatenate(blocks)

def predict_frame(clf,X,ids):
    assert np.array_equal(clf.classes_,np.arange(8))
    p=pd.DataFrame(clf.predict_proba(X),columns=['p_'+c for c in CLASSES]);p.insert(0,'image_id',list(ids));return p

def save_evaluation(folder,reference,predictions,prefix):
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    m,cm,norm=evaluate_predictions(reference,predictions)
    atomic_json(folder/f'{prefix}_metrics.json',m)
    predictions.to_csv(folder/f'{prefix}_predictions.csv',index=False)
    cm.to_csv(folder/f'{prefix}_confusion_counts.csv');norm.to_csv(folder/f'{prefix}_confusion_normalized.csv')
    return m

def fit_linear(train_ref,Xtrain,val_ref,Xval,subset,folder,config):
    assert set(train_ref.split)=={'train'} and set(val_ref.split)=={'val'} and set(subset.split)=={'train'}
    assert set(train_ref.image_id).isdisjoint(val_ref.image_id)
    assert set(subset.image_id)<=set(train_ref.image_id) and subset.image_id.is_unique
    ids=subset.sort_values('image_id').image_id.tolist();positions=pd.Series(np.arange(len(train_ref)),index=train_ref.image_id)
    selected=positions.loc[ids].to_numpy(); X=Xtrain[selected];y=train_ref.iloc[selected].class_id.to_numpy()
    folder=bind_config(folder,config)
    if (folder/'selected.json').exists():
        result=json.loads((folder/'selected.json').read_text());assert sha(folder/'classifier.joblib')==result['classifier_sha256'];return result
    trials=[];best=None
    for C in sorted(config['C_grid']):
        start=time.perf_counter();clf=make_pipeline(StandardScaler(),LogisticRegression(C=C,solver='lbfgs',max_iter=config['max_iter'],random_state=17))
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter('always');clf.fit(X,y)
        messages=[str(w.message) for w in caught]
        valid=not any(issubclass(w.category,ConvergenceWarning) for w in caught)
        record={'C':C,'valid':valid,'warnings':messages,'seconds':time.perf_counter()-start}
        if valid:
            assert np.allclose(clf[0].mean_,X.mean(0),rtol=1e-4,atol=1e-5),'Scaler não usa só o subconjunto.'
            pred=predict_frame(clf,Xval,val_ref.image_id);m,_,_=evaluate_predictions(val_ref,pred)
            record['validation_macro_f1']=m['macro_f1']
            if best is None or m['macro_f1']>best[0]: best=(m['macro_f1'],C,clf,pred)
        trials.append(record);atomic_json(folder/'trials.json',trials)
    if best is None: raise RuntimeError('Nenhum candidato convergiu. Revisar orçamento igualmente para todos.')
    score,C,clf,pred=best;tmp=folder/'classifier.tmp';joblib.dump(clf,tmp);tmp.replace(folder/'classifier.joblib')
    m=save_evaluation(folder,val_ref,pred,'validation')
    chosen={'C':C,'validation_macro_f1':score,'classifier_sha256':sha(folder/'classifier.joblib'),'config_hash':digest(config),'test_used_for_selection':False}
    atomic_json(folder/'selected.json',chosen);return chosen
