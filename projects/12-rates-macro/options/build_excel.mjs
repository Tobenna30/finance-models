import fs from 'node:fs/promises';
import path from 'node:path';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const here=path.dirname(new URL(import.meta.url).pathname);
const d=JSON.parse(await fs.readFile(path.join(here,'data/build_inputs.json'),'utf8'));
const wb=Workbook.create();
const names=['Summary','Inputs','Curve','Pricing','Scenarios','Sensitivity','Sources'];
const sheets=Object.fromEntries(names.map(n=>[n,wb.worksheets.add(n)]));
const C={navy:'#16354A',teal:'#127D88',pale:'#E8F0F4',blue:'#0000FF',green:'#008040',amber:'#FFF2CC'};
function val(s,a,v){sheets[s].getRange(a).values=[[v]];}
function fx(s,a,v){sheets[s].getRange(a).formulas=[[v]];sheets[s].getRange(a).format.font.color=v.includes('!')?C.green:'#000000';}
function band(s,a,t){sheets[s].getRange(a).merge();val(s,a.split(':')[0],t);sheets[s].getRange(a).format={fill:C.navy,font:{bold:true,color:'#FFFFFF',size:12}};}
function note(s,a,t){sheets[s].getRange(a).merge();val(s,a.split(':')[0],t);sheets[s].getRange(a).format.wrapText=true;sheets[s].getRange(a).format.rowHeight=34;}
for(const [n,s] of Object.entries(sheets)){
 s.showGridLines=false;s.getRange('A1:L65').format.font={name:'Arial',size:10};
 s.getRange('A:A').format.columnWidth=39;s.getRange('B:D').format.columnWidth=19;s.getRange('E:H').format.columnWidth=19;
 s.getRange('A1:H65').format.rowHeight=21;
 band(n,'A1:H2',n==='Summary'?'Sterling receiver options | Project 12':`Project 12 | ${n}`);
}
const ins=sheets.Inputs;band('Inputs','A4:H4','Blue = editable | S sourced, A assumption, D derived');
ins.getRange('A5:D5').values=[['Input','Value','Tag','Meaning / units']];
let r=6;for(const [key,[v,tag,reason]] of Object.entries(d.inputs)){
 ins.getRange(`A${r}:D${r}`).values=[[key,v,tag,reason]];
 ins.getRange(`B${r}`).format.font.color=C.blue;
 ins.getRange(`D${r}:H${r}`).merge();val('Inputs',`D${r}`,reason);ins.getRange(`D${r}:H${r}`).format.wrapText=true;ins.getRange(`A${r}:H${r}`).format.rowHeight=32;r++;
}
val('Inputs','A24','Curve date');val('Inputs','B24',d.asof);val('Inputs','C24','S');
note('Inputs','A26:H27','Default volatilities and costs are assumptions. Quote cells are blank. Mode 1 requires source and timestamp; missing data blocks valuation. Dealer mode does not establish an executable or attractive trade.');
ins.getRange('B14:B19').format.fill=C.amber;ins.getRange('B14').setNumberFormat('0.000%');ins.getRange('B6').setNumberFormat('#,##0');
for(const cell of ['B13','B15'])ins.getRange(cell).dataValidation={rule:{type:'list',values:['0','1']}};
ins.dataValidations.add({range:'B8',rule:{type:'whole',operator:'between',formula1:1,formula2:10}});
ins.dataValidations.add({range:'B7',rule:{type:'decimal',operator:'between',formula1:1/12,formula2:2}});
ins.dataValidations.add({range:'B9',rule:{type:'decimal',operator:'greaterThan',formula1:0}});
for(const cell of ['B10','B11','B12','B16','B17'])ins.dataValidations.add({range:cell,rule:{type:'decimal',operator:'greaterThanOrEqual',formula1:0}});
val('Inputs','A6','Notional (£)');const curve=sheets.Curve;curve.getRange('A5:B5').values=[['Years','Zero rate (% continuous)']];
curve.getRange(`A6:B${d.curve.length+5}`).values=d.curve;curve.getRange(`B6:B${d.curve.length+5}`).setNumberFormat('0.000000');curve.freezePanes.freezeRows(5);
note('Curve','D5:H7','S | BoE fitted OIS zero curve; percent continuous. Linear interpolation. No extrapolation. Source URL, retrieval date and hash are in Sources and data/curves.json.');
const end=d.curve.length+5;const xr=`Curve!$A$6:$A$${end}`,yr=`Curve!$B$6:$B$${end}`;
const pr=sheets.Pricing;
val('Pricing','A4','Basic inputs valid');
fx('Pricing','B4','=AND(ISNUMBER(Inputs!B6),Inputs!B6>0,ISNUMBER(Inputs!B7),Inputs!B7>=1/12,Inputs!B7<=2,ISNUMBER(Inputs!B8),Inputs!B8=INT(Inputs!B8),Inputs!B8>=1,Inputs!B8<=10,ISNUMBER(Inputs!B9),Inputs!B9>0,ISNUMBER(Inputs!B10),Inputs!B10>=0,ISNUMBER(Inputs!B11),Inputs!B11>=0,ISNUMBER(Inputs!B12),Inputs!B12>=0,ISNUMBER(Inputs!B20),ISNUMBER(Inputs!B21),OR(Inputs!B13=0,Inputs!B13=1),OR(Inputs!B15=0,Inputs!B15=1))');
val('Pricing','D4','Dealer fields valid');
fx('Pricing','E4','=AND(IF(OR(Inputs!B13=1,Inputs!B15=1),AND(Inputs!B18<>"",Inputs!B19<>""),TRUE),IF(Inputs!B13=1,ISNUMBER(Inputs!B14),TRUE),IF(Inputs!B15=1,AND(ISNUMBER(Inputs!B16),Inputs!B16>=0,ISNUMBER(Inputs!B17),Inputs!B17>=0),TRUE))');
pr.getRange('A5:K5').values=[['Cash flow','Time','Index','Lower t','Upper t','Lower z %','Upper z %','Zero %','DF','Alpha','DF x alpha']];
for(let rr=6;rr<=17;rr++){
 val('Pricing',`A${rr}`,rr===6?'Option expiry':rr===17?'Underlying maturity':`Payment ${rr-6}`);
 fx('Pricing',`B${rr}`,rr===6?'=Inputs!B7':rr===17?'=Inputs!B7+Inputs!B8':`=IF(${rr-6}<=Inputs!B8,Inputs!B7+${rr-6},Inputs!B7)`);
 fx('Pricing',`C${rr}`,`=IF(AND(B${rr}>=MIN(${xr}),B${rr}<=MAX(${xr})),MIN(ROWS(${xr})-1,MATCH(B${rr},${xr},1)),NA())`);
 fx('Pricing',`D${rr}`,`=INDEX(${xr},C${rr})`);fx('Pricing',`E${rr}`,`=INDEX(${xr},C${rr}+1)`);
 fx('Pricing',`F${rr}`,`=INDEX(${yr},C${rr})`);fx('Pricing',`G${rr}`,`=INDEX(${yr},C${rr}+1)`);
 fx('Pricing',`H${rr}`,`=F${rr}+(G${rr}-F${rr})*(B${rr}-D${rr})/(E${rr}-D${rr})+Inputs!B20/100`);
 fx('Pricing',`I${rr}`,`=EXP(-H${rr}/100*B${rr})`);
 fx('Pricing',`J${rr}`,rr>6&&rr<17?`=IF(${rr-6}<=Inputs!B8,1,0)`:'=0');fx('Pricing',`K${rr}`,`=I${rr}*J${rr}`);
}
const rows={21:['Curve forward','=(I6-I17)/B22'],22:['Discount annuity','=SUM(K7:K16)'],23:['PV01 (£ per bp)','=Inputs!B6*B22/10000'],
24:['Selected forward','=IF(AND(B4,E4),IF(Inputs!B13=1,Inputs!B14,B21),NA())'],
25:['Long normal vol (bp)','=IF(AND(B4,E4),IF(Inputs!B15=1,Inputs!B16,Inputs!B10),NA())'],26:['Short normal vol (bp)','=IF(AND(B4,E4),IF(Inputs!B15=1,Inputs!B17,Inputs!B11),NA())'],
27:['Long strike','=B24'],28:['Short strike','=B27-Inputs!B9/10000'],29:['Long rate std dev','=B25/10000*SQRT(Inputs!B7)'],30:['Short rate std dev','=B26/10000*SQRT(Inputs!B7)'],
31:['Long d','=IF(B29=0,0,(B27-B24)/B29)'],32:['Short d','=IF(B30=0,0,(B28-B24)/B30)'],
33:['Long receiver value (rate)','=IF(B29=0,MAX(B27-B24,0),(B27-B24)*NORMSDIST(B31)+B29*EXP(-(B31^2)/2)/SQRT(2*PI()))'],
34:['Sold receiver value (rate)','=IF(B30=0,MAX(B28-B24,0),(B28-B24)*NORMSDIST(B32)+B30*EXP(-(B32^2)/2)/SQRT(2*PI()))'],
35:['Spread value (rate)','=B33-B34'],36:['Vertical bounds valid','=AND(B35>=0,B35<=Inputs!B9/10000)'],
38:['Outright delta (£ / rate bp)','=IF(B29=0,-0.5,-NORMSDIST(B31))*B23'],
39:['Spread delta (£ / rate bp)','=B38-IF(B30=0,0,-NORMSDIST(B32)*B23)'],
40:['Outright vega (£ / norm bp)','=IF(B29=0,0,Inputs!B6*B22*SQRT(Inputs!B7)*EXP(-(B31^2)/2)/SQRT(2*PI())/10000)'],
41:['Spread parallel vega','=B40-IF(B30=0,0,Inputs!B6*B22*SQRT(Inputs!B7)*EXP(-(B32^2)/2)/SQRT(2*PI())/10000)']};
for(const [rr,[label,formula]] of Object.entries(rows)){val('Pricing',`A${rr}`,label);fx('Pricing',`B${rr}`,formula);}
pr.getRange('B21:B28').setNumberFormat('0.000000');pr.getRange('B24').setNumberFormat('0.000%');pr.getRange('B27:B28').setNumberFormat('0.000%');pr.getRange('B33:B35').setNumberFormat('0.00000000');pr.getRange('B38:B41').setNumberFormat('#,##0.00;(#,##0.00)');
note('Pricing','D21:K23','Synthetic annual-pay swap. Dealer forward must reference the same underlying. Annuity is curve-derived even in dealer mode. Zero-vol kink delta uses half-delta convention. A negative vertical value flags inconsistent strike vols, not an arbitrage trade.');
pr.getRange('B4').conditionalFormats.addCustom('B4=FALSE',{fill:'#FCE4D6'});pr.getRange('E4').conditionalFormats.addCustom('E4=FALSE',{fill:'#FCE4D6'});
const sum=sheets.Summary;
note('Summary','A4:H5','Independent research | Synthetic SONIA receiver comparison. No executable swaption quote or post-Budget curve is supplied. Model values are not trade recommendations.');
const outputs={7:['Input state','=IF(NOT(AND(Pricing!B4,Pricing!E4)),"BLOCKED: INVALID / MISSING INPUTS",IF(Inputs!B15=0,"ILLUSTRATIVE VOLATILITY","DEALER VOL INPUTS: VERIFY CONVENTIONS"))'],
8:['Curve date','=Inputs!B24'],9:['Forward swap rate','=Pricing!B24'],10:['Discount annuity','=Pricing!B22'],11:['PV01 (£/bp)','=Pricing!B23'],
13:['Outright premium (rate bp)','=Pricing!B33*10000'],14:['Spread premium (rate bp)','=Pricing!B35*10000'],15:['Spread maximum loss incl costs','=IF(Pricing!B36,(B14+Inputs!B12)*B11,NA())'],
16:['Spread maximum profit incl costs','=IF(Pricing!B36,(Inputs!B9-B14-Inputs!B12)*B11,NA())'],17:['Spread break-even rally (bp)','=IF(Pricing!B36,B14+Inputs!B12,NA())'],18:['Outright wins beyond rally (bp)','=IF(Pricing!B36,Inputs!B9+B13-B14,NA())'],
20:['Selected rate shift (bp)','=Inputs!B21'],21:['Linear receiver P&L','=(-B20-Inputs!B12)*B11'],22:['Outright receiver P&L','=(MAX(-B20,0)-B13-Inputs!B12)*B11'],23:['Receiver spread P&L','=IF(Pricing!B36,(MIN(MAX(-B20,0),Inputs!B9)-B14-Inputs!B12)*B11,NA())'],
25:['Structure state','=IF(NOT(AND(Pricing!B4,Pricing!E4)),"BLOCKED",IF(NOT(Pricing!B36),"PASS: INCONSISTENT STRIKE VOLS",IF(B16<=0,"PASS: COST EXCEEDS CAPPED PAYOFF","CONDITIONAL COMPARISON; NO TRADE SIGNAL")))']};
for(const [rr,[label,formula]]of Object.entries(outputs)){val('Summary',`A${rr}`,label);if([7,25].includes(+rr))sum.getRange(`B${rr}:H${rr}`).merge();fx('Summary',`B${rr}`,formula);}
sum.getRange('B9').setNumberFormat('0.000%');sum.getRange('B10:B18').setNumberFormat('#,##0.00;(#,##0.00)');sum.getRange('B20:B23').setNumberFormat('#,##0.00;(#,##0.00)');
note('Summary','A28:H29','Compare same notional, not equal delta or risk. Expiry P&L is present-value-equivalent with frozen initial annuity. Costs are an assumed all-in rate-bp allowance per strategy. No probability-weighted return, collateral, calendar or early-exit valuation.');
note('Summary','A31:H32','Research call: pass an unconditional cash steepener. A bounded-rally view may favour a receiver spread, subject to premium, skew and costs. Larger rallies favour the outright receiver. Current data do not establish option cheapness.');
const sc=sheets.Scenarios;sc.getRange('A5:E5').values=[['Rate shift (bp)','Linear £','Outright £','Spread £','Spread - outright £']];
for(let i=0;i<11;i++){let rr=6+i;val('Scenarios',`A${rr}`,[-100,-75,-50,-25,-10,0,10,25,50,75,100][i]);fx('Scenarios',`B${rr}`,`=(-A${rr}-Inputs!$B$12)*Pricing!$B$23`);fx('Scenarios',`C${rr}`,`=(MAX(-A${rr},0)-Summary!$B$13-Inputs!$B$12)*Pricing!$B$23`);fx('Scenarios',`D${rr}`,`=IF(Pricing!$B$36,(MIN(MAX(-A${rr},0),Inputs!$B$9)-Summary!$B$14-Inputs!$B$12)*Pricing!$B$23,NA())`);fx('Scenarios',`E${rr}`,`=D${rr}-C${rr}`);}
sc.getRange('B6:E16').setNumberFormat('#,##0;(#,##0)');
const ch=sc.charts.add('line',sc.getRange('A5:D16'));ch.title='Expiry P&L | same notional';ch.setPosition('A20','H37');ch.xAxis={axisType:'textAxis'};ch.yAxis={numberFormatCode:'#,##0',numberFormatSourceLinked:false};
note('Scenarios','A39:H40','Rate shifts are scenarios, not forecasts. Premium deducted once; frozen-annuity PV-equivalent outputs. A linear swap has uncapped loss; receiver spread loss is capped at debit only when vertical bounds are valid.');
const se=sheets.Sensitivity;se.getRange('A5:F5').values=[['Flat normal vol (bp)','ATM cost bp','OTM cost bp','Spread cost bp','Max net gain bp','Crossover rally bp']];
for(let i=0;i<7;i++){let rr=6+i;val('Sensitivity',`A${rr}`,[0,40,60,80,100,120,160][i]);fx('Sensitivity',`B${rr}`,`=A${rr}*SQRT(Inputs!$B$7)/SQRT(2*PI())`);fx('Sensitivity',`C${rr}`,`=IF(A${rr}=0,0,-Inputs!$B$9*NORMSDIST(-Inputs!$B$9/(A${rr}*SQRT(Inputs!$B$7)))+A${rr}*SQRT(Inputs!$B$7)*EXP(-0.5*(Inputs!$B$9/(A${rr}*SQRT(Inputs!$B$7)))^2)/SQRT(2*PI()))`);fx('Sensitivity',`D${rr}`,`=B${rr}-C${rr}`);fx('Sensitivity',`E${rr}`,`=Inputs!$B$9-D${rr}-Inputs!$B$12`);fx('Sensitivity',`F${rr}`,`=Inputs!$B$9+B${rr}-D${rr}`);}
se.getRange('B6:F12').setNumberFormat('0.00');note('Sensitivity','A15:H16','Sensitivity grid assumes the same vol for both strikes. Active pricing permits different long/short vols on Inputs. No calibration or observed market vol is claimed.');
const so=sheets.Sources;so.getRange('A5:E5').values=[['Tag','Source','Data date','URL','Use / limitation']];so.getRange(`A6:E${5+d.sources.length}`).values=d.sources;so.getRange('B:B').format.columnWidth=30;so.getRange('D:D').format.columnWidth=65;so.getRange('E:E').format.columnWidth=75;so.getRange('A6:E11').format.wrapText=true;so.getRange('A6:E11').format.rowHeight=60;
for(const s of Object.values(sheets))s.getRange('A5:H5').format.fill=C.pale;
for(const n of ['Pricing','Sensitivity','Scenarios'])sheets[n].freezePanes.freezeRows(5);
await wb.recalculate();
await fs.mkdir(path.join(here,'previews'),{recursive:true});
for(const [n,range]of [['Summary','A1:H32'],['Inputs','A1:H27'],['Curve','A1:H12'],['Pricing','A19:K42'],['Scenarios','A1:H40'],['Sensitivity','A1:H16'],['Sources','A1:H11']]){
 const blob=await wb.render({sheetName:n,range,scale:1.3,format:'png'});await fs.writeFile(path.join(here,'previews',n+'.png'),new Uint8Array(await blob.arrayBuffer()));
}
const out=path.resolve(here,'../models/Sterling_Receiver_Options.xlsx');await fs.mkdir(path.dirname(out),{recursive:true});
const xlsx=await SpreadsheetFile.exportXlsx(wb);await xlsx.save(out);
console.log(JSON.stringify({out,forward: sheets.Pricing.getRange('B24').values,premium:sheets.Summary.getRange('B13:B18').values}));
