from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'policy'))
import engine as E
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
r=E.results();p=Path(__file__).parent
fig,axs=plt.subplots(1,2,figsize=(10,3.3))
d=E.curves();axs[0].plot(d.index,(d.gilt_spot_10-d.gilt_spot_2)*100,color='#17365D');axs[0].set_xticks([d.index[i] for i in range(0,len(d),350)]);axs[0].tick_params(axis='x',rotation=30);axs[0].set_title('Fitted gilt 2s10s (bp)');axs[0].axhline(0,color='grey',lw=.6)
m=r['meetings'];axs[1].plot([x['date'] for x in m],[x['market'] for x in m],label='OIS-implied + basis');axs[1].axhline(E.A.SCENARIO_END,color='#B66B19',label='Hold scenario');axs[1].set_title('Meeting-interval Bank Rate proxy (%)');axs[1].tick_params(axis='x',rotation=45);axs[1].legend(fontsize=8)
for ax in axs:ax.spines[['top','right']].set_visible(False);ax.grid(axis='y',alpha=.2)
fig.tight_layout();fig.savefig(p/'rates_policy.png',dpi=140);plt.close(fig)
