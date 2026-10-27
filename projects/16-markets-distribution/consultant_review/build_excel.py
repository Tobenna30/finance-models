from pathlib import Path
import json
from .assumptions import PERIODS,FUND,BENCHMARK,SECTORS,REQUESTS,SOURCE
from .engine import calculate
from .excel_style import workbook
ROOT=Path(__file__).resolve().parents[1]
def build():
    performance=[['Performance: Class I vs benchmark','Fund %','Benchmark %','Arithmetic excess bp']]
    for r in range(2,8):performance.append([f'=Inputs!A{r}',f'=Inputs!B{r}',f'=Inputs!C{r}',f'=(B{r}-C{r})*100'])
    performance += [['Convention','3m/YTD cumulative; 1y and longer annualised. Excess is arithmetic difference, not geometric or risk-adjusted alpha'],['Use','Do not blend these horizons or infer return contributions from sector weights']]
    sectors=[['Sector','Fund %','Benchmark %','Active percentage points']]
    for r in range(2,7):sectors.append([f'=Inputs!E{r}',f'=Inputs!F{r}',f'=Inputs!G{r}',f'=B{r}-C{r}'])
    sectors += [['Total','=SUM(B2:B6)','=SUM(C2:C6)','=SUM(D2:D6)'],['Benchmark rounding residual','=100-C7'],['Caution','Exposure differences are not measured return attribution. Benchmark source sums99.9%; residual0.1pp is not allocated']]
    inputs=[['Inputs: 30 June 2026 Class I','Fund return %','Benchmark return %',None,'Sector','Fund weight %','Benchmark weight %']]
    for i in range(6):
      inputs.append([PERIODS[i],FUND[i],BENCHMARK[i],None,*SECTORS[i]] if i<5 else [PERIODS[i],FUND[i],BENCHMARK[i]])
    requests=[['ID','Consultant question','Status','Evidence / gap','Suggested role owner','Due day, illustrative']]+[[*x,5] for x in REQUESTS]
    w=workbook({
      'Cover':[['Institutional client review: independent case'],['Anchor','Hypothetical UK pension; US fund used only as a public research proxy'],['Call','ESCALATE for further due diligence; no mandate approval'],['Quarter excess, bp','=Performance!D2'],['1-year excess, bp','=Performance!D4'],['Open requests','=COUNTIF(Requests!C2:C9,"Open")'],['Total sample requests','=COUNTA(Requests!A2:A9)'],['Scope','As of30 June2026. No real client meetings, requests or replies are implied'],['Gate','Do not use US fund results as a GBP-hedged institutional mandate record']],
      'Performance':performance,'Exposure':sectors,'Requests':requests,'Inputs':inputs,
      'Sources':[['Sources','Document','Page/date'],['Factsheet',json.loads((ROOT/'data/sources.json').read_text())['factsheet']['url'],'p1 returns; p2 sectors, 30 Jun 2026'],['Commentary',json.loads((ROOT/'data/sources.json').read_text())['commentary']['url'],'p1 return cross-check, p2 qualitative attribution'],['Basis','USD US fund Class I vs Bloomberg Global Aggregate, not a strategy composite','Same end date'],['Assumptions','Sample questions, owner roles and five-day target are illustrative workflow fields','No live requests'],['Cash benchmark','Dash interpreted as0 in displayed sector table, source benchmark total99.9 with0.1pp rounding residual','Explicit interpretation']]})
    for sh in ['Performance','Exposure']:
     for row in w[sh].iter_rows(min_row=2,max_row=7):
      for c in row[1:]:c.number_format='0.00;[Red](0.00);"-"'
    w['Exposure']['B8'].number_format='0.00'
    w.save(ROOT/'models/Consultant_Review.xlsx');(ROOT/'outputs/results.json').write_text(json.dumps(calculate(),indent=2));return ROOT/'models/Consultant_Review.xlsx'
if __name__=='__main__':print(build())
