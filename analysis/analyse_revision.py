"""Paired validation of prespecified instruction interventions and extraction sensitivity."""
import collections, hashlib, json, statistics
from pathlib import Path
from focused_scoring import final_number, score_record
from analyse_focused_study import paired, holm, write_csv, wilson
ROOT=Path(__file__).resolve().parents[1]

def marker_line_number(text):
    if not isinstance(text,str): return None
    if '####' not in text: return final_number(text)
    tail=text.rsplit('####',1)[1].strip()
    return final_number(tail.splitlines()[0]) if tail else None

def line_score(c,r):
    s=score_record(c,r)
    if s['status'] in ('generation_failed','generation_truncated','not_generated'): return s
    value=marker_line_number(r.get('response_text'))
    return dict(status='ok' if value is not None else 'answer_unparseable',prediction=str(value) if value is not None else None,correct=value==final_number(c['reference']) if value is not None else None)

def read(p): return [json.loads(l) for l in p.read_text().splitlines()]

def main():
    folder=ROOT/'experiment/revision';out=ROOT/'audit/revision_study';out.mkdir(exist_ok=True)
    design=json.loads((folder/'design.json').read_text());calls=read(folder/'calls.jsonl');responses=read(folder/'run/responses.jsonl')
    assert len(responses)==len(calls)==2448
    baseline_ids={c['baseline_call_id'] for c in calls}
    core=ROOT/'experiment/focused'
    originals=[dict(c,answer_format='restrictive') for c in read(core/'calls.jsonl') if c['call_id'] in baseline_ids]
    assert len(originals)==816
    calls+=originals
    responses += [r for r in read(core/'run/responses.jsonl') if r['call_id'] in baseline_ids]
    byid={r['call_id']:r for r in responses};assert len(byid)==len(responses)
    rows=[];lookup={}
    for c in calls:
        r=byid[c['call_id']];assert r['model']==c['model']
        text=r.get('response_text') or ''
        for evaluator,func in [('strict',score_record),('marker_line',line_score)]:
            row={k:c[k] for k in ['call_id','model','item_id','language','answer_format']}
            row.update(evaluator=evaluator,**func(c,r))
            row.update(marker_present='####' in text,prefix_present='####' in text and bool(text.split('####',1)[0].strip()),completion_tokens=r.get('raw',{}).get('usage',{}).get('completion_tokens'))
            rows.append(row);lookup[(c['model'],c['language'],c['item_id'],c['answer_format'],evaluator)]=row
    (out/'scored.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
    groups=collections.defaultdict(list)
    for r in rows:groups[tuple(r[k] for k in ['evaluator','model','language','answer_format'])].append(r)
    cells=[]
    for key,rs in sorted(groups.items()):
        N=len(rs);n=sum(r['correct'] is not None for r in rs);k=sum(r['correct'] is True for r in rs)
        row=dict(zip(['evaluator','model','language','answer_format'],key));row.update(N=N,observed=n,correct=k,conditional_accuracy=k/n if n else None,correct_delivery=k/N,bound_low=k/N,bound_high=(k+N-n)/N,prefix_present=sum(r['prefix_present'] for r in rs),marker_present=sum(r['marker_present'] for r in rs))
        for status in ['ok','answer_unparseable','generation_truncated','generation_failed']:row[status]=sum(r['status']==status for r in rs)
        cells.append(row)
    write_csv(out/'cells.csv',cells)
    contrasts=[]
    for ev in ['strict','marker_line']:
        for arm in design['arms']:
            family=[]
            for m in design['models']:
                for lang in ['en','zh','es']:
                    ps=[(lookup[(m,lang,i,'restrictive',ev)],lookup[(m,lang,i,arm,ev)]) for i in design['item_ids']]
                    row=dict(evaluator=ev,arm=arm,model=m,language=lang,**paired(ps,20260913+len(contrasts)%18))
                    row['correct_delivery_difference']=sum(int(b['correct'] is True)-int(a['correct'] is True) for a,b in ps)/len(ps)
                    family.append(row);contrasts.append(row)
            holm(family)
    write_csv(out/'contrasts.csv',contrasts)
    summary={'new_calls':2448,'baseline_calls':816,'recorded':len(responses)}
    (out/'summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
