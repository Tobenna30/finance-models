"""House-style openpyxl model. Recalculate with python -m vitamin.recalc.

One active forecast selected on Inputs. Cases change drivers, not pasted outputs.
"""
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import CellIsRule
from openpyxl.chart import LineChart, Reference
from openpyxl.utils import get_column_letter as L
from . import assumptions as A

ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'models'/'_raw_Vitamin_Well_Credit.xlsx'
OUT=ROOT/'models'/'Vitamin_Well_Credit.xlsx'
M='#,##0.0;(#,##0.0);"-"'; P='0.0%;(0.0%);"-"'; X='0.00"x"'
NAVY='1F3864'; GREEN='008000'
wb=Workbook(); wb.remove(wb.active)
S={n:wb.create_sheet(n) for n in ['Cover','Inputs','Forecast','Capacity','Recovery','Sensitivity','Sources']}

def put(w,cell,val,fmt=None):
    c=w[cell]; c.value=val
    formula=isinstance(val,str) and val.startswith('=')
    c.font=Font(name='Arial',size=10,color=GREEN if formula and '!' in val else '000000' if formula or isinstance(val,str) else '0000FF')
    if fmt:c.number_format=fmt

def header(w,row,labels):
    for j,label in enumerate(labels,1):
        c=w.cell(row,j,label); c.fill=PatternFill('solid',fgColor=NAVY)
        c.font=Font(name='Arial',size=10,bold=True,color='FFFFFF');c.alignment=Alignment(horizontal='center',vertical='center',wrap_text=True)
    w.row_dimensions[row].height=30

def title(w,text,sub):
    put(w,'A1',text);w['A1'].font=Font(name='Arial',size=14,bold=True,color=NAVY)
    put(w,'A2',sub);w['A2'].font=Font(name='Arial',size=10,italic=True)

for name,w in S.items():
    w.sheet_view.showGridLines=False;w.column_dimensions['A'].width=48
    for col in 'BCDEFGH':w.column_dimensions[col].width=18
    w.freeze_panes='B5';w.sheet_properties.pageSetUpPr.fitToPage=True
    w.page_setup.orientation='landscape';w.page_setup.paperSize=w.PAPERSIZE_A3
    w.page_setup.fitToWidth=1;w.page_setup.fitToHeight=1
    w.sheet_properties.tabColor=NAVY if name=='Cover' else '708AB0' if name=='Inputs' else None

i=S['Inputs']; title(i,'Vitamin Well: underwriting inputs','SEKm unless labelled. S: source/agency forecast. A: assumption. D: derived. No audited borrower accounts.')
put(i,'A4','Case number: 1 Downside, 2 Base, 3 Bull');put(i,'C4',2)
dv=DataValidation(type='whole',operator='between',formula1=1,formula2=3);dv.errorTitle='Choose case 1, 2 or 3';dv.error='Use the case key';dv.showErrorMessage=True;i.add_data_validation(dv);dv.add(i['C4'])
put(i,'A5','Selected case');put(i,'C5','=CHOOSE(C4,"Downside","Base","Bull")')
header(i,8,['Input','Unit','Value','Tag','Source / reason'])
I={}
for row,(key,(label,value,tag,unit,note)) in enumerate(A.INPUTS.items(),9):
    for col,val in zip('ABCDE',[label,unit,value,tag,note]):put(i,f'{col}{row}',val)
    i[f'C{row}'].number_format=P if unit=='%' else X if unit=='x' else '0' if unit=='year' else M
    I[key]=f'Inputs!$C${row}'
