"""Issuer cash timing and initial preferred mechanics, refreshed from engine."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from meta.engine import calculate

out=Path(__file__).resolve().parent;b=calculate()
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
fig,ax=plt.subplots(figsize=(8,3.1))
x=['Priced package','Immediate common\nillustrative','Straight debt\nillustrative']
initial=[b['initial_cash']/1000,b['net_total']/1000,b['net_total']/1000]
deferred=[b['forward_net']/1000,0,0]
ax.bar(x,initial,color='#1F3864',label='Net cash at expected close')
ax.bar(x,deferred,bottom=initial,color='#A8B9D0',label='Deferred net proceeds')
ax.text(0,initial[0]/2,f"USD{initial[0]:.2f}bn",ha='center',color='white')
ax.text(0,initial[0]+deferred[0]/2,f"USD{deferred[0]:.2f}bn",ha='center')
ax.set_ylim(0,49);ax.set_ylabel('USD billion');ax.legend(frameon=False,loc='upper right',fontsize=8)
fig.tight_layout();fig.savefig(out/'funding_timing.png',dpi=180);plt.close(fig)
fig,ax=plt.subplots(figsize=(8,3.1))
prices=list(range(300,901,5));rets=[calculate({'price_base':p})['pref_total_return']*100 for p in prices]
ax.plot(prices,rets,color='#1F3864',linewidth=2);ax.axhline(0,color='#777777',linewidth=.8)
ax.axvline(625,color='#999999',linestyle='--');ax.axvline(b['max_price'],color='#999999',linestyle='--')
ax.set_xlabel('Initial Class A final averaging price illustration (USD)');ax.set_ylabel('Nominal return incl cash dividends (%)')
ax.set_title('Initial terms only. Class C adjustments excluded.',fontsize=10)
fig.tight_layout();fig.savefig(out/'preferred_payoff.png',dpi=180);plt.close(fig)
