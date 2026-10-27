"""Charts refresh directly from the merger engine."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from eqt_range.engine import calculate

out=Path(__file__).resolve().parent
b=calculate()
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
fig,ax=plt.subplots(figsize=(8,3.1))
labels=['No synergies','Year 1\nincluding costs','Year 3\nrecurring','Company-adjusted\nbefore PPA']
ys=[b['no_synergy_accretion'],b['years'][0]['inclusive_accretion'],b['years'][2]['recurring_accretion'],b['years'][2]['company_accretion']]
ax.bar(labels,[v*100 for v in ys],color=['#A63C3C','#A63C3C','#1F3864','#7C96BA'],width=.6)
ax.axhline(0,color='#777777',linewidth=.8);ax.set_ylabel('EPS accretion / dilution (%)')
for i,v in enumerate(ys):ax.text(i,v*100+(.3 if v>=0 else -.35),f'{v:+.1%}',ha='center',va='bottom' if v>=0 else 'top')
ax.set_ylim(-9.1,6.2);fig.tight_layout();fig.savefig(out/'eps_bridge.png',dpi=180);plt.close(fig)
fig,ax=plt.subplots(figsize=(8,3.1))
syn=list(range(100,501,10));val=[calculate({'synergy':s})['value_surplus'] for s in syn]
ax.plot(syn,val,color='#1F3864',linewidth=2);ax.axhline(0,color='#777777',linewidth=.8)
ax.axvline(325,color='#A63C3C',linestyle='--',label='Management base target: USD325m')
ax.axvline(b['value_breakeven_synergy'],color='#62856A',linestyle=':',label=f'Value break-even: USD{b["value_breakeven_synergy"]:.0f}m')
ax.set_xlabel('Annual pre-tax synergies (USDm)');ax.set_ylabel('Value surplus after premium (USDm)');ax.legend(frameon=False,fontsize=8)
fig.tight_layout();fig.savefig(out/'synergy_value.png',dpi=180);plt.close(fig)
