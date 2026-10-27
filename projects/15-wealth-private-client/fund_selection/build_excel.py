from pathlib import Path
import json
from .assumptions import INPUTS
from .engine import calculate
from .excel_style import workbook
ROOT=Path(__file__).resolve().parents[1]
def build():
    inputs=[['Inputs: sourced and assumed values','Value','Tag','Source / rationale']]+[[k,*v[:2],v[2]] for k,v in INPUTS.items()]
    # Row mapping: capital2, return3, horizon4, I net5, R net6, I gross7, R gross8, I minimum9, R minimum10, institutional11, duration12.
    w=workbook({
      'Cover':[['Fund selection: retail family case'],['Decision','PASS institutional Class I despite lower published fee'],['Anchor','Hypothetical US-dollar family after a liquidity event'],['Scope','Two share classes of one fund, not two different managers'],['As of','30 June 2026. Historical research snapshot, not current dealing advice'],['Limitations','No allocation made; eligibility, tax and distribution-channel access need prospectus/platform review']],
      'Selection':[['Share-class comparison','Class I','Class R'],['Net expense ratio','=Inputs!B5','=Inputs!B6'],['Gross expense ratio','=Inputs!B7','=Inputs!B8'],['Illustrative first-year fee','=Inputs!B2*B2','=Inputs!B2*C2'],['10-year ending capital','=Inputs!B2*(1+Inputs!B3-B2)^Inputs!B4','=Inputs!B2*(1+Inputs!B3-C2)^Inputs!B4'],['Net fee gap, basis points','=(C2-B2)*10000'],['Annual indicative cost difference','=C4-B4'],['10-year wealth difference','=B5-C5'],['I access gate','=AND(Inputs!B11,Inputs!B2>=Inputs!B9)'],['R published minimum met','=Inputs!B2>=Inputs!B10'],['100bp parallel-yield stress, price only','=-Inputs!B12*0.01'],['Decision','Pass I: institutional eligibility not assumed. R remains a candidate, not a recommendation'],['Return convention','Hypothetical pre-expense return minus expense ratio. Never subtract fees again from published net returns'],['Stress limitation','First-order duration only: excludes carry, convexity, FX, spread and active changes']],
      'Sensitivity':[['Gross return assumption','I terminal wealth: net fees','R terminal wealth: net fees','I less R'],[-.02,'=Inputs!B2*(1+A2-Inputs!B5)^Inputs!B4','=Inputs!B2*(1+A2-Inputs!B6)^Inputs!B4','=B2-C2'],[.05,'=Inputs!B2*(1+A3-Inputs!B5)^Inputs!B4','=Inputs!B2*(1+A3-Inputs!B6)^Inputs!B4','=B3-C3'],[.08,'=Inputs!B2*(1+A4-Inputs!B5)^Inputs!B4','=Inputs!B2*(1+A4-Inputs!B6)^Inputs!B4','=B4-C4'],['Illustrative no-waiver case','I wealth at gross expense','R wealth at gross expense'],['Not a forecast','=Inputs!B2*(1+Inputs!B3-Inputs!B7)^Inputs!B4','=Inputs!B2*(1+Inputs!B3-Inputs!B8)^Inputs!B4']],
      'Inputs':inputs,
      'Sources':[['Sources','URL / detail','Page / date'],['Factsheet',json.loads((ROOT/'data/sources.json').read_text())['factsheet']['url'],'Pages 1-2; 30 Jun 2026'],['Hypothetical client','Retail family; US-dollar sleeve; not an actual client','Assumption'],['Model','Flat annual pre-expense return and fee approximation; no taxes or cash flows','Assumption'],['Waiver','31 Jan 2027 expiry is not evidence of automatic fee rise','factsheet p1'],['Identifier discrepancy','Header says LSGBXR; fund-facts table says LSGLX. Use class names, request clarification','factsheet p1']]})
    for sh in ['Selection']:
      for row in [2,3,11]:
       for cell in w[sh][row][1:]:cell.number_format='0.00%'
      for row in [4,5,7,8]:
       for cell in w[sh][row][1:]:cell.number_format='$#,##0;($#,##0);"-"'
    for row in w['Sensitivity'].iter_rows(min_row=2,max_row=4):
      row[0].number_format='0%'
      for c in row[1:]:c.number_format='$#,##0'
    for row in [2,9,10]:w['Inputs'].cell(row,2).number_format='$#,##0'
    for row in [3,5,6,7,8]:w['Inputs'].cell(row,2).number_format='0.00%'
    for col in ['B','C']:w['Sensitivity'][col+'6'].number_format='$#,##0'
    out=ROOT/'models/Fund_Selection.xlsx';w.save(out)
    (ROOT/'outputs/results.json').write_text(json.dumps(calculate(),indent=2))
    return out
if __name__=='__main__':print(build())
