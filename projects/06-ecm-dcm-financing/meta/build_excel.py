"""Live openpyxl workbook under AGENTS.md, with LibreOffice cache step."""
import csv
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font,PatternFill,Alignment
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import CellIsRule
from .assumptions import ROOT,INPUTS,SOURCES,CLOSE,SETTLE,CONVERT,DIVIDEND_DATES,PRICE_GRID,YIELD_GRID

RAW=ROOT/'models'/'Meta_ECM_DCM_raw.xlsx'
OUT=ROOT/'models'/'Meta_ECM_DCM.xlsx'
I={k:r for r,k in enumerate(INPUTS,6)}
DATE_ROW=len(INPUTS)+8
ACTIVE=DATE_ROW+4
NUM='#,##0.0;(#,##0.0);"-"'
PCT='0.0%;(0.0%);"-"'
def inp(k):return f'Inputs!$D${I[k]}'
def datecell(i):return f'Inputs!$D${DATE_ROW+i}'

def main():
    w=Workbook();w.remove(w.active)
    for name in ('Cover','Inputs','Funding','Alternatives','Conversion','Bond','Position','Sources'):
        s=w.create_sheet(name);s.sheet_view.showGridLines=False
        for c,width in {'A':2,'B':2,'C':55,'D':19,'E':19,'F':19,'G':19,'H':19,'I':19}.items():s.column_dimensions[c].width=width
        s['C2']='Meta AI financing' if name=='Cover' else name;s['C2'].font=Font(name='Arial',size=16,bold=True,color='1F3864')
        s.merge_cells('C3:I3');s['C3']='27 Oct 2026 priced terms. USDm / million securities. Offerings not yet closed.'
        s['C3'].font=Font(name='Arial',size=10,italic=True)
        s.freeze_panes='D6' if name!='Cover' else None
        s.sheet_properties.pageSetUpPr.fitToPage=True;s.page_setup.orientation='landscape';s.page_setup.paperSize=s.PAPERSIZE_A3;s.page_setup.fitToWidth=1;s.page_setup.fitToHeight=0
    def header(s,r,labels):
        for c,v in enumerate(labels,3):
            s.cell(r,c,v);s.cell(r,c).fill=PatternFill('solid',fgColor='1F3864');s.cell(r,c).font=Font(name='Arial',size=10,bold=True,color='FFFFFF')
    def put(s,r,label,vals,fmt=NUM):
        s.cell(r,3,label)
        for c,v in enumerate(vals,4):s.cell(r,c,v);s.cell(r,c).number_format=fmt
    def note(s,r,text):
        s.merge_cells(start_row=r,start_column=3,end_row=r,end_column=9);s.cell(r,3,text);s.cell(r,3).alignment=Alignment(wrap_text=True,vertical='center');s.row_dimensions[r].height=max(30,14*(len(text)//140+1))
    s=w['Inputs'];header(s,5,['Input','Value','Units','Tag','Source / reasoning'])
    s.column_dimensions['G'].width=88
    for key,(label,v,tag,unit,why) in INPUTS.items():
        r=I[key];put(s,r,label,[v],PCT if unit=='%' else '0.0000' if key in ('min_rate','max_rate') else NUM);s.cell(r,5,unit);s.cell(r,6,tag);s.cell(r,7,why)
        s.cell(r,4).fill=PatternFill('solid',fgColor='FFF2CC');s.cell(r,7).alignment=Alignment(wrap_text=True);s.row_dimensions[r].height=30
    for n,(label,d) in enumerate((('Expected offer close',CLOSE),('Forward settlement deadline, assumed use',SETTLE),('Mandatory preferred conversion',CONVERT))):
        put(s,DATE_ROW+n,label,[datetime.combine(d,datetime.min.time())],'d-mmm-yyyy')
    put(s,ACTIVE,'Active initial Class A reference price',[f'=CHOOSE({inp("case")},{inp("price_down")},{inp("price_base")},{inp("price_up")})'])
    put(s,ACTIVE+1,'Case selected',[f'=CHOOSE({inp("case")},"Down","Base","Up")'])
    dv=DataValidation(type='whole',operator='between',formula1=1,formula2=3);dv.showErrorMessage=True;dv.errorStyle='stop';s.add_data_validation(dv);dv.add(s.cell(I['case'],4))
    maturity=DataValidation(type='whole',operator='equal',formula1=5);maturity.showErrorMessage=True;maturity.errorStyle='stop';s.add_data_validation(maturity);maturity.add(s.cell(I['bond_term'],4))
    for name in ('Cover','Funding','Alternatives','Conversion','Bond','Position'):
        w[name]['H2']='Case selected';w[name]['I2']=f'=Inputs!D{ACTIVE+1}'
    s=w['Funding'];header(s,5,['Priced package and cash timing','USDm'])
    rows={
     6:('Preferred gross proceeds',f'={inp("deposits")}*{inp("deposit_price")}'),
     7:('Preferred issuance cost proxy',f'=D6*{inp("pref_fee")}'),
     8:('Expected preferred net cash at close','=D6-D7'),
     9:('Common forward gross public offering',f'={inp("common_shares")}*{inp("offer_price")}'),
     10:('Gross priced package','=D6+D9'),
     11:('Initial common net forward proceeds',f'={inp("common_shares")}*{inp("forward_price")}'),
     12:('Forward price adjustment stress',f'=D11*{inp("forward_change")}'),
     13:('Forward extra expense proxy',f'={inp("forward_expense")}'),
     14:('Deferred net proceeds','=D11+D12-D13'),
     15:('Total eventual net proceeds','=D8+D14'),
     16:('Cash available at expected offering close','=D8'),
     17:('Share of net proceeds deferred','=D14/D15'),
     18:('Excluded conditional ATM capacity',f'={inp("atm")}'),
     19:('Annual preferred dividends',f'=Conversion!D6*{inp("liquidation")}*{inp("dividend")}'),
     20:('Bridge interest to latest settlement',f'=D14*{inp("bridge_rate")}*({datecell(1)}-{datecell(0)})/365'),
     21:('Bridge fee overlay',f'=D14*{inp("bridge_fee")}'),
     22:('Bridge total after assumed tax shield',f'=SUM(D20:D21)*(1-{inp("tax")})'),
     24:('Historical nine-month free cash flow',f'={inp("ocf9")}-{inp("ppe9")}-{inp("lease9")}'),
     25:('Reported liquid resources, 30 Sep',f'={inp("cash")}+{inp("securities")}'),
     26:('Q4 spend implied by capex guidance, low',f'={inp("capex_low")}-{inp("ppe9")}-{inp("lease9")}'),
     27:('Q4 spend implied by capex guidance, high',f'={inp("capex_high")}-{inp("ppe9")}-{inp("lease9")}'),
    }
    for r,(label,f) in rows.items():put(s,r,label,[f],PCT if r==17 else NUM)
    note(s,30,'Preferred net proceeds use unverified issuance costs. Common proceeds assume physical settlement at the deadline and a zero base price adjustment; contractual carry, dividends, stock borrow and alternative settlement may change the result.')
    note(s,32,'Bridge overlay assumes all eventual proceeds are needed at close. It is not a verified loan or Meta funding requirement. Interest and fees are additional cash uses. No ATM cash, options, operating cash flow or prior cash is added to issuance proceeds.')
    note(s,34,'Historical liquidity includes securities. Free cash flow is nine-month operating cash less capex and finance-lease principal. Q4 capex range is implied spend, not a funding shortfall or forecast cash burn.')
    s=w['Alternatives'];header(s,5,['Same eventual net funding','Priced package','Immediate common','Straight debt'])
    for r,label in {6:'Net cash at close',7:'Deferred net cash',8:'Total net proceeds',9:'Gap if all proceeds needed at close',10:'Annual after-tax financing cash charge',11:'New common at initial forward settlement',12:'New common at preferred conversion (initial terms)',13:'Bond face amount',14:'Bond bullet maturity principal',15:'Issue-only balance-sheet check'}.items():s.cell(r,3,label)
    formulas={
    'D6':'=Funding!D8','E6':'=Funding!D15','F6':'=Funding!D15','D7':'=Funding!D14','E7':'=0','F7':'=0',
    'D8':'=SUM(D6:D7)','E8':'=SUM(E6:E7)','F8':'=SUM(F6:F7)','D9':'=D8-D6','E9':'=E8-E6','F9':'=F8-F6',
    'D10':'=Funding!D19','E10':'=0','F10':f'=Bond!D7*(1-{inp("tax")})',
    'D11':f'={inp("common_shares")}','E11':f'=E6/(1-{inp("equity_fee")} )/{inp("offer_price")}','F11':'=0',
    'D12':'=Conversion!D10','E12':'=0','F12':'=0','D13':'=0','E13':'=0','F13':'=Bond!D6',
    'D14':'=0','E14':'=0','F14':'=Bond!D6',
    'D15':'=Position!D11','E15':'=Position!F11','F15':'=Position!G11'}
    for cell,f in formulas.items():s[cell]=f;s[cell].number_format=NUM
    note(s,18,'Annual charge compares preferred cash dividends (no tax deduction) with bond coupons after an assumed 21% tax shield. It excludes common dividends and equity opportunity cost, and does not establish the cheapest source of capital.')
    note(s,20,'Mixed package shares are an initial Class A reference illustration, not actual 2029 dilution after Class C. All alternatives exclude over-allotments. Straight debt has a five-year bullet and new interest costs; cash charges are not GAAP EPS.')
    s=w['Conversion'];header(s,5,['Initial Class A mechanics only','Value'])
    rows={6:('Preferred shares, not depositary shares',f'={inp("deposits")}/{inp("deposits_per_pref")}'),7:('Lower conversion price',f'={inp("liquidation")}/{inp("max_rate")}'),8:('Upper conversion price',f'={inp("liquidation")}/{inp("min_rate")}'),9:('Active conversion rate',f'=ROUND(MAX({inp("min_rate")},MIN({inp("max_rate")},{inp("liquidation")}/Inputs!D{ACTIVE})),4)'),10:('Shares delivered, initial terms','=D6*D9'),11:('Converted market value',f'=D10*Inputs!D{ACTIVE}'),12:('Illustrative total cash dividends','=SUM(E20:E30)'),13:('Investor total nominal return','=(D11+D12)/Funding!D6-1')}
    for r,(label,f) in rows.items():put(s,r,label,[f],PCT if r==13 else '0.0000' if r==9 else NUM)
    note(s,15,'Class C transition and anti-dilution adjustments may change conversion securities, prices and rates. This schedule deliberately illustrates initial terms only. It is not a forecast of actual economic or voting dilution.')
    header(s,19,['Illustrative dividend date','30/360 years','Dividend USDm','Dividend PV'])
    for r,d in enumerate(DIVIDEND_DATES,20):
        s.cell(r,3,datetime.combine(d,datetime.min.time()));s.cell(r,3).number_format='d-mmm-yyyy'
        previous=datecell(0) if r==20 else f'C{r-1}'
        s.cell(r,4,f'=(360*(YEAR(C{r})-YEAR({previous}))+30*(MONTH(C{r})-MONTH({previous}))+MIN(DAY(C{r}),30)-MIN(DAY({previous}),30))/360').number_format='0.0000'
        s.cell(r,5,f'=$D$6*{inp("liquidation")}*{inp("dividend")}*D{r}').number_format=NUM
        s.cell(r,6,f'=E{r}/(1+{inp("investor_hurdle")})^((C{r}-{datecell(0)})/365)').number_format=NUM
    note(s,32,'All dividends assumed declared and paid in cash. Analyst 30/360 approximation includes first stub; verify final prospectus day count. No share-paid dividends, arrears or early/fundamental-change conversion.')
    header(s,35,['Price reference','Conversion rate','New shares','Capital value','Return incl dividends'])
    for r,p in enumerate(PRICE_GRID,36):
        put(s,r,p,[f'=ROUND(MAX({inp("min_rate")},MIN({inp("max_rate")},{inp("liquidation")}/C{r})),4)',f'=$D$6*D{r}',f'=E{r}*C{r}',f'=(F{r}+$D$12)/Funding!$D$6-1']);s.cell(r,3).number_format=NUM;s.cell(r,7).number_format=PCT
        s.cell(r,4).number_format='0.0000';s.cell(r,5).number_format='0.000'
    s['D10'].number_format='0.000'
    put(s,45,'PV of assumed cash dividends',['=SUM(F20:F30)'])
    put(s,46,'Required terminal value at investor hurdle',[f'=(Funding!D6-D45)*(1+{inp("investor_hurdle")})^(({datecell(2)}-{datecell(0)})/365)'])
    put(s,47,'Initial Class A price meeting investor hurdle',[f'=D46/($D$6*IF(D46>$D$6*{inp("liquidation")},{inp("min_rate")},{inp("max_rate")}))'])
    note(s,49,'Deterministic price at the selected return hurdle; not an option valuation, market forecast or actual Class C price. Cash dividends assumed certain for this illustration. Conversion-rate rounding creates small boundary differences.')
    s=w['Bond'];header(s,5,['Hypothetical five-year debt','Value'])
    rows={6:('Face needed for matched net proceeds',f'=Funding!D15/(1-{inp("bond_fee")})'),7:('Annual coupon cash',f'=D6*{inp("bond_coupon")}'),8:('Effective yield including issuance costs',f'=RATE({inp("bond_term")},-D7,Funding!D15,-D6)'),9:('Price per 100 at selected yield',f'=-PV({inp("bond_yield")},{inp("bond_term")},{inp("bond_coupon")}*100,100)'),10:('Benchmark total cash coupon, five years',f'=D7*{inp("bond_term")}')}
    for r,(label,f) in rows.items():put(s,r,label,[f],PCT if r==8 else NUM)
    note(s,12,'Hypothetical debt, not an announced bond or market quote. Fixed coupon and selected valuation yield are separate. Own May 2026 notes provide a historical coupon range only, not comparable live yields.')
    header(s,15,['Year','Opening carrying','Cash coupon','Effective interest','Fee amortisation','Principal','Closing carrying'])
    for r in range(16,21):
        year=r-15;s.cell(r,3,year)
        fs={4:'=Funding!D15' if r==16 else f'=I{r-1}',5:'=$D$7',6:f'=D{r}*$D$8',7:f'=F{r}-E{r}',8:f'=IF(C{r}={inp("bond_term")},$D$6,0)',9:f'=D{r}+G{r}-H{r}'}
        for c,f in fs.items():s.cell(r,c,f);s.cell(r,c).number_format=NUM
    s['I20']='=ROUND(D20+G20-H20,6)'
    header(s,23,['Assumed yield','Price per 100'])
    for r,y in enumerate(YIELD_GRID,24):s.cell(r,3,y);s.cell(r,3).number_format=PCT;s.cell(r,4,f'=-PV(C{r},{inp("bond_term")},{inp("bond_coupon")}*100,100)').number_format='0.00'
    note(s,30,'Five-year annual schedule is fixed. Change coupon, yield or fee for sensitivities; changing maturity requires rebuilding the schedule. Principal is a cash outflow at maturity, not a financing expense.')
    s=w['Position'];header(s,5,['Issue-only snapshot','Package close','Package settled','Immediate common','Straight debt'])
    for r,label in {6:'Reported opening cash',7:'Net issuance cash',8:'Pro forma cash before deployment',9:'Total assets',10:'Liabilities plus equity capital',11:'Balance difference',13:'Liabilities',14:'Equity capital'}.items():s.cell(r,3,label)
    for col in 'DEFG':
        inflow='=Funding!D8' if col=='D' else '=Funding!D15'
        s[f'{col}6']=f'={inp("cash")}';s[f'{col}7']=inflow;s[f'{col}8']=f'=SUM({col}6:{col}7)';s[f'{col}9']=f'={inp("assets")}+{col}7';s[f'{col}13']=f'={inp("liabilities")}'+(f'+{col}7' if col=='G' else '');s[f'{col}14']=f'={inp("equity")}'+('' if col=='G' else f'+{col}7');s[f'{col}10']=f'=SUM({col}13:{col}14)';s[f'{col}11']=f'={col}9-{col}10'
        for r in (6,7,8,9,10,11,13,14):s[f'{col}{r}'].number_format='0.00' if r==11 else NUM
    note(s,17,'Static issuance bridge on 30 Sep balances, not a forecast balance sheet at future dates. Proceeds retained as cash; no capex, operating flows, bridge overlay, dividends or other balance changes. Securities remain separate from cash.')
    note(s,19,'Preferred treated as equity capital and issuance costs deducted from equity. New bond costs reduce carrying debt. Final classification, existing instruments and forward derivative accounting unverified. Package settled excludes any intervening dividends.')
    s=w['Cover'];header(s,5,['ECM / DCM Financing Case','Result'])
    put(s,6,'Call',['ACCEPT FOR STAGED FUNDING'])
    s.merge_cells('D6:G6')
    for r,label,f in [(8,'Gross priced package (USDm)','=Funding!D10'),(9,'Expected initial net cash (USDm)','=Funding!D16'),(10,'Deferred net proceeds (USDm)','=Funding!D14'),(11,'Annual preferred dividends (USDm)','=Funding!D19'),(12,'Bridge after-tax cost to deadline (USDm)','=Funding!D22'),(13,'Debt alternative annual after-tax coupon (USDm)','=Alternatives!F10'),(14,'Conditional ATM excluded (USDm)','=Funding!D18')]:put(s,r,label,[f])
    note(s,17,'Accept the equity-led package for staged investment. If the full amount is required at close, arrange funding for the deferred proceeds. Do not count the planned ATM as cash. This is an issuer financing recommendation, not a Meta stock recommendation.')
    note(s,19,'Conversion analysis illustrates initial Class A terms. Pending Class C recapitalisation must be modelled before quoting actual 2029 dilution. Final prospectus and forward agreements remain review items.')
    s=w['Sources'];header(s,5,['ID','Document / locator','URL']);s.column_dimensions['D'].width=80;s.column_dimensions['E'].width=95
    for r,(k,(desc,url)) in enumerate(SOURCES.items(),6):
        s.cell(r,3,k);s.cell(r,4,desc);s.cell(r,5,url);s.cell(r,5).hyperlink=url;s.cell(r,4).alignment=Alignment(wrap_text=True);s.cell(r,5).alignment=Alignment(wrap_text=True);s.row_dimensions[r].height=75
    for s in w:
        s.sheet_properties.tabColor='1F3864' if s.title=='Cover' else '6E8BB5' if s.title=='Inputs' else None
        s.print_area=f'C2:I{s.max_row}'
        for row in s:
            for c in row:
                if c.value is None:continue
                if c.font.name in (None,'Calibri'):
                    colour='000000' if s.title=='Cover' else '008000' if c.data_type=='f' and '!' in c.value else '000000' if c.data_type=='f' else '0000FF' if isinstance(c.value,(int,float,datetime)) else '222222'
                    c.font=Font(name='Arial',size=10,color=colour)
                if not c.alignment.wrap_text:c.alignment=Alignment(vertical='center',horizontal='right' if c.data_type=='f' or isinstance(c.value,(int,float,datetime)) else 'left')
        s.conditional_formatting.add(f'D6:I{s.max_row}',CellIsRule(operator='lessThan',formula=['-0.00001'],font=Font(color='9C0006')))
        if s.title in ('Cover','Funding','Alternatives','Conversion','Bond','Position'):s['I2'].font=Font(name='Arial',size=10,color='008000')
    for col in 'DEF':w['Alternatives'][f'{col}15'].number_format='0.00'
    (ROOT/'data').mkdir(exist_ok=True)
    with (ROOT/'data/inputs.csv').open('w',newline='') as f:
        writer=csv.writer(f,lineterminator='\n');writer.writerow(['key','label','value','tag','unit','source_or_reason'])
        for k,v in INPUTS.items():writer.writerow([k,*v])
    w.save(RAW);print(RAW)

if __name__=='__main__':main()