i.column_dimensions['A'].width=49;i.column_dimensions['B'].width=14;i.column_dimensions['D'].width=8;i.column_dimensions['E'].width=105
DR={};r=43
for driver,label in [('growth','Revenue growth'),('margin','EBITDA margin'),('rate_shock','Rate shock'),('capex_multiplier','Capex multiplier')]:
    header(i,r,[label,'','',*A.YEARS]); active=r+1
    put(i,f'A{active}','Active '+label.lower());DR[driver]=[]
    for k,(case,c) in enumerate(A.CASES.items(),r+2):
        put(i,f'A{k}',case);put(i,f'B{k}','A')
        for j in range(5):
            x=c[driver][j] if isinstance(c[driver],list) else c[driver]
            put(i,f'{L(4+j)}{k}',x,P if driver!='capex_multiplier' else X)
    for j in range(5):
        col=L(4+j);put(i,f'{col}{active}',f'=CHOOSE($C$4,{col}{r+2},{col}{r+3},{col}{r+4})',P if driver!='capex_multiplier' else X)
        DR[driver].append(f'Inputs!${col}${active}')
    r+=7

c=S['Capacity'];title(c,'Debt capacity under assumed credit policy','Entry capacity only. These are underwriting limits, not contractual covenants.')
header(c,4,['Metric','Value'])
cap=[('Term loan translated to SEKm',f'={I["tlb_eur"]}*{I["fx"]}',M),
     ('Revolver translated to SEKm',f'={I["rcf_eur"]}*{I["fx"]}',M),
     ('2026 adjusted EBITDA forecast midpoint',f'=AVERAGE({I["ebitda_low"]},{I["ebitda_high"]})',M),
     ('Inferred revenue proxy',f'=B7/{I["margin"]}',M),
     ('Cash EBITDA after haircut',f'=B7*(1-{I["cash_haircut"]})',M),
     ('Assumed all-in term-loan rate',f'={I["base_rate"]}+{I["spread"]}',P),
     ('Debt capacity: leverage limit',f'=B9*{I["max_leverage"]}',M),
     ('Debt capacity: cover limit',f'=(B9/{I["min_cover"]}-B6*{I["commit_fee"]})/B10',M),
     ('Capacity: binding policy limit','=MAX(0,MIN(B11:B12))',M),
     ('Requested debt less capacity','=B5-B13',M),
     ('Adjusted EBITDA needed at leverage limit',f'=B5/{I["max_leverage"]}/(1-{I["cash_haircut"]})',M),
     ('EBITDA fall to entry leverage ceiling','=1-B15/B7',P)]
for r,(lab,f,fmt) in enumerate(cap,5):put(c,f'A{r}',lab);put(c,f'B{r}',f,fmt)
c.column_dimensions['A'].width=54

w=S['Forecast'];title(w,'Cash flow and debt forecast','Full-year pro forma proxies; opening-balance interest; no acquisition completion claim.')
put(w,'A3','Case selected');put(w,'B3','=Inputs!C5');header(w,4,['Metric',*A.YEARS])
labels=['Revenue growth','Adjusted EBITDA margin','Opening cash','Opening term loan','Opening revolver','Revenue','Adjusted EBITDA','Cash EBITDA',
        'Interest on opening balances','Undrawn commitment fee','D&A proxy','Cash tax proxy','Capex','Working capital investment','Transaction costs','FCF after interest and tax',
        'Mandatory term-loan amortisation','Cash before discretionary financing','Revolver draw','Revolver repayment','Term-loan cash sweep','Closing term loan',
        'Closing revolver','Closing cash','Gross funded debt','Net funded debt','Cash plus undrawn revolver','Gross leverage / cash EBITDA','Cash interest cover',
        'Headroom to assumed leverage ceiling','Headroom above assumed cover floor','Unfunded cash-minimum gap','Cash rollforward check','Debt rollforward check']
