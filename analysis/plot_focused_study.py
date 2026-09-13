"""Draw fixed-sample outcome decomposition from the audited prospective labels."""
import collections
import json
import os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'.mpl-cache'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

rows=[json.loads(l) for l in (ROOT/'audit/focused_study/scored.jsonl').read_text().splitlines()]
design=json.loads((ROOT/'experiment/focused/design.json').read_text())
models=design['models'];short=['Qwen2.5-7B','Mistral-7B-v0.3'];langs=['en','zh','es']
colors=['#287D8E','#D78642','#D8D8D8']
plt.rcParams.update({'font.size':12})
fig,axes=plt.subplots(1,2,figsize=(8.4,4.6),sharex=True)
for ax,model,label in zip(axes,models,short):
    selected=[r for r in rows if r['model']==model and r['translation_arm']=='published' and r['answer_format']=='brief']
    y=np.arange(3);left=np.zeros(3)
    vals=[]
    for lang in langs:
        group=[r for r in selected if r['language']==lang];assert len(group)==250
        vals.append([sum(r['correct'] is True for r in group),sum(r['correct'] is False for r in group),sum(r['correct'] is None for r in group)])
    for j,(name,color) in enumerate(zip(['Observed correct','Observed incorrect','Unscored'],colors)):
        width=np.array([v[j] for v in vals])/250
        ax.barh(y,width,left=left,color=color,label=name,height=.6,edgecolor='white',linewidth=.5)
        for yy,w,l,v in zip(y,width,left,[v[j] for v in vals]):
            if v>=8:ax.text(l+w/2,yy,str(v),va='center',ha='center',fontsize=12,color='white' if j==0 else '#222222')
        left+=width
    ax.set(yticks=y,yticklabels=['English','Chinese','Spanish'],xlim=(0,1),title=label,xlabel='Fraction of 250 requested answers')
    ax.invert_yaxis();ax.spines[['top','right','left']].set_visible(False)
    ax.tick_params(axis='y',length=0);ax.set_axisbelow(True);ax.grid(axis='x',alpha=.15)
handles,labels=axes[0].get_legend_handles_labels()
fig.legend(handles,labels,loc='lower center',ncol=3,frameon=False,bbox_to_anchor=(.5,.01))

fig.tight_layout(rect=(0,.11,1,.94))
out=ROOT/'manuscript/figures';out.mkdir(exist_ok=True)
fig.savefig(out/'focused-outcomes.pdf',bbox_inches='tight')
fig.savefig(out/'focused-outcomes.png',dpi=200,bbox_inches='tight')
print('Created focused-outcomes.pdf and .png from scored.jsonl')
