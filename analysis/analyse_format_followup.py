"""Exploratory follow-up analysis, separated from prespecified core contrasts."""
import collections
import hashlib
import json
import statistics
from pathlib import Path
from analyse_focused_study import paired,holm,write_csv
from focused_scoring import score_record
ROOT=Path(__file__).resolve().parents[1];folder=ROOT/'experiment/focused';out=ROOT/'audit/focused_study'
calls=[json.loads(l) for l in (folder/'followup-calls.jsonl').read_text().splitlines()]
responses=[json.loads(l) for l in (folder/'run/followup-responses.jsonl').read_text().splitlines()]
assert len(calls)==len(responses)==600
byid={r['call_id']:r for r in responses};assert len(byid)==600
design=json.loads((folder/'followup-design.json').read_text())
core=[json.loads(l) for l in (out/'scored.jsonl').read_text().splitlines()]
lookup={(r['model'],r['item_id'],r['language']):r for r in core if r['answer_format']=='brief' and r['translation_arm']=='published'}
core_raw={r['call_id']:r for r in map(json.loads,(folder/'run/responses.jsonl').read_text().splitlines())}
scored=[];groups=collections.defaultdict(list)
def adherence(rs):
    # Surface evidence only: absence of marker is separately reported, never
    # automatically classified as an explanation or a valid calculation.
    return {'requests':len(rs),'marker_present':sum('####' in r.get('response_text','') for r in rs),
            'text_before_marker':sum('####' in r.get('response_text','') and bool(r['response_text'].rsplit('####',1)[0].strip()) for r in rs),
            'median_completion_tokens':statistics.median(r['raw']['usage']['completion_tokens'] for r in rs if r['status']=='success')}
for c in calls:
    r=byid[c['call_id']];assert r['model']==c['model']
    s={k:c[k] for k in ['call_id','model','item_id','language','answer_format']};s.update(score_record(c,r));scored.append(s)
    groups[c['model'],c['language']].append(s)
(out/'followup-scored.jsonl').write_text(''.join(json.dumps(s)+'\n' for s in scored))
contrasts=[];cells=[];adherence_rows=[]
for i,((model,lang),rs) in enumerate(sorted(groups.items())):
    pairs=[(lookup[model,r['item_id'],lang],r) for r in rs]
    contrast={'family':'posthoc_format','model':model,'language':lang};contrast.update(paired(pairs,20260913+100+i));contrasts.append(contrast)
    for label,data,raw in [('restrictive_brief',[a for a,b in pairs],[core_raw[a['call_id']] for a,b in pairs]),
                           ('minimal_brief',rs,[byid[r['call_id']] for r in rs])]:
        row={'model':model,'language':lang,'instruction':label,'N':len(data),'observed':sum(r['correct'] is not None for r in data),'correct':sum(r['correct'] is True for r in data)}
        row['conditional_accuracy']=row['correct']/row['observed'] if row['observed'] else None
        row['bound_low']=row['correct']/row['N'];row['bound_high']=(row['correct']+row['N']-row['observed'])/row['N'];cells.append(row)
        ar={'model':model,'language':lang,'instruction':label};ar.update(adherence(raw));adherence_rows.append(ar)
holm(contrasts)
write_csv(out/'followup-contrasts.csv',contrasts);write_csv(out/'followup-cells.csv',cells);write_csv(out/'followup-adherence.csv',adherence_rows)
summary={'recorded':600,'status_counts':dict(collections.Counter(r['status'] for r in scored))}
(out/'followup-summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
print(json.dumps(cells,indent=2));print(json.dumps(contrasts,indent=2));print(json.dumps(adherence_rows,indent=2))