R={label:r for r,label in enumerate(labels,5)}
for lab,row in R.items():put(w,f'A{row}',lab)
for j,year in enumerate(A.YEARS):
    col,prev=L(2+j),L(1+j)
    q=lambda lab:f'{col}{R[lab]}'
    forms={
      'Revenue growth':f'={DR["growth"][j]}','Adjusted EBITDA margin':f'={DR["margin"][j]}',
      'Opening cash':f'={I["opening_cash"]}' if j==0 else f'={prev}{R["Closing cash"]}',
      'Opening term loan':'=Capacity!B5' if j==0 else f'={prev}{R["Closing term loan"]}',
      'Opening revolver':'=0' if j==0 else f'={prev}{R["Closing revolver"]}',
      'Revenue':f'={"Capacity!B8" if j==0 else prev+str(R["Revenue"])}*(1+{q("Revenue growth")})',
      'Adjusted EBITDA':f'={q("Revenue")}*{q("Adjusted EBITDA margin")}',
      'Cash EBITDA':f'={q("Adjusted EBITDA")}*(1-{I["cash_haircut"]})',
      'Interest on opening balances':f'={q("Opening term loan")}*({I["base_rate"]}+{I["spread"]}+{DR["rate_shock"][j]})+{q("Opening revolver")}*({I["base_rate"]}+{I["rcf_spread"]}+{DR["rate_shock"][j]})',
      'Undrawn commitment fee':f'=(Capacity!$B$6-{q("Opening revolver")})*{I["commit_fee"]}',
      'D&A proxy':f'={q("Revenue")}*{I["da"]}',
      'Cash tax proxy':f'=MAX(0,{q("Cash EBITDA")}-{q("D&A proxy")}-{q("Interest on opening balances")}-{q("Undrawn commitment fee")})*{I["tax"]}',
      'Capex':f'={"AVERAGE("+I["capex_low"]+","+I["capex_high"]+")" if j==0 else q("Revenue")+"*"+I["capex_normal"]}*{DR["capex_multiplier"][j]}',
      'Working capital investment':f'=({q("Revenue")}-{"Capacity!$B$8" if j==0 else prev+str(R["Revenue"])})*{I["nwc"]}',
      'Transaction costs':f'={I["transaction_cost"]}' if j==0 else '=0',
      'FCF after interest and tax':f'={q("Cash EBITDA")}-SUM({q("Interest on opening balances")}:{q("Undrawn commitment fee")})-{q("Cash tax proxy")}-SUM({q("Capex")}:{q("Transaction costs")})',
      'Mandatory term-loan amortisation':f'=MIN({q("Opening term loan")},Capacity!$B$5*{I["amort"]})',
      'Cash before discretionary financing':f'={q("Opening cash")}+{q("FCF after interest and tax")}-{q("Mandatory term-loan amortisation")}',
      'Revolver draw':f'=MIN(MAX(0,{I["minimum_cash"]}-{q("Cash before discretionary financing")}),Capacity!$B$6-{q("Opening revolver")})',
      'Revolver repayment':f'=MIN(MAX(0,{q("Cash before discretionary financing")}-{I["minimum_cash"]}),{q("Opening revolver")})',
      'Term-loan cash sweep':f'=MIN(MAX(0,{q("Cash before discretionary financing")}-{q("Revolver repayment")}-{I["minimum_cash"]})*{I["sweep"]},{q("Opening term loan")}-{q("Mandatory term-loan amortisation")})',
      'Closing term loan':f'={q("Opening term loan")}-{q("Mandatory term-loan amortisation")}-{q("Term-loan cash sweep")}',
      'Closing revolver':f'={q("Opening revolver")}+{q("Revolver draw")}-{q("Revolver repayment")}',
      'Closing cash':f'={q("Cash before discretionary financing")}+{q("Revolver draw")}-{q("Revolver repayment")}-{q("Term-loan cash sweep")}',
      'Gross funded debt':f'={q("Closing term loan")}+{q("Closing revolver")}',
      'Net funded debt':f'={q("Gross funded debt")}-{q("Closing cash")}',
      'Cash plus undrawn revolver':f'={q("Closing cash")}+Capacity!$B$6-{q("Closing revolver")}',
      'Gross leverage / cash EBITDA':f'={q("Gross funded debt")}/{q("Cash EBITDA")}',
      'Cash interest cover':f'={q("Cash EBITDA")}/SUM({q("Interest on opening balances")}:{q("Undrawn commitment fee")})',
      'Headroom to assumed leverage ceiling':f'={I["max_leverage"]}-{q("Gross leverage / cash EBITDA")}',
      'Headroom above assumed cover floor':f'={q("Cash interest cover")}-{I["min_cover"]}',
      'Unfunded cash-minimum gap':f'=MAX(0,{I["minimum_cash"]}-{q("Closing cash")})',
      'Cash rollforward check':f'={q("Closing cash")}-{q("Opening cash")}-{q("FCF after interest and tax")}+{q("Mandatory term-loan amortisation")}-{q("Revolver draw")}+{q("Revolver repayment")}+{q("Term-loan cash sweep")}',
      'Debt rollforward check':f'={q("Gross funded debt")}-{q("Opening term loan")}-{q("Opening revolver")}+{q("Mandatory term-loan amortisation")}+{q("Term-loan cash sweep")}-{q("Revolver draw")}+{q("Revolver repayment")}',
    }
    for lab,f in forms.items():put(w,q(lab),f,P if lab in labels[:2] else X if lab in labels[27:31] else M)
