"""Render manuscript tables and an auditable report from derived CSV files."""
import csv
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];folder=ROOT/'audit/focused_study'
output=ROOT/'manuscript';output.mkdir(parents=True,exist_ok=True)
cells=list(csv.DictReader((folder/'cells.csv').open()))
contrasts=list(csv.DictReader((folder/'contrasts.csv').open()))
short=lambda m:'Qwen' if m.startswith('Qwen') else 'Mistral'
def num(x,d=1):return f'{100*float(x):.{d}f}' if x not in ['',None] else '--'
def interval(a,b):return '['+num(a)+', '+num(b)+']'
def pvalue(x):return '$<0.001$' if float(x)<.001 else f'{float(x):.3f}'
def table(caption,spec,header,rows,label):
    return '\\begin{table}[ht]\n\\centering\\small\n\\caption{'+caption+'}\n\\begin{tabular}{'+spec+'}\\toprule\n'+header+'\\\\\\midrule\n'+'\n'.join(' & '.join(r)+'\\\\' for r in rows)+'\n\\bottomrule\n\\end{tabular}\\label{'+label+'}\n\\end{table}\n'
selected=[r for r in cells if r['translation_arm']=='published' and r['answer_format']=='brief']
rows=[[short(r['model']),r['language'],r['observed'],r['correct'],num(r['conditional_accuracy']),interval(r['wilson_low'],r['wilson_high']),interval(r['bound_low'],r['bound_high'])] for r in selected]
tex=table('Published-wording MGSM results under brief-solution instructions. Every row has 250 requested answers. $n$ is the scoreable count and $k$ the correct count. Accuracy and intervals are percentages; Wilson intervals condition on scoreable answers, whereas bounds allow every missing outcome to vary.','llrrrrr','Model & Language & $n$ & $k$ & $k/n$ & 95\\% Wilson & Bounds',rows,'tab:fresh-cells')
langs=[r for r in contrasts if r['family']=='language']
rows=[[short(r['model']),r['language'],r['complete_pairs'],r['both_correct'],r['a_only_correct'],r['b_only_correct'],r['neither_correct'],r['equal_wrong_numeric_answers']] for r in langs]
tex+=table('Paired English--target numerical correctness under published wording and brief-solution instructions. BC: both correct; E: English only correct; T: target only correct; NC: neither correct. SW counts equal wrong numerical answers and is a subset of NC. Each comparison requests 250 question pairs.','llrrrrrr','Model & Target & Pairs & BC & E & T & NC & SW',rows,'tab:fresh-pairs')
for family,title,label in [('language','Target-language minus English','tab:fresh-language'),('wording','Published minus archived wording','tab:fresh-wording'),('format','Number-only minus brief-solution instruction','tab:fresh-format')]:
    rs=[r for r in contrasts if r['family']==family]
    rows=[[short(r['model']),r['language'],r['complete_pairs'],num(r['difference_b_minus_a']),interval(r['difference_ci_low'],r['difference_ci_high']),interval(r['difference_bound_low'],r['difference_bound_high']),pvalue(r['holm_p'])] for r in rs]
    caption=title+' contrasts. Differences and intervals are percentage points. The 95\\% percentile interval resamples complete question pairs; bounds retain all requested pairs and allow missing correctness to vary. $p_H$ is the within-family Holm-adjusted exact McNemar value.'
    tex+=table(caption,'llrrrrr','Model & Language & Pairs & Difference & 95\\% interval & Bounds & $p_H$',rows,label)
(output/'focused-tables.tex').write_text(tex)
report=['# Prospective MGSM study results','',json.dumps(json.loads((folder/'summary.json').read_text()),indent=2),'','## Cell outcomes','']
for r in cells:report.append(f"- {short(r['model'])} {r['language']} {r['translation_arm']} {r['answer_format']}: {r['correct']}/{r['observed']} scoreable, N={r['N']}; conditional {num(r['conditional_accuracy'])}%; bounds {interval(r['bound_low'],r['bound_high'])}%.")
report+=['','## Paired contrasts','']
for r in contrasts:report.append(f"- {r['family']}, {short(r['model'])} {r['language']}: n={r['complete_pairs']}/{r['N']}, B-A {num(r['difference_b_minus_a'])} pp, bootstrap {interval(r['difference_ci_low'],r['difference_ci_high'])}; bounds {interval(r['difference_bound_low'],r['difference_bound_high'])}; Holm p={r['holm_p']}; equal-wrong {r['equal_wrong_numeric_answers']}.")
(folder/'REPORT.md').write_text('\n'.join(report)+'\n')
print('Rendered tables and REPORT.md')

# Retain explicit display provenance required by the journal.
_caption_path=Path(__file__).resolve().parents[1]/'manuscript/focused-tables.tex'
_caption_lines=_caption_path.read_text().splitlines()
_caption_path.write_text('\n'.join(line[:-1]+" Source: paired analyses of the study's scored responses.}" if line.startswith('\\caption{') and 'Source:' not in line else line for line in _caption_lines)+'\n')
