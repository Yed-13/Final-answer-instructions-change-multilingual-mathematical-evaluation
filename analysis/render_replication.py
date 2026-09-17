"""Render the complete replication tables from saved cell and contrast CSVs."""
import csv
from pathlib import Path
R=Path(__file__).resolve().parents[1];folder=R/'audit/replication';sections=R/'manuscript/sections';sections.mkdir(parents=True,exist_ok=True)
cells=list(csv.DictReader((folder/'cells.csv').open()));cs=list(csv.DictReader((folder/'contrasts.csv').open()));models=sorted({c['model'] for c in cells});langs=['en','zh','es'];arms=['restrictive','clause_removed','scope_explicit'];names={'restrictive':'R','clause_removed':'Clause removed','scope_explicit':'Scope explicit'}
lookup={(c['model'],c['language'],c['answer_format'],c['evaluator']):c for c in cells}
lines=[r'\begin{table}[!htbp]\centering\small',r'\caption{MSVAMP replication outcomes on 200 questions per cell. Entries are correct/scoreable counts ($k/n$). Correct delivery is $k/200$, extraction coverage is $n/200$, and binary-completion bounds are $[k/200,(k+200-n)/200]$. Every planned response is included. Source: scored replication responses.}',r'\label{tab:replication_cells}',r'\begin{tabular}{@{}lllrr@{}}\toprule',r'Model & Language & Instruction & Strict & Marker-line \\\midrule']
for m in models:
 for l in langs:
  for a in arms:
   x,y=lookup[m,l,a,'strict'],lookup[m,l,a,'marker_line']
   lines.append(f"{'Qwen' if m.startswith('Qwen') else 'Mistral'} & {l} & {names[a]} & {x['correct']}/{x['observed']} & {y['correct']}/{y['observed']} \\\\")
  lines.append(r'\addlinespace')
lines.append(r'\bottomrule\end{tabular}\end{table}')
for ev in ['strict','marker_line']:
 lines += [r'\begin{table}[!htbp]\centering\small',r'\caption{MSVAMP '+('strict' if ev=='strict' else 'marker-line')+r' paired contrasts: intervention minus R. Differences, 95\% bootstrap intervals and binary-completion bounds are percentage points; $n$ is the complete-pair count. $p_H$ adjusts six model--language comparisons within each intervention/evaluator family. Source: paired replication outcomes.}',r'\label{tab:replication_'+ev+'}',r'\begin{tabular}{@{}llrrrrr@{}}\toprule',r'Model/lang. & Intervention & $n$ & Difference & 95\% CI & Bounds & $p_H$ \\\midrule']
 for c in cs:
  if c['evaluator']!=ev:continue
  f=lambda k:float(c[k])*100
  p=float(c['holm_p']);ps='<.001' if p<.001 else f'{p:.3f}'
  ci=f"[{f('difference_ci_low'):.1f}, {f('difference_ci_high'):.1f}]" if int(c['complete_pairs'])>1 else '---'
  lines.append(f"{'Qwen' if c['model'].startswith('Qwen') else 'Mistral'}/{c['language']} & {names[c['arm']]} & {c['complete_pairs']} & {f('difference_b_minus_a'):+.1f} & {ci} & [{f('difference_bound_low'):.1f}, {f('difference_bound_high'):.1f}] & {ps} \\\\")
 lines.append(r'\bottomrule\end{tabular}\end{table}')
(sections/'replication-tables.tex').write_text('\n'.join(lines)+'\n');print('Rendered replication tables')

# Keep each display near its corresponding discussion in the article.
import re
_parts=re.findall(r'\\begin\{table\}.*?\\end\{table\}',(R/'manuscript/sections/replication-tables.tex').read_text(),re.S)
for _name,_part in zip(['cells', 'strict', 'marker-line'],_parts):(R/('manuscript/sections/replication-'+_name+'.tex')).write_text(_part+'\n')