for r in [34,35]:w.conditional_formatting.add(f'B{r}:F{r}',CellIsRule(operator='lessThan',formula=['0'],fill=PatternFill('solid',fgColor='FCE4D6')))
w.conditional_formatting.add('B36:F36',CellIsRule(operator='greaterThan',formula=['0'],fill=PatternFill('solid',fgColor='FCE4D6')))
chart=LineChart();chart.title='Gross leverage / cash EBITDA';chart.add_data(Reference(w,min_col=2,max_col=6,min_row=32,max_row=32),from_rows=True);chart.set_categories(Reference(w,min_col=2,max_col=6,min_row=4,max_row=4));chart.width=19;chart.height=8;w.add_chart(chart,'A41')

r=S['Recovery'];title(r,'Default recovery waterfall','Assumed pari passu first lien; no legal opinion. No unrestricted cash credited at default.')
header(r,4,['Metric','Value'])
rec=[('Default cash EBITDA',f'=Capacity!B9*(1-{I["recovery_haircut"]})',M),('Default enterprise value',f'=B5*{I["recovery_multiple"]}',M),
     ('Enforcement cost reserve',f'=B6*{I["recovery_cost"]}',M),('Other priority claims',f'={I["priority_claims"]}',M),
     ('Available first-lien pool','=MAX(0,B6-B7-B8)',M),('Term-loan claim','=Capacity!B5',M),
     ('Revolver claim at default',f'=Capacity!B6*{I["recovery_rcf_draw"]}',M),('Total pari passu claims','=SUM(B10:B11)',M),
     ('First-lien recovery','=MIN(1,B9/B12)',P),('Term-loan proceeds','=B10*B13',M),('Revolver proceeds','=B11*B13',M),
     ('Unrecovered first-lien claim','=B12-SUM(B14:B15)',M),('Residual equity','=MAX(0,B9-B12)',M)]
for row,(lab,f,fmt) in enumerate(rec,5):put(r,f'A{row}',lab);put(r,f'B{row}',f,fmt)

s=S['Sensitivity'];title(s,'Recovery and debt-capacity sensitivities','Direct scalar calculations; fixed current policy and default assumptions. No duplicated cash-flow model.')
header(s,4,['Recovery: EBITDA haircut / EV multiple',4,5,6,7,8])
for row,h in enumerate([.15,.25,.35,.45,.55],5):
    put(s,f'A{row}',h,P)
    for col in range(2,7):
        x=L(col);put(s,f'{x}{row}',f'=MIN(1,MAX(0,Capacity!$B$9*(1-$A{row})*{x}$4*(1-{I["recovery_cost"]})-{I["priority_claims"]})/Recovery!$B$12)',P)
