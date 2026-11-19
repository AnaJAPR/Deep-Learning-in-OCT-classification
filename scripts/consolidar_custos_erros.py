from pathlib import Path
import json
import pandas as pd
ROOT=Path(__file__).resolve().parents[1];R=ROOT/'reports';T=R/'results'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
rows=[]
for model in ['dinov3','resnet50']:
    p=R/'embeddings'/model/'complete.json';j=read(p)
    rows.append(dict(model=model,stage='extraction_recorded_call',run=model,seconds=j['seconds'],source=p.relative_to(ROOT).as_posix(),scope=f"new={j.get('new')}; reused={j.get('reused')}; duração da chamada registrada, não necessariamente de todas as sessões"))
    for p in (R/'linear_probe'/model).glob('*/trials.json'):
        trials=read(p)
        rows.append(dict(model=model,stage='linear_search_fit',run=p.parent.name,seconds=sum(t['seconds'] for t in trials),source=p.relative_to(ROOT).as_posix(),scope=f'{len(trials)} candidatos; soma seconds, não duração integral da sessão'))
for p in (R/'partial_ft/dinov3').glob('p*/**/history.json'):
    h=read(p);assert len({e['epoch'] for e in h})==len(h)
    lock=read(p.parent.parent/'selection_lock.json');selected=Path(lock['selected']['run']).name==p.parent.name
    rows.append(dict(model='dinov3',stage='partial_ft_candidate',run=p.parent.relative_to(R).as_posix(),seconds=sum(e['train_seconds']+e['validation_seconds']+e['checkpoint_seconds'] for e in h),selected=selected,peak_allocated_gib=max(e['peak_allocated_gib'] for e in h),source=p.relative_to(ROOT).as_posix(),scope=f'{len(h)} épocas; treino+validação+checkpoint; exclui carregamento e avaliação final'))
c=pd.DataFrame(rows);c.to_csv(T/'cost_runs.csv',index=False)
c.groupby(['model','stage']).agg(seconds=('seconds','sum'),records=('run','count')).reset_index().to_csv(T/'cost_summary.csv',index=False)
d=pd.read_csv(T/'test_summary.csv');errors=[]
for _,row in d.iterrows():
    p=ROOT/row.run_path/'test_confusion_counts.csv';cm=pd.read_csv(p,index_col=0)
    for actual in cm.index:
        support=int(cm.loc[actual].sum())
        for predicted in cm.columns:
            if actual!=predicted:
                errors.append(dict(model=row.model,adaptation=row.adaptation,train_fraction_pct=row.train_fraction_pct,subset_seed=row.subset_seed,true_class=actual,predicted_class=predicted,count=int(cm.loc[actual,predicted]),fraction_of_true_class=float(cm.loc[actual,predicted]/support)))
e=pd.DataFrame(errors);e.to_csv(T/'confusion_pairs_by_run.csv',index=False)
e.groupby(['model','adaptation','train_fraction_pct','true_class','predicted_class']).agg(mean_count=('count','mean'),mean_fraction=('fraction_of_true_class','mean'),n_runs=('subset_seed','count')).reset_index().sort_values('mean_fraction',ascending=False).to_csv(T/'confusion_pairs_summary.csv',index=False)
print(c.groupby(['model','stage']).seconds.sum()/60)
print('Tabelas de custo e erros salvas em',T)
