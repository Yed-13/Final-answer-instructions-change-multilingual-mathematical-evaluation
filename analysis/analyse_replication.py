"""Reproduce the prespecified MSVAMP outcomes using the frozen scorers."""
import collections,json
from pathlib import Path
from analyse_revision import read,line_score
from focused_scoring import score_record
from analyse_focused_study import paired,holm,write_csv
R=Path(__file__).resolve().parents[1]
def main():
 f=R/'experiment/replication';out=R/'audit/replication';out.mkdir(exist_ok=True)
 design=json.loads((f/'design.json').read_text());calls=read(f/'calls.jsonl');responses=read(f/'run/responses.jsonl');byid={r['call_id']:r for r in responses}
 assert len(byid)==len(responses)==len(calls)==3600
 rows=[];lookup={}
 for c in calls:
  r=byid[c['call_id']];assert r['model']==c['model']
  for ev,func in [('strict',score_record),('marker_line',line_score)]:
   row={k:c[k] for k in ['call_id','model','language','item_id','answer_format']};row.update(evaluator=ev,**func(c,r));rows.append(row);lookup[(c['model'],c['language'],c['item_id'],c['answer_format'],ev)]=row
 (out/'scored.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
 groups=collections.defaultdict(list)
 for r in rows:groups[tuple(r[k] for k in ['evaluator','model','language','answer_format'])].append(r)
 cells=[]
 for key,rs in sorted(groups.items()):
  N=len(rs);n=sum(r['correct'] is not None for r in rs);k=sum(r['correct'] is True for r in rs)
  row=dict(zip(['evaluator','model','language','answer_format'],key));row.update(N=N,observed=n,correct=k,correct_delivery=k/N,coverage=n/N,conditional_accuracy=k/n if n else None,bound_low=k/N,bound_high=(k+N-n)/N)
  for s in ['ok','answer_unparseable','generation_truncated','generation_failed']:row[s]=sum(r['status']==s for r in rs)
  cells.append(row)
 write_csv(out/'cells.csv',cells);contrasts=[]
 for ev in ['strict','marker_line']:
  for arm in ['clause_removed','scope_explicit']:
   family=[]
   for m in design['models']:
    for l in ['en','zh','es']:
     ps=[(lookup[(m,l,i,'restrictive',ev)],lookup[(m,l,i,arm,ev)]) for i in design['item_ids']]
     row=dict(evaluator=ev,arm=arm,model=m,language=l,**paired(ps,20260915+len(contrasts)))
     row['correct_delivery_difference']=sum(int(b['correct'] is True)-int(a['correct'] is True) for a,b in ps)/len(ps);family.append(row);contrasts.append(row)
   holm(family)
 write_csv(out/'contrasts.csv',contrasts)
 (out/'summary.json').write_text(json.dumps(dict(requests=len(calls),responses=len(responses),questions=200,termination_statuses=dict(collections.Counter(r['finish_reason'] for r in responses))),indent=2));print((out/'summary.json').read_text())
if __name__=='__main__':main()