header(s,13,['Debt capacity: EBITDA / all-in rate',.05,.07,.09,.11,.13])
for col in range(2,7):s.cell(13,col).number_format=P
for row,factor in enumerate([.70,.85,1.0,1.15,1.30],14):
    put(s,f'A{row}',f'=Capacity!$B$7*{factor}',M)
    for col in range(2,7):
        x=L(col);put(s,f'{x}{row}',f'=MAX(0,MIN($A{row}*(1-{I["cash_haircut"]})*{I["max_leverage"]},($A{row}*(1-{I["cash_haircut"]})/{I["min_cover"]}-Capacity!$B$6*{I["commit_fee"]})/{x}$13))',M)

o=S['Cover'];title(o,'Vitamin Well / Vital Bidco credit review','27 October 2026. Public-information model of the 2026 refinancing; no verified contractual covenant test.')
put(o,'A3','Case selected');put(o,'B3','=Inputs!C5');header(o,5,['Metric','Value'])
out=[('Term loan, EURm equivalent','=Inputs!'+I['tlb_eur'].split('!')[1],M),('Term loan translated, SEKm','=Capacity!B5',M),
     ('Capacity under assumed policy, SEKm','=Capacity!B13',M),('Requested less capacity, SEKm','=Capacity!B14',M),
     ('2026 gross leverage / cash EBITDA','=Forecast!B32',X),('2026 cash interest cover','=Forecast!B33',X),
     ('2026 FCF, SEKm','=Forecast!B20',M),('Peak revolver, SEKm','=MAX(Forecast!B27:F27)',M),
     ('Minimum cash plus undrawn RCF, SEKm','=MIN(Forecast!B31:F31)',M),('Peak unfunded cash gap, SEKm','=MAX(Forecast!B36:F36)',M),
     ('2030 gross leverage / cash EBITDA','=Forecast!F32',X),('Default first-lien recovery','=Recovery!B13',P),
     ('Actual contractual covenant compliance','Not established: loan agreement missing',None),
     ('Selected-case policy screen','=IF(OR(Capacity!B14>0,MAX(Forecast!B36:F36)>0,MIN(Forecast!B34:F34)<0,MIN(Forecast!B35:F35)<0),"REJECT at assumed policy limits","PASS policy screen; evidence still required")',None)]
for row,(lab,f,fmt) in enumerate(out,6):put(o,f'A{row}',lab);put(o,f'B{row}',f,fmt);o[f'B{row}'].font=Font(name='Arial',size=10)
put(o,'A20','Recorded credit-memo verdict');put(o,'B20','Reject pending downside protection and evidence')
o.column_dimensions['A'].width=53;o.column_dimensions['B'].width=56;o.freeze_panes=None
put(o,'A22','No purchase-price or sources-and-uses bridge: transaction consideration is undisclosed.')
put(o,'A23','No audited full balance sheet: cash and debt rollforwards reconcile separately.')
put(o,'A24','2026 is a full-year pro forma proxy, not remaining cash flow after the review date.')

z=S['Sources'];title(z,'Sources and evidence boundaries','Agency forecasts are not audited borrower financials. Accessed 27 October 2026.')
header(z,4,['Key','Document / section','URL'])
for row,(key,(label,url)) in enumerate(A.SOURCES.items(),5):
    put(z,f'A{row}',key);put(z,f'B{row}',label);put(z,f'C{row}',url)
z.column_dimensions['A'].width=15;z.column_dimensions['B'].width=125;z.column_dimensions['C'].width=115
put(z,'A11','Missing: final agreement, audited group accounts, closing cash/debt bridge, security and ranking, pricing, covenants.')
if __name__=='__main__':
    RAW.parent.mkdir(exist_ok=True);wb.save(RAW);print('saved',RAW)
