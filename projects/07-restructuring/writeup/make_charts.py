"""Conditional funding charts, refreshed from engine."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from thames.engine import calculate
out=Path(__file__).resolve().parent
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
fig,ax=plt.subplots(figsize=(8,3.1))
for name,change,color in [('Existing capacity only',{'funding_case':1},'#A63C3C'),('Upsize and extension assumed',{},'#1F3864'),('Upsize, extension fails',{'maturity_case':0},'#9C7A36')]:
    r=calculate(change);ax.plot(range(12),[x['closing_cash'] for x in r['months']],label=name,color=color,linewidth=2)
ax.axhline(100,color='#888888',linestyle='--',linewidth=.8);ax.axhline(0,color='#777777',linewidth=.8)
ax.set_xticks(range(0,12,2),['Nov 26','Jan 27','Mar 27','May 27','Jul 27','Sep 27']);ax.set_ylabel('Unfunded cash position (GBPm)');ax.legend(frameon=False,fontsize=8)
fig.tight_layout();fig.savefig(out/'liquidity_cases.png',dpi=180);plt.close(fig)
fig,ax=plt.subplots(figsize=(8,3.1))
xs=list(range(12000,28001,200));ys=[calculate({'ev':x})['waterfall']['a_recovery']*100 for x in xs]
ax.plot([x/1000 for x in xs],ys,color='#1F3864',linewidth=2)
ax.axhline(69,color='#888888',linestyle='--',label='March 2026 c69% reference, not current')
ax.axvline(18,color='#A63C3C',linestyle=':',label='Illustrative GBP18bn EV')
ax.set_xlabel('Illustrative enterprise value (GBPbn)');ax.set_ylabel('Illustrative Class A recovery (%)');ax.legend(frameon=False,fontsize=8)
fig.tight_layout();fig.savefig(out/'recovery_sensitivity.png',dpi=180);plt.close(fig)
