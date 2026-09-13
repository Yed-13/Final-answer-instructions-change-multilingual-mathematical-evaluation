"""Check all validation paired counts, bounds and tests by a separate label join."""
import csv,json,math
from pathlib import Path
R=Path(__file__).resolve().parents[1];D=R/'audit/revision_study'
rows=[json.loads(l) for l in (D/'scored.jsonl').read_text().splitlines()];lookup={(r['model'],r['language'],r['item_id'],r['answer_format'],r['evaluator']):r['correct'] for r in rows};ids=sorted({r['item_id'] for r in rows});contrasts=list(csv.DictReader((D/'contrasts.csv').open()));families={}
for c in contrasts:
 a=[lookup[c['model'],c['language'],i,'restrictive',c['evaluator']] for i in ids];b=[lookup[c['model'],c['language'],i,c['arm'],c['evaluator']] for i in ids]
 complete=[(x,y) for x,y in zip(a,b) if x is not None and y is not None]
 n=len(complete);loss=sum(x and not y for x,y in complete);gain=sum(y and not x for x,y in complete)
 assert n==int(c['complete_pairs']) and loss==int(c['a_only_correct']) and gain==int(c['b_only_correct'])
 # Independent aggregate derivation of binary-completion difference bounds.
 ka=sum(x is True for x in a);kb=sum(x is True for x in b);ua=sum(x is None for x in a);ub=sum(x is None for x in b)
 lo=(kb-ka-ua)/len(ids);hi=(kb+ub-ka)/len(ids)
 assert abs(lo-float(c['difference_bound_low']))<1e-12 and abs(hi-float(c['difference_bound_high']))<1e-12
 p=min(1,2*sum(math.comb(gain+loss,j)*.5**(gain+loss) for j in range(min(gain,loss)+1))) if gain+loss else 1.
 assert abs(p-float(c['mcnemar_p']))<1e-12
 families.setdefault((c['evaluator'],c['arm']),[]).append((p,c))
for family in families.values():
 ordered=sorted(family,key=lambda x:x[0]);adjusted=[]
 for j,(p,c) in enumerate(ordered):
  q=min(1,max((len(ordered)-i)*ordered[i][0] for i in range(j+1)))
  assert abs(q-float(c['holm_p']))<1e-12
result={'validated_contrasts':len(contrasts),'checks':['paired counts','aggregate binary-completion bounds','exact sign/McNemar probabilities','Holm families'],'status':'pass'}
(R/'audit/independent-statistics.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
