"""Execute na raiz do repositório: python scripts/organizar_resultados.py
Copia relatórios sem apagar originais; bloqueia cópias conflitantes.
"""
from pathlib import Path
import io,json,zipfile,hashlib,re
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
REPORTS=ROOT/'reports'; TABLES=REPORTS/'results'
def digest(b):return hashlib.sha256(b).hexdigest()
def write_checked(path,content):
    if path.exists() and path.read_bytes()!=content:
        raise RuntimeError(f'Conflito; nenhum arquivo existente será substituído: {path}')
    path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(content)
def collect():
    result=[]
    for p in REPORTS.rglob('test_metrics.json'):
        result.append((p.as_posix(),{q.name:q.read_bytes() for q in p.parent.glob('test_*') if q.is_file()}))
    for p in REPORTS.rglob('*.zip'):
        with zipfile.ZipFile(p) as z:
            for n in z.namelist():
                if n.endswith('/test_metrics.json'):
                    prefix=n.rsplit('/',1)[0]+'/'
                    result.append((p.as_posix()+'::'+n,{Path(q).name:z.read(q) for q in z.namelist() if q.startswith(prefix+'test_') and '/' not in q[len(prefix):] and not q.endswith('/')}))
    return result
sources=collect();df=pd.read_csv(TABLES/'test_summary.csv')
assert len(df)==29 and df['split'].eq('test').all()
plan=[]
for i,row in df.iterrows():
    suffix=re.search(r'(p\d+_seed\d+(?:_[0-9a-f]+|/[0-9a-f]+))$',row.source_run_path).group(1)
    matches=[(s,b) for s,b in sources if '/'+suffix+'/test_metrics.json' in '/'+s]
    if not matches:raise FileNotFoundError(f'Falta relatório de {suffix}; mantenha os ZIPs originais em reports/.')
    blobs={}
    for s,files in matches:
        for name,b in files.items():
            if name in blobs and blobs[name]!=b:raise RuntimeError(f'Cópias conflitantes: {suffix}/{name}')
            blobs[name]=b
    for name in ['test_metrics.json','test_predictions.csv','test_confusion_counts.csv','test_confusion_normalized.csv']:
        assert name in blobs,(suffix,name)
    m=json.loads(blobs['test_metrics.json'])
    assert m['n']==2797
    for k in ['macro_f1','accuracy','balanced_accuracy','auroc_macro']:
        assert abs(m[k]-row[k])<1e-9,(suffix,k)
    base=REPORTS/('partial_ft' if row.adaptation=='partial_finetuning' else 'linear_probe')/('dinov3' if row.model=='dinov3_vitl16' else 'resnet50')/suffix
    for name,b in blobs.items():
        target=base/name
        if target.exists() and target.read_bytes()!=b:raise RuntimeError(f'Conflito: {target}')
        plan.append((target,b))
    df.loc[i,'run_path']=base.relative_to(ROOT).as_posix()
    for column,name in [('metrics_path','test_metrics.json'),('predictions_path','test_predictions.csv')]:df.loc[i,column]=(base/name).relative_to(ROOT).as_posix()
# Todos os conflitos são checados antes das cópias.
for p,b in plan:write_checked(p,b)
original=TABLES/'test_summary_before_organization.csv'
if not original.exists():original.write_bytes((TABLES/'test_summary.csv').read_bytes())
df.to_csv(TABLES/'test_summary.csv',index=False)
for col in ['run_path','metrics_path','predictions_path']:assert df[col].map(lambda x:(ROOT/x).exists()).all()
# Atualiza índice das figuras sem caminhos absolutos da máquina.
index=TABLES/'confusion_figures_index.csv'
if index.exists():
    idx=pd.read_csv(index);keys=['model','adaptation','train_fraction_pct','subset_seed']
    lookup=df.set_index(keys)
    for i,row in idx.iterrows():
        key=tuple(row[k] for k in keys)
        if key in lookup.index:
            idx.loc[i,'detail']=lookup.loc[key,'run_path']+'/test_confusion_counts.csv'
    idx.to_csv(index,index=False)
print('29 avaliações organizadas. Originais preservados; caminhos relativos corrigidos.')
