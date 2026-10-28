import numpy as np
import pandas as pd
from PIL import Image
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix, roc_auc_score

CLASSES = ['AMD','CNV','CSR','DME','DR','DRUSEN','MH','NORMAL']

def make_subsets(manifest, seeds=(17,42,2026), percentages=(1,5,10,25,100)):
    train=manifest.loc[manifest.split=='train'].copy()
    result={}
    for seed in seeds:
        permutations={}
        for cls in range(8):
            rows=train.loc[train.class_id==cls].sort_values('image_id').reset_index(drop=True)
            rng=np.random.default_rng(np.random.SeedSequence([seed,cls]))
            permutations[cls]=rows.iloc[rng.permutation(len(rows))]
        previous=set()
        for pct in percentages:
            parts=[rows.iloc[:max(1,len(rows)*pct//100)] for rows in permutations.values()]
            subset=pd.concat(parts).sort_values('image_id').reset_index(drop=True)
            ids=set(subset.image_id)
            assert previous.issubset(ids)
            previous=ids
            result[(seed,pct)]=subset
        assert previous==set(train.image_id)
    return result

def prepare_rgb(path):
    # Imagem inteira; distorce a proporção original, sem recorte/padding.
    with Image.open(path) as im:
        return im.convert('RGB').resize((224,224),Image.Resampling.BICUBIC)

def normalize_rgb(image, mean, std):
    mean=np.asarray(mean,dtype=np.float32); std=np.asarray(std,dtype=np.float32)
    if mean.shape!=(3,) or std.shape!=(3,) or not np.isfinite(mean).all() or not np.isfinite(std).all() or (std<=0).any():
        raise ValueError('Informe mean/std verificados para os três canais.')
    x=np.asarray(image,dtype=np.float32)/255.0
    if x.shape!=(224,224,3): raise ValueError('Esperado RGB 224x224.')
    return ((x-mean)/std).transpose(2,0,1).copy()

def evaluate_predictions(reference, predictions):
    columns=['p_'+c for c in CLASSES]
    if not {'image_id','class_id'}.issubset(reference.columns): raise ValueError('Referência inválida.')
    if not {'image_id',*columns}.issubset(predictions.columns): raise ValueError('Faltam probabilidades por classe.')
    if not reference.image_id.is_unique or not predictions.image_id.is_unique: raise ValueError('IDs duplicados.')
    if len(reference)==0 or set(reference.image_id)!=set(predictions.image_id): raise ValueError('IDs não correspondem.')
    labels=reference.class_id.to_numpy()
    if not np.isin(labels,np.arange(8)).all(): raise ValueError('Rótulos fora de 0..7.')
    aligned=reference[['image_id','class_id']].merge(predictions[['image_id']+columns],on='image_id',validate='one_to_one')
    y=aligned.class_id.to_numpy(dtype=int); p=aligned[columns].to_numpy(dtype=float)
    if not np.isfinite(p).all() or (p<0).any() or (p>1).any() or not np.allclose(p.sum(1),1,atol=1e-5):
        raise ValueError('Esperadas probabilidades finitas, entre 0 e 1, somando 1; não logits.')
    pred=p.argmax(1)
    cm=confusion_matrix(y,pred,labels=np.arange(8)); support=cm.sum(1)
    recall=[float(cm[i,i]/support[i]) if support[i] else None for i in range(8)]
    auc=[float(roc_auc_score((y==i).astype(int),p[:,i])) if 0<(y==i).sum()<len(y) else None for i in range(8)]
    acc=float(accuracy_score(y,pred)); ba=float(np.mean([r for r in recall if r is not None]))
    balanced=bool((support>0).all() and (support==support[0]).all())
    if balanced and not np.isclose(acc,ba): raise AssertionError('Erro em métricas de conjunto balanceado.')
    metrics={'n':len(y),'class_order':CLASSES,'macro_f1':float(f1_score(y,pred,labels=np.arange(8),average='macro',zero_division=0)),
             'accuracy':acc,'balanced_accuracy':ba,'balanced_accuracy_scope':'classes_present',
             'recall_per_class':dict(zip(CLASSES,recall)),'support':dict(zip(CLASSES,map(int,support))),
             'auroc_per_class':dict(zip(CLASSES,auc)),
             'auroc_macro':float(np.mean(auc)) if all(a is not None for a in auc) else None,
             'auroc_macro_defined_classes':float(np.mean([a for a in auc if a is not None])) if any(a is not None for a in auc) else None,
             'auroc_classes_defined':sum(a is not None for a in auc),
             'balanced_support':balanced,'accuracy_minus_balanced_accuracy':acc-ba}
    normalized=np.divide(cm,support[:,None],out=np.zeros_like(cm,dtype=float),where=support[:,None]!=0)
    return metrics,pd.DataFrame(cm,index=CLASSES,columns=CLASSES),pd.DataFrame(normalized,index=CLASSES,columns=CLASSES)
