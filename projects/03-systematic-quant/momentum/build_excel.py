"""Live monthly dollar-neutral portfolio arithmetic from sourced decile returns."""
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font,PatternFill,Alignment
from openpyxl.utils import get_column_letter
import assumptions as A
import engine as E
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'models/Momentum_Factor_Backtest.xlsx';RAW=OUT.with_name('_raw_'+OUT.name)
def build():
 d=E.panel();r=E.results();w=Workbook();w.remove(w.active)
 for n in ['Cover','Inputs','Backtest','Performance','Walk forward','Sensitivity','Drawdowns','Data','Sources']:w.create_sheet(n)
 s=w['Inputs'];s.append(['Driver','Value','S/A/D / interpretation'])
 for row in [('Absolute weight per leg',A.LEG_WEIGHT,'A: 50% long winners, 50% short losers'),('Execution bp per traded notional',A.COST_BP,'A: buys and sells charged'),('One-way monthly turnover per leg',A.ONE_WAY_TURNOVER,'A: 50% replacement; not measured'),('Annual borrow rate',A.BORROW_ANNUAL,'A: charged on short weight'),('Annualisation months',12,'A'),('Design end',A.TRAIN_END,'A: fixed split'),('Evaluation start',A.TEST_START,'D: next month'),('Source end',A.END,'S: 202609 CRSP release')]:s.append(row)
 s.append(['Gross / net exposure','=2*B2','=B2-B2']);s.append(['Traded notional per NAV','=4*B2*B4','D: buys plus sells, both legs'])
 s=w['Data'];s.append(['Month']+['Decile '+str(i) for i in range(1,11)]+['Published Mom'])
 for month,v in d.iterrows():s.append([month]+[float(v['decile'+str(i)]) for i in range(1,11)]+[float(v.mom)])
 s=w['Backtest'];s.append(['Month','Winner','Loser','Gross excess','Execution cost','Borrow cost','Net excess','P&L index','High water','Drawdown','Published Mom'])
 for i in range(2,len(d)+2):
  s.append([f'=Data!A{i}',f'=Data!K{i}',f'=Data!B{i}',f'=(B{i}-C{i})*Inputs!B2','=4*Inputs!B2*Inputs!B4*Inputs!B3/10000','=Inputs!B2*Inputs!B5/Inputs!B6',f'=D{i}-E{i}-F{i}',f'=(1+G{i})'+('' if i==2 else f'*H{i-1}'),f'=MAX(1,H$2:H{i})',f'=H{i}/I{i}-1',f'=Data!L{i}'])
 n=len(d)+1;split=2+len(d.loc[:A.TRAIN_END]);s=w['Performance'];s.append(['Sample','N months','Net Sharpe','Annual net mean','Annual net vol','Net CAGR','Execution drag','Borrow drag','Gross vs Mom corr','Worst monthly DD'])
 for i,(name,first,last) in enumerate([('Design',2,split-1),('Evaluation',split,n),('Full',2,n)],2):
  x=f"Backtest!G{first}:G{last}";g=f"Backtest!D{first}:D{last}";m=f"Backtest!K{first}:K{last}"
  end=f'Backtest!H{last}';start='1' if first==2 else f'Backtest!H{first-1}'
  # Drawdown column is full-history DD, labelled accordingly, not reset by sample.
  s.append([name,last-first+1,f'=AVERAGE({x})/STDEV({x})*SQRT(Inputs!B6)',f'=AVERAGE({x})*Inputs!B6',f'=STDEV({x})*SQRT(Inputs!B6)',f'=({end}/{start})^(Inputs!B6/B{i})-1',f'=AVERAGE(Backtest!E{first}:E{last})*Inputs!B6',f'=AVERAGE(Backtest!F{first}:F{last})*Inputs!B6',f'=CORREL({g},{m})',f'=MIN(Backtest!J{first}:J{last})'])
 s=w['Walk forward'];s.append(['Year','Training end','Train months','Train Sharpe','Train ann vol','Test months','Test return','Test ann vol'])
 for wf in r['walk_forward']:
  year=str(wf['year']);first=2+list(d.index).index(year+'-01');last=first+wf['test_months']-1;trainlast=first-1;i=s.max_row+1
  s.append([wf['year'],wf['train_end'],first-2,f'=AVERAGE(Backtest!G2:G{trainlast})/STDEV(Backtest!G2:G{trainlast})*SQRT(Inputs!B6)',f'=STDEV(Backtest!G2:G{trainlast})*SQRT(Inputs!B6)',last-first+1,f'=Backtest!H{last}/Backtest!H{first-1}-1',f'=STDEV(Backtest!G{first}:G{last})*SQRT(Inputs!B6)'])
 s=w['Sensitivity'];s.append(['Turnover one-way A','Execution bp A','Monthly all-in drag','OOS net Sharpe','Annual all-in drag'])
 for v in r['cost_sensitivity']:
  i=s.max_row+1;s.append([v['turnover'],v['cost_bp'],f'=4*Inputs!B2*A{i}*B{i}/10000+Inputs!B2*Inputs!B5/Inputs!B6',f'=(AVERAGE(Backtest!D{split}:D{n})-C{i})/STDEV(Backtest!D{split}:D{n})*SQRT(Inputs!B6)',f'=C{i}*Inputs!B6'])
 s.append(['Base-turnover execution break-even bp',f'=(AVERAGE(Backtest!D{split}:D{n})-Inputs!B2*Inputs!B5/12)/(4*Inputs!B2*Inputs!B4)*10000'])
 s=w['Drawdowns'];s.append(['Peak','Trough','Recovery','Net drawdown D'])
 for v in r['drawdown_episodes']:s.append([v['peak'],v['trough'],v['recovery'] or 'Not recovered by '+A.END,v['drawdown']])
 s.append(['Worst calendar years','Net return D','Months'])
 for v in r['worst_years']:s.append([v['year'],v['net_return'],v['months']])
 s.append(['Episodes are fixed Python research output. Rerun engine if changing costs; live full-history minimum is Performance!J4.'])
 s=w['Cover'];s.append(['US 12–1 momentum','28 October 2026 / data through September'])
 for row in [('Verdict','Reject standalone strategy under base costs'),('Design net Sharpe','=Performance!C2'),('Evaluation net Sharpe','=Performance!C3'),('Annual execution + borrow','=Performance!G4+Performance!H4'),('Full-history monthly drawdown','=Performance!J4'),('Gross return correlation to Mom','=Performance!I4'),('Data scope','Published monthly historical-universe deciles; no independent stock-level signals'),('Turnover','50% per leg assumed, not observed'),('Test scope','Historical split and expanding annual review; not a prospective preregistered test')]:s.append(row)
 s=w['Sources'];s.append(['Source / method','URL / limitation'])
 for k,v in A.SOURCES.items():s.append([k,v])
 for row in [('Frozen files','momentum/data/*.zip and manifest.json retain hashes; first value-weight monthly table only'),('Signal S','Prior months -12 to -2, excluding latest month. NYSE deciles; NYSE/AMEX/NASDAQ eligible stocks.'),('Universe limit','Historical CRSP-based aggregates, not current-survivor ticker selection. Constituents and delisting handling not independently audited.'),('Vintage limit','202609 revised history, not archival point-in-time releases. CIZ/FIZ methodology change from 2025.'),('Costs A','Execution 10bp on bought/sold notional, 50% turnover each leg; 2% annual borrow on 50% short.'),('Return D','Monthly +0.5 winner -0.5 loser minus costs; excess over cash. Dollar-neutral at monthly rebalance; beta may vary.'),('Validation limit','French Mom uses related underlying CRSP data and is not an independent validation set.'),('Daily data limit','No stock-level daily/delisted price files. Daily French momentum deciles are formed daily and are not substituted for monthly portfolios.')]:s.append(row)
 for s in w:
  s.freeze_panes='B2';s.sheet_view.showGridLines=False;s.auto_filter.ref=s.dimensions
  for c in s[1]:c.fill=PatternFill('solid',fgColor='17365D');c.font=Font(name='Arial',size=11,color='FFFFFF',bold=True);c.alignment=Alignment(wrap_text=True)
  s.row_dimensions[1].height=34
  for row in s.iter_rows(min_row=2):
   for c in row:
    c.font=Font(name='Arial',size=10,color='008000' if c.data_type=='f' else '0000FF' if isinstance(c.value,(int,float)) else '222222');c.alignment=Alignment(wrap_text=True,vertical='top')
    if isinstance(c.value,(int,float)) or c.data_type=='f':c.number_format='0.000;[Red](0.000);"—"'
    if c.row%2==0:c.fill=PatternFill('solid',fgColor='EFF3F8')
   s.row_dimensions[row[0].row].height=30
  for j in range(1,s.max_column+1):s.column_dimensions[get_column_letter(j)].width=30 if j==1 else 23
  if s.title in ['Cover','Sources']:s.column_dimensions['B'].width=100
 # Decimal financial return columns receive percent formatting; Sharpe/correlation stay ratios.
 for sn,cols in [('Data',range(2,13)),('Backtest',[2,3,4,5,6,7,10,11]),('Performance',[4,5,6,7,8,10]),('Walk forward',[5,7,8]),('Sensitivity',[1,3,5])]:
  for j in cols:
   for row in w[sn].iter_rows(min_row=2,min_col=j,max_col=j):row[0].number_format='0.00%;[Red](0.00%);"—"'
 for cell in ['B5','B6']:w['Cover'][cell].number_format='0.00%;[Red](0.00%)'
 for c in ['B2','B4','B5']:w['Inputs'][c].number_format='0.0%'
 w['Inputs'].column_dimensions['C'].width=70
 for i in range(2,7):w['Drawdowns'].cell(i,4).number_format='0.00%;[Red](0.00%)'
 for i in range(8,13):
  w['Drawdowns'].cell(i,2).number_format='0.00%;[Red](0.00%)'
  w['Drawdowns'].cell(i,3).number_format='0'
 for i in range(2,5):w['Performance'].cell(i,2).number_format='0'
 for i in range(2,w['Walk forward'].max_row+1):
  for j in [1,3,6]:w['Walk forward'].cell(i,j).number_format='0'
 w.save(RAW);print(RAW)
if __name__=='__main__':build()
