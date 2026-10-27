"""Charts from engine outputs; run with repository Python dependencies."""
import os
import sys
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR','/private/tmp/vitamin-mpl')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from vitamin import engine as E, assumptions as A

OUT=Path(__file__).resolve().parent/'charts';OUT.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8,'axes.spines.right':False,'axes.spines.top':False})
fig,axs=plt.subplots(1,2,figsize=(8.0,2.6),dpi=180)
for case,col in [('Downside','#C0392B'),('Base','#1F3864'),('Bull','#8C9FAD')]:
    r=E.run(case)
    axs[0].plot(A.YEARS,[x['leverage'] for x in r],marker='o',label=case,color=col)
    axs[1].plot(A.YEARS,[x['revolver'] for x in r],marker='o',label=case,color=col)
axs[0].axhline(A.value('max_leverage'),ls='--',color='#888888',label='Assumed limit')
axs[0].set_title('Gross funded debt / cash EBITDA');axs[0].set_ylabel('x');axs[0].legend(frameon=False,fontsize=6)
axs[1].axhline(A.RCF,ls='--',color='#888888');axs[1].set_title('Revolver drawn (SEKm)')
for ax in axs:ax.set_xticks(A.YEARS)
fig.tight_layout();fig.savefig(OUT/'credit_paths.png');plt.close(fig)

fig,ax=plt.subplots(figsize=(4,2.4),dpi=180)
xs=[4,5,6,7,8]
for h,col in [(.25,'#8C9FAD'),(.35,'#1F3864'),(.45,'#C0392B')]:
    ax.plot(xs,[100*E.recovery(multiple=m,haircut=h)['recovery'] for m in xs],marker='o',label=f'{h:.0%} EBITDA haircut',color=col)
ax.set_xlabel('Default EV / stressed cash EBITDA');ax.set_ylabel('First-lien recovery (%)');ax.set_ylim(0,105)
ax.legend(frameon=False,fontsize=6);fig.tight_layout();fig.savefig(OUT/'recovery.png');plt.close(fig)
