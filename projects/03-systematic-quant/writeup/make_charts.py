from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'momentum'))
import engine as E
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
p=Path(__file__).parent;d=E.panel();dates=__import__('pandas').to_datetime(d.index)
fig,ax=plt.subplots(2,1,figsize=(9,4.5),sharex=True,gridspec_kw={'height_ratios':[2,1]})
ax[0].plot(dates,(1+d.gross).cumprod(),label='Gross, 100% gross exposure',color='#17365D');ax[0].plot(dates,d.wealth,label='Net assumed costs',color='#B66B19');ax[0].set_yscale('log');ax[0].set_ylabel('Excess-P&L index, log');ax[0].legend(fontsize=8);ax[0].axvline(__import__('pandas').Timestamp('2000-01-01'),color='grey',ls='--',lw=.8)
ax[1].fill_between(dates,d.drawdown*100,0,color='#B66B19',alpha=.5);ax[1].set_ylabel('Net drawdown %')
for a in ax:a.spines[['top','right']].set_visible(False);a.grid(axis='y',alpha=.2)
fig.tight_layout();fig.savefig(p/'momentum_drawdown.png',dpi=140);plt.close(fig)
