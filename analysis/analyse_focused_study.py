"""Reproducible paired analyses of the prospective fixed study manifest."""
import argparse
import collections
import csv
import hashlib
import json
import math
from decimal import Decimal
from pathlib import Path
import numpy as np
from focused_scoring import score_record

ROOT = Path(__file__).resolve().parents[1]


def wilson(k,n):
    if not n:return [None,None]
    z=1.959963984540054; p=k/n; d=1+z*z/n
    mid=(p+z*z/(2*n))/d
    half=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return [mid-half,mid+half]


def mcnemar(b,c):
    n=b+c
    if not n:return 1.
    return min(1.,2*sum(math.comb(n,k) for k in range(min(b,c)+1))/2**n)


def paired(rows, seed):
    """Rows are (A,B), contrast B-A; retain one-sided labels for bounds."""
    counts=collections.Counter(); low=high=0; equal=shared_wrong=0
    for a,b in rows:
        x=a['correct'];y=b['correct']
        low+=(int(y) if y is not None else 0)-(int(x) if x is not None else 1)
        high+=(int(y) if y is not None else 1)-(int(x) if x is not None else 0)
        if x is None or y is None:continue
        counts[(x,y)]+=1
        same=Decimal(a['prediction'])==Decimal(b['prediction'])
        equal+=same;shared_wrong+=same and not x and not y
    n=sum(counts.values()); N=len(rows)
    b=counts[(True,False)];c=counts[(False,True)]
    ci=[None,None]
    if n:
        # Multinomial counts are exactly equivalent to resampling question rows
        # for this contrast's {-1,0,+1} statistic.
        draws=np.random.default_rng(seed).multinomial(n,[b/n,(n-b-c)/n,c/n],10000)
        ci=np.quantile((draws[:,2]-draws[:,0])/n,[.025,.975]).tolist()
    return {'N':N,'complete_pairs':n,'both_correct':counts[(True,True)],
            'a_only_correct':b,'b_only_correct':c,'neither_correct':counts[(False,False)],
            'difference_b_minus_a':(c-b)/n if n else None,
            'difference_ci_low':ci[0],'difference_ci_high':ci[1],
            'difference_bound_low':low/N,'difference_bound_high':high/N,
            'discordance':(b+c)/n if n else None,
            'equal_numeric_answers':equal,'equal_wrong_numeric_answers':shared_wrong,
            'mcnemar_p':mcnemar(b,c) if n else None}


def holm(records):
    valid=sorted([r for r in records if r['mcnemar_p'] is not None],key=lambda r:r['mcnemar_p'])
    last=0
    for i,r in enumerate(valid):
        last=max(last,min(1,(len(valid)-i)*r['mcnemar_p']))
        r['holm_p']=last


def write_csv(path,rows):
    with path.open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--allow-partial',action='store_true');args=ap.parse_args()
    folder=ROOT/'experiment/focused';out=ROOT/'audit/focused_study';out.mkdir(parents=True,exist_ok=True)
    calls=[json.loads(l) for l in (folder/'calls.jsonl').read_text().splitlines()]
    responses=[json.loads(l) for l in (folder/'run/responses.jsonl').read_text().splitlines()]
    design=json.loads((folder/'design.json').read_text())
    byid={r['call_id']:r for r in responses};assert len(byid)==len(responses)
    assert set(byid)<={c['call_id'] for c in calls}
    if not args.allow_partial:assert len(responses)==len(calls), 'Study incomplete'
    scored=[];lookup={}
    for c in calls:
        r=byid.get(c['call_id'])
        if r:assert r['model']==c['model']
        row={k:c[k] for k in ['call_id','model','item_id','language','translation_arm','answer_format']}
        row.update(score_record(c,r));scored.append(row)
        key=tuple(row[k] for k in ['model','item_id','language','translation_arm','answer_format'])
        assert key not in lookup;lookup[key]=row
    (out/'scored.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in scored))
    groups=collections.defaultdict(list)
    for r in scored:groups[tuple(r[k] for k in ['model','language','translation_arm','answer_format'])].append(r)
    cells=[]
    for key,rs in sorted(groups.items()):
        n=sum(r['correct'] is not None for r in rs);k=sum(r['correct'] is True for r in rs);N=len(rs)
        lo,hi=wilson(k,n)
        row=dict(zip(['model','language','translation_arm','answer_format'],key))
        row.update(N=N,observed=n,correct=k,conditional_accuracy=k/n if n else None,
                   wilson_low=lo,wilson_high=hi,bound_low=k/N,bound_high=(k+N-n)/N)
        for status in ['ok','answer_unparseable','generation_truncated','generation_failed','not_generated']:
            row[status]=sum(r['status']==status for r in rs)
        cells.append(row)
    write_csv(out/'cells.csv',cells)
    contrasts=[]
    def add(family,model,lang,ids,arm_a,arm_b,format_a,format_b,lang_a=None):
        pairs=[(lookup[(model,i,lang_a or lang,arm_a,format_a)],
                lookup[(model,i,lang,arm_b,format_b)]) for i in ids]
        r={'family':family,'model':model,'language':lang,
           'a':(lang_a or lang)+'/'+arm_a+'/'+format_a,'b':lang+'/'+arm_b+'/'+format_b}
        r.update(paired(pairs,20260913+len(contrasts)));contrasts.append(r)
    allids=sorted({c['item_id'] for c in calls})
    overlap=sorted({c['item_id'] for c in calls if c['translation_arm']=='archived'})
    for model in design['models']:
        for lang in ['zh','es']:
            add('language',model,lang,allids,'published','published','brief','brief','en')
            add('wording',model,lang,overlap,'archived','published','brief','brief')
        for lang in ['en','zh','es']:
            add('format',model,lang,design['format_item_ids'],'published','published','brief','number_only')
    for family in ['language','wording','format']:holm([r for r in contrasts if r['family']==family])
    write_csv(out/'contrasts.csv',contrasts)
    summary={'expected':len(calls),'recorded':len(responses),'statuses':dict(collections.Counter(r['status'] for r in scored)),
             'complete':len(responses)==len(calls)}
    (out/'summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
