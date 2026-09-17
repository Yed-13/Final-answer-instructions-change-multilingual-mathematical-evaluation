"""Render all validation cells/contrasts directly from saved analysis outputs."""
import csv,os
from pathlib import Path
R=Path(__file__).resolve().parents[1]
os.environ.setdefault('MPLCONFIGDIR',str(R/'.mpl-cache'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
cells=list(csv.DictReader((R/'audit/revision_study/cells.csv').open()))
cs=list(csv.DictReader((R/'audit/revision_study/contrasts.csv').open()))
sections=R/'manuscript/sections';sections.mkdir(parents=True,exist_ok=True)
models=sorted({r['model'] for r in cells});langs=['en','zh','es'];arms=['restrictive','minimal','clause_removed','scope_explicit'];names=['R','Minimal','Clause removed','Scope explicit']
lookup={(r['model'],r['language'],r['answer_format'],r['evaluator']):r for r in cells}
lines=[r'\begin{table}[!htbp]\centering\small',r'\caption{Validation outcomes on 136 questions per cell. Entries are correct/scoreable counts; every cell contains 136 requests. Prefix counts record text before the first marker, irrespective of correctness. R is the restrictive baseline.}',r'\label{tab:validation_cells}',r'\begin{tabular}{@{}lllrrr@{}}\toprule',r'Model & Language & Instruction & Strict & Marker-line & Prefix \\\midrule']
for model in models:
 for lang in langs:
  for arm,name in zip(arms,names):
   a=lookup[(model,lang,arm,'strict')];b=lookup[(model,lang,arm,'marker_line')]
   lines.append(f"{'Qwen' if model.startswith('Qwen') else 'Mistral'} & {lang} & {name} & {a['correct']}/{a['observed']} & {b['correct']}/{b['observed']} & {a['prefix_present']} \\\\")
  lines.append(r'\addlinespace')
lines += [r'\bottomrule\end{tabular}\end{table}']
for ev in ['strict','marker_line']:
 lines += [r'\begin{table}[!htbp]\centering\small',r'\caption{'+('Strict' if ev=='strict' else 'Marker-line')+r' evaluator: paired validation differences for each intervention minus R. Differences, 95\% question-bootstrap intervals (CI), and binary-completion bounds are percentage points. $n$ is the complete-pair count; CI is omitted when $n=1$. $p_H$ uses six comparisons within each intervention/evaluator family.}',r'\label{tab:validation_'+ev+'}',r'\begin{tabular}{@{}llrrrrr@{}}\toprule',r'Model/lang. & Intervention & $n$ & Difference & 95\% CI & Bounds & $p_H$ \\\midrule']
 for c in cs:
  if c['evaluator']!=ev:continue
  f=lambda key:float(c[key])*100
  ph=float(c['holm_p']);ps='<.001' if ph<.001 else f'{ph:.3f}'
  name=names[arms.index(c['arm'])];ml=('Qwen' if c['model'].startswith('Qwen') else 'Mistral')+'/'+c['language']
  ci=f"[{f('difference_ci_low'):.1f}, {f('difference_ci_high'):.1f}]" if int(c['complete_pairs'])>1 else '---'
  lines.append(f"{ml} & {name} & {c['complete_pairs']} & {f('difference_b_minus_a'):+.1f} & {ci} & [{f('difference_bound_low'):.1f}, {f('difference_bound_high'):.1f}] & {ps} \\\\")
 lines += [r'\bottomrule\end{tabular}\end{table}']
(sections/'validation-tables.tex').write_text('\n'.join(lines)+'\n')
plt.rcParams.update({'font.size':11})
fig,axes=plt.subplots(3,2,figsize=(8.5,8),sharex=True)
colors=['#287D8E','#D78642','#D8D8D8']
for col,model in enumerate(models):
 for row,lang in enumerate(langs):
  ax=axes[row,col];left=np.zeros(4)
  group=[lookup[(model,lang,a,'marker_line')] for a in arms]
  values=[[int(g['correct']),int(g['observed'])-int(g['correct']),136-int(g['observed'])] for g in group]
  for j,(label,color) in enumerate(zip(['Correct','Incorrect','Unscored'],colors)):
   vals=np.array([v[j] for v in values]);width=vals/136
   ax.barh(np.arange(4),width,left=left,label=label,color=color,edgecolor='white',height=.72)
   for y,w,l,n in zip(range(4),width,left,vals):
    if n>=9:ax.text(l+w/2,y,str(n),va='center',ha='center',fontsize=10,color='white' if j==0 else '#222222')
   left+=width
  ax.set(yticks=range(4),yticklabels=names,xlim=(0,1),title=('Qwen' if col==0 else 'Mistral')+' / '+dict(en='English',zh='Chinese',es='Spanish')[lang]);ax.invert_yaxis()
  ax.spines[['top','right','left']].set_visible(False);ax.tick_params(axis='y',length=0)
  if row==2:ax.set_xlabel('Fraction of 136 requests')
handles,labels=axes[0,0].get_legend_handles_labels();fig.legend(handles,labels,loc='lower center',ncol=3,frameon=False)
fig.tight_layout(rect=(0,.04,1,1));folder=R/'manuscript/figures';folder.mkdir(parents=True,exist_ok=True)
for ext in ['pdf','png']:fig.savefig(folder/('validation-outcomes.'+ext),dpi=200,bbox_inches='tight')
print('Rendered validation tables and outcome figure')

# Retain explicit display provenance required by the journal.
_caption_path=Path(__file__).resolve().parents[1]/'manuscript/sections/validation-tables.tex'
_caption_lines=_caption_path.read_text().splitlines()
_caption_path.write_text('\n'.join(line[:-1]+" Source: paired analyses of the study's scored responses.}" if line.startswith('\\caption{') and 'Source:' not in line else line for line in _caption_lines)+'\n')

# Keep each display near its corresponding discussion in the article.
import re
_parts=re.findall(r'\\begin\{table\}.*?\\end\{table\}',(R/'manuscript/sections/validation-tables.tex').read_text(),re.S)
for _name,_part in zip(['cells', 'strict', 'marker-line'],_parts):(R/('manuscript/sections/validation-'+_name+'.tex')).write_text(_part+'\n')
