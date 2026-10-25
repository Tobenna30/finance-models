"""Build the live LSEG Excel model (v2, driver-based). Every forecast cell is a formula.
Run from projects/01-equity-pitch-kit: python -m lseg.build_excel"""
from copy import copy
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter as CL
from . import assumptions as A
from .engine import run, sotp, solve, stub, pe_history, beta_sensitivity, KEYS, DIV_OF
from .trackers import hiring, weekly
from openpyxl.chart import BarChart
import csv
from openpyxl.chart import LineChart, Reference

BLUE, GREEN, BOLD = Font(color="0000FF"), Font(color="008000"), Font(bold=True)
HDR, HDRF = PatternFill("solid", fgColor="1F3864"), Font(bold=True, color="FFFFFF")
SEC = PatternFill("solid", fgColor="D9E1F2"); TOP = Border(top=Side(style="thin"))
M, PCT, X, P0, P1 = '#,##0;(#,##0);"–"', '0.0%;(0.0%);"–"', '0.0"x"', '#,##0"p"', '#,##0.0"p"'
OUT = Path(__file__).resolve().parents[1] / "models" / "LSEG_Model.xlsx"
YH, YF = A.YEARS_HIST, A.YEARS_FCST
LABEL = {k: l for k, l, _ in A.LINES}
DIVN = dict(A.DIVISIONS)

wb = Workbook()
cover = wb.active; cover.title = "Cover"
inp = wb.create_sheet("Inputs"); dv = wb.create_sheet("Divisions"); qs = wb.create_sheet("Quarterly")
mdl = wb.create_sheet("Model"); dcf = wb.create_sheet("DCF"); sot = wb.create_sheet("SOTP")
cmp_ = wb.create_sheet("Comps"); cs = wb.create_sheet("vs Consensus"); rev = wb.create_sheet("Reverse DCF")
scn = wb.create_sheet("Scenarios"); pair = wb.create_sheet("Pair trade"); stb = wb.create_sheet("Stub ex-Tradeweb", 7)
hist = wb.create_sheet("Valuation history", 8); ev = wb.create_sheet("Industry evidence", 9); trk = wb.create_sheet("Trackers", 10)
src = wb.create_sheet("Sources")

def title(ws, t, sub=None):
    ws["A1"] = t; ws["A1"].font = Font(bold=True, size=14)
    if sub: ws["A2"] = sub
def hdr(ws, r, c, v):
    x = ws.cell(r, c, v); x.fill = HDR; x.font = HDRF; return x
def boldify(cell):
    f = copy(cell.font); f.bold = True; cell.font = f

# =============== Inputs ===============
I = {}; FC = {y: CL(6 + i) for i, y in enumerate(YF)}
title(inp, "LSEG – Model inputs", "Blue = hard-coded input. Tag: S = sourced, A = assumption, D = derived. £m unless stated. Series columns F–J = 2026–2030.")
for c, h in zip("ABCDE", ["Input", "Unit", "Value", "Tag", "Source / note"]): hdr(inp, 4, ord(c) - 64, h)
for y, c in FC.items(): hdr(inp, 4, ord(c) - 64, y)
row = 5
def section(t):
    global row
    row += 1; inp[f"A{row}"] = t; inp[f"A{row}"].font = BOLD
    for c in "ABCDEFGHIJ": inp[f"{c}{row}"].fill = SEC
    row += 1
def scalar(name, val, unit, tag, note="", fmt=None):
    global row
    for c, v in zip("ABCDE", [name, unit, val, tag, note]): inp[f"{c}{row}"] = v
    inp[f"C{row}"].font = BLUE
    if fmt: inp[f"C{row}"].number_format = fmt
    I[name] = f"Inputs!$C${row}"; row += 1
def series(name, vals, unit, tag, note="", fmt=PCT):
    global row
    for c, v in zip("ABDE", [name, unit, tag, note]): inp[f"{c}{row}"] = v
    I[name] = {}
    for y, v in zip(YF, vals):
        c = inp[f"{FC[y]}{row}"]
        if v is not None: c.value = v; c.font = BLUE
        else: c.fill = PatternFill("solid", fgColor="EEEEEE")
        c.number_format = fmt; I[name][y] = f"Inputs!${FC[y]}${row}"
    row += 1

section("Scenario (1 = Bear, 2 = Base, 3 = Bull)")
scalar("Scenario", A.SCENARIO, "1/2/3", "A", "Change this cell to flex the whole model.")
SL = {"retention_adj": "Retention adjustment", "wf_spread_adj": "Workflows extra growth spread", "mkt_vol_adj": "Markets volume growth adjustment",
      "aum_adj": "ETF AUM growth adjustment", "nti_adj": "NTI spread shock (2027)", "margin_adj": "Divisional margin change per year", "tv_growth": "Terminal growth"}
inp[f"F{row}"], inp[f"G{row}"], inp[f"H{row}"] = "Bear", "Base", "Bull"
for c in "FGH": inp[f"{c}{row}"].font = BOLD
row += 1
for k, lab in SL.items():
    inp[f"A{row}"], inp[f"B{row}"], inp[f"D{row}"] = lab, "%", "A"
    for j, s in enumerate((1, 2, 3)):
        c = inp[f"{CL(6+j)}{row}"]; c.value = A.SCEN[k][s]; c.font = BLUE; c.number_format = PCT
    inp[f"C{row}"] = f"=CHOOSE({I['Scenario']},F{row},G{row},H{row})"; inp[f"C{row}"].number_format = PCT
    I[k] = f"Inputs!$C${row}"; row += 1

section("Market data & FX")
scalar("Share price", A.SHARE_PRICE, "p", "S", A.SOURCES["PX"], P0)
scalar("GBPUSD", A.GBPUSD, "$ per £", "S", "Q3 2026 guidance FX", "0.00")
scalar("EURGBP", A.EURGBP, "€ per £", "S", "Q3 2026 guidance FX", "0.00")
scalar("Opening shares", A.OPENING_SHARES, "m", "S", "31 Dec 2025, excl. treasury", "0.0")

section("Q4 2026E reported growth vs Q4 2025 (2026E = 9M actual + Q4E)")
for k in KEYS: scalar(f"Q4 growth {k}", A.Q4_GROWTH[k], "%", "A", f"{LABEL[k]}; anchored on Q3 2026 reported growth", PCT)

section("Subscription engine: ASV growth = gross sales % + price/other – (1 – retention)")
series("Retention", A.RETENTION, "%", "A", "2025A 92.4%; H1 2026 92.8%")
series("Gross sales %", A.GROSS_SALES_PCT, "% of sub. income", "D", "2025: rolling gross sales £481m / subscription income £5,187m")
series("Price & other", A.PRICE_OTHER, "%", "D", "2025 implied: 5.9% ASV – 9.3% sales + 7.6% churn = 4.2%")
for k in ("wf", "df", "an", "fs", "ri"):
    series(f"Spread {k}", A.SPREAD[k], "pp vs ASV", "A", f"{LABEL[k]} growth minus ASV growth (H1 2026 organic spreads)")

section("FTSE Russell asset-based: average ETF AUM × yield")
scalar("ETF AUM avg 2026", A.ETF_AUM_AVG_2026, "$bn", "A", "H1 2026 average $1,997bn; end-H1 $2,193bn", M)
series("ETF AUM growth", A.ETF_AUM_GROWTH, "%", "A", "Market return + net flows")
series("ETF yield change", A.ETF_YIELD_CHANGE, "%", "A", "Fee compression")

section("Markets drivers")
scalar("Tradeweb ADV 2026", A.TW_ADV_2026, "$bn/day", "A", "H1 2026 $3,180bn (+24.8%)", M)
series("Tradeweb ADV growth", A.TW_ADV_GROWTH, "%", "A")
series("FIDO capture change", A.FIDO_CAPTURE_CHANGE, "%", "A", "Revenue per $bn ADV; mix shift to derivatives")
series("SwapClear notional growth", A.SWAPCLEAR_GROWTH, "%", "A", "2025 notional cleared $1,941trn")
series("OTC capture change", A.OTC_CAPTURE_CHANGE, "%", "A")
scalar("Cash collateral 2026", A.COLLATERAL_2026, "€bn avg", "A", "2025 €101.3bn; H1 2026 €110.2bn", '0.0')
series("Collateral growth", A.COLLATERAL_GROWTH, "%", "A")
series("NTI spread change", A.NTI_SPREAD_CHANGE, "%", "A", "Rate cuts compress the spread")
for k in ("eq", "fx", "sr", "ncc", "oth"):
    series(f"Growth {k}", A.OTHER_GROWTH[k], "%", "A", LABEL[k])
scalar("Recoveries growth", A.RECOVERIES_GROWTH, "%", "A", "", PCT)

section("Divisional EBITDA margins (on income excl. recoveries)")
for d in ("D&A", "FTSE", "RI", "MKT"):
    series(f"Margin {d}", A.DIV_MARGIN[d], "%", "A", f"{DIVN[d]}: 2025A {A.DIV_EBITDA_HIST[d][2025]/sum(A.HIST_LINES[k][2025] for k in KEYS if DIV_OF[k]==d):.1%}")
scalar("Other EBITDA", A.OTHER_EBITDA, "£m", "A", "", M)

section("D&A, capex, tax, financing, NCI, cash")
series("Adj D&A % income", A.ADJ_DA_PCT, "%", "A", "2025A 11.3%")
series("Capex % income", A.CAPEX_PCT, "%", "A/S", "2026 guide c.9.5%")
scalar("Purchased amortisation 2026", A.PURCH_AMORT_2026, "£m", "A", "2025A £1,221m", M)
scalar("Purchased amortisation decline", A.PURCH_AMORT_DECLINE, "%/yr", "A", "", PCT)
scalar("Tax rate", A.TAX_RATE, "%", "S", "Guide 24–25%", PCT)
scalar("NCI share of adj NI", A.NCI_SHARE, "%", "D", "2025: adjusted NCI £334m / adjusted net income £2,529m", PCT)
scalar("NCI payout", A.NCI_PAYOUT, "%", "A", "", PCT)
scalar("Net finance rate", A.NET_FIN_RATE, "%", "D", "2025 net finance / average net debt", '0.00%')
scalar("Other cash items % EBITDA", A.OTHER_CASH_PCT, "%", "A", "Leases, WC, non-underlying; calibrated to 2026 EqFCF guide ≥ £2.8bn", '0.00%')
scalar("Dividend payout", A.DIV_PAYOUT, "% adj EPS", "D", "2025: 150p / 420.6p", PCT)
series("Buybacks (fixed)", [A.BUYBACKS_FIXED.get(y) for y in YF], "£m", "S/A", "2026 £2.6bn YTD + Q4; 2027 £0.4bn remaining + £1.25bn. Blank = formula", M)
scalar("Buyback share of surplus FCF", A.BUYBACK_SHARE_OF_SURPLUS, "%", "A", "2028+", PCT)
scalar("Buyback price growth", A.BUYBACK_PRICE_GROWTH, "%/yr", "A", "", PCT)

section("Octus acquisition")
o = A.OCTUS
scalar("Octus price", o["price_usd_m"], "$m", "S", "Q3 2026 update; debt-funded (Reuters)", M)
scalar("Octus close year", o["close_year"], "year", "A", "Not disclosed; assumed 1 Jan 2027", "0")
scalar("Octus 2026 revenue", o["rev_2026_usd_m"], "$m", "S", "$300–320m expected this year (Reuters)", M)
scalar("Octus growth", o["growth"], "%", "A", "'Double-digit growth' (LSEG)", PCT)
scalar("Octus EBITDA margin", o["ebitda_margin"], "%", "A", "", PCT)
scalar("Octus purchased amortisation", o["purch_amort"], "£m", "A", "", M)
scalar("Octus debt rate", o["debt_rate"], "%", "A", "", PCT)

section("Valuation")
d_ = A.DCF
scalar("Risk-free rate", d_["rf"], "%", "A", "UK 10y gilt area", PCT)
scalar("Beta", d_["beta"], "x", "A", "Conservative: above observed 0.41 and Blume 0.60. See DCF sheet for sensitivity.", "0.00")
scalar("Equity risk premium", d_["erp"], "%", "A", "", PCT)
scalar("Pre-tax cost of debt", d_["kd_pre"], "%", "A", "", PCT)
scalar("Debt weight", d_["debt_weight"], "%", "A", "Target D/(D+E)", PCT)
scalar("Beta (observed, 5y)", A.BETA_OBSERVED, "x", "S", "stockanalysis.com; shown for reference", "0.00")
scalar("Beta (Blume-adjusted)", A.BETA_BLUME, "x", "D", "0.67 × observed + 0.33", "0.00")

section("Tradeweb (listed subsidiary)")
scalar("Tradeweb share price", A.TW_PRICE_USD, "$", "S", "Close 22 Oct 2026", "0.00")
scalar("Tradeweb shares", A.TW_SHARES_M, "m", "S", "Class A+B+C+D, Tradeweb 10-Q filed 30 Jul 2026", "0.00")
scalar("Tradeweb forward P/E", A.TW_FWD_PE, "x", "S", "stockanalysis.com", X)
scalar("LSEG economic interest in Tradeweb", A.LSEG_TW_ECON, "%", "S", "Tradeweb 10-Q, 30 Jun 2026", PCT)
scalar("LSEG shares outstanding", A.LSEG_MKT_SHARES, "m", "S", "stockanalysis.com", "0.00")
inp.column_dimensions["A"].width = 44; inp.column_dimensions["E"].width = 72
for c in "BCDFGHIJ": inp.column_dimensions[c].width = 11

# =============== Quarterly ===============
title(qs, "LSEG – Quarterly income by line (£m)", "Q1 2025–Q3 2026 sourced from company releases. Q4 2026E = Q4 2025 × (1 + Inputs growth). FY2026E feeds the Divisions sheet.")
qcols = A.QUARTERS + ["Q4 26E", "FY25 (sum)", "FY26E", "FY26E growth", "Q4E growth"]
hdr(qs, 4, 1, "Line")
for j, h in enumerate(qcols, start=2): hdr(qs, 4, j, h)
QR = {}
for i, k in enumerate(KEYS, start=5):
    qs.cell(i, 1, LABEL[k]); QR[k] = i
    for j, v in enumerate(A.Q[k], start=2):
        c = qs.cell(i, j, v); c.font = BLUE; c.number_format = M
    qs.cell(i, 9, f"=E{i}*(1+{I['Q4 growth '+k]})").number_format = M
    qs.cell(i, 10, f"=SUM(B{i}:E{i})").number_format = M
    qs.cell(i, 11, f"=SUM(F{i}:I{i})").number_format = M
    qs.cell(i, 12, f"=K{i}/J{i}-1").number_format = PCT
    qs.cell(i, 13, f"=I{i}/E{i}-1").number_format = PCT
tq = 5 + len(KEYS)
qs.cell(tq, 1, "Total income excl. recoveries").font = BOLD
for j in range(2, 12):
    c = qs.cell(tq, j, f"=SUM({CL(j)}5:{CL(j)}{tq-1})"); c.number_format = M; c.font = BOLD; c.border = TOP
qs.cell(tq, 12, f"=K{tq}/J{tq}-1").number_format = PCT
qs.cell(tq + 1, 1, "YoY growth (total)")
for j in range(6, 10):
    qs.cell(tq + 1, j, f"={CL(j)}{tq}/{CL(j-4)}{tq}-1").number_format = PCT
qs.cell(tq + 3, 1, "Note: 2025 quarterly sums differ from reported FY by up to £5m per line (restatements/rounding); FY figures on Divisions use the reported FY.")
qs.column_dimensions["A"].width = 34
for j in range(2, 14): qs.column_dimensions[CL(j)].width = 10

# =============== Divisions (driver-based revenue + divisional EBITDA) ===============
COLS = {y: CL(3 + i) for i, y in enumerate(YH + YF)}     # C..J
def prev(y): return COLS[y - 1]
def setup(ws, t, sub):
    title(ws, t, sub)
    hdr(ws, 4, 1, "£m unless stated"); hdr(ws, 4, 2, "")
    for y, c in COLS.items():
        hdr(ws, 4, ord(c) - 64, y); ws[f"{c}5"] = "A" if y in YH else "E"; ws[f"{c}5"].alignment = Alignment(horizontal="right")
    ws.column_dimensions["A"].width = 48
    for c in COLS.values(): ws.column_dimensions[c].width = 11
    ws.freeze_panes = "C6"
setup(dv, "LSEG – Divisional build", "2026E = 9M actual + Q4E (Quarterly). 2027E+ driven by ASV/retention, ETF AUM, Tradeweb ADV, SwapClear notional and cash collateral.")
D = {}; r = 6
def line(ws, reg, key, label, hist=None, fc=None, fmt=M, bold=False, top=False, hf=None):
    global r
    ws[f"A{r}"] = label
    for y, c in COLS.items():
        cell = ws[f"{c}{r}"]
        if y in YH:
            if hf and hf(y, c) is not None: cell.value = "=" + hf(y, c)
            elif hist and y in hist and hist[y] is not None: cell.value = hist[y]; cell.font = BLUE
        elif fc:
            v = fc(y, c)
            if v is not None: cell.value = "=" + v
        cell.number_format = fmt
        if bold: boldify(cell)
        if top: cell.border = TOP
    if bold: ws[f"A{r}"].font = BOLD
    reg[key] = r; r += 1
def head(ws, t):
    global r
    r += 1; ws[f"A{r}"] = t; ws[f"A{r}"].font = BOLD
    for c in ["A", "B"] + list(COLS.values()): ws[f"{c}{r}"].fill = SEC
    r += 1
def q26(k): return f"Quarterly!$K${QR[k]}"

head(dv, "Subscription KPIs")
line(dv, D, "ret", "Revenue retention", {2025: A.KPI["Retention"][2025]}, lambda y, c: None if y == 2026 else f"{I['Retention'][y]}+{I['retention_adj']}", fmt=PCT)
line(dv, D, "asv", "ASV growth", A.KPI["ASV growth"], lambda y, c: None if y == 2026 else f"{I['Gross sales %'][y]}+{I['Price & other'][y]}-(1-{c}{D['ret']})", fmt=PCT, bold=True)

head(dv, "Data & Analytics")
for k in ("wf", "df", "an"):
    extra = f"+{I['wf_spread_adj']}" if k == "wf" else ""
    line(dv, D, k, f"  {LABEL[k]}", A.HIST_LINES[k], lambda y, c, k=k, extra=extra: q26(k) if y == 2026 else f"{prev(y)}{r}*(1+{c}${D['asv']}+{I['Spread '+k][y]}{extra})")
line(dv, D, "oct", "  Octus", fc=lambda y, c: f"IF({c}$4={I['Octus close year']},{I['Octus 2026 revenue']}/{I['GBPUSD']}*(1+{I['Octus growth']})^({c}$4-2026),IF({c}$4>{I['Octus close year']},{prev(y)}{r}*(1+{I['Octus growth']}),0))")
line(dv, D, "rev_D&A", "Data & Analytics income", fc=lambda y, c: f"SUM({c}{D['wf']}:{c}{D['oct']})", hf=lambda y, c: f"SUM({c}{D['wf']}:{c}{D['an']})" if y >= 2024 else None, bold=True, top=True)

head(dv, "FTSE Russell")
line(dv, D, "fs", "  Subscription", A.HIST_LINES["fs"], lambda y, c: q26("fs") if y == 2026 else f"{prev(y)}{r}*(1+{c}${D['asv']}+{I['Spread fs'][y]})")
line(dv, D, "aum", "    Average ETF AUM ($bn)", fc=lambda y, c: I['ETF AUM avg 2026'] if y == 2026 else f"{prev(y)}{r}*(1+{I['ETF AUM growth'][y]}+{I['aum_adj']})")
line(dv, D, "yld", "    Asset-based yield (bps)", fc=lambda y, c: f"{q26('fa')}*{I['GBPUSD']}/({c}{D['aum']}*1000)*10000" if y == 2026 else f"{prev(y)}{r}*(1+{I['ETF yield change'][y]})", fmt="0.00")
line(dv, D, "fa", "  Asset-based", A.HIST_LINES["fa"], lambda y, c: q26("fa") if y == 2026 else f"{c}{D['aum']}*1000*{c}{D['yld']}/10000/{I['GBPUSD']}")
line(dv, D, "rev_FTSE", "FTSE Russell income", fc=lambda y, c: f"{c}{D['fs']}+{c}{D['fa']}", hf=lambda y, c: f"{c}{D['fs']}+{c}{D['fa']}" if y >= 2024 else None, bold=True, top=True)

head(dv, "Risk Intelligence")
line(dv, D, "ri", "  Risk Intelligence", A.HIST_LINES["ri"], lambda y, c: q26("ri") if y == 2026 else f"{prev(y)}{r}*(1+{c}${D['asv']}+{I['Spread ri'][y]})")
line(dv, D, "rev_RI", "Risk Intelligence income", fc=lambda y, c: f"{c}{D['ri']}", hf=lambda y, c: f"{c}{D['ri']}" if y >= 2024 else None, bold=True, top=True)

head(dv, "Markets")
line(dv, D, "eq", "  Equities", A.HIST_LINES["eq"], lambda y, c: q26("eq") if y == 2026 else f"{prev(y)}{r}*(1+{I['Growth eq'][y]}+{I['mkt_vol_adj']})")
line(dv, D, "adv", "    Tradeweb ADV ($bn/day)", {2025: A.KPI["Tradeweb ADV ($bn)"][2025]}, lambda y, c: I['Tradeweb ADV 2026'] if y == 2026 else f"{prev(y)}{r}*(1+{I['Tradeweb ADV growth'][y]}+{I['mkt_vol_adj']})")
line(dv, D, "capt", "    FIDO revenue per $bn ADV (£m)", fc=lambda y, c: f"{q26('fido')}/{c}{D['adv']}" if y == 2026 else f"{prev(y)}{r}*(1+{I['FIDO capture change'][y]})", fmt="0.000",
     hf=lambda y, c: f"{c}{r+1}/{c}{D['adv']}" if y == 2025 else None)
line(dv, D, "fido", "  Fixed Income, Derivatives & Other", A.HIST_LINES["fido"], lambda y, c: q26("fido") if y == 2026 else f"{c}{D['adv']}*{c}{D['capt']}")
line(dv, D, "fx", "  FX", A.HIST_LINES["fx"], lambda y, c: q26("fx") if y == 2026 else f"{prev(y)}{r}*(1+{I['Growth fx'][y]}+{I['mkt_vol_adj']})")
line(dv, D, "otc", "  OTC Derivatives (SwapClear et al.)", A.HIST_LINES["otc"], lambda y, c: q26("otc") if y == 2026 else f"{prev(y)}{r}*(1+{I['SwapClear notional growth'][y]}+{I['mkt_vol_adj']})*(1+{I['OTC capture change'][y]})")
line(dv, D, "sr", "  Securities & Reporting", A.HIST_LINES["sr"], lambda y, c: q26("sr") if y == 2026 else f"{prev(y)}{r}*(1+{I['Growth sr'][y]})")
line(dv, D, "ncc", "  Non-Cash Collateral", A.HIST_LINES["ncc"], lambda y, c: q26("ncc") if y == 2026 else f"{prev(y)}{r}*(1+{I['Growth ncc'][y]})")
line(dv, D, "coll", "    Average cash collateral (€bn)", {2024: 109.0, 2025: 101.3}, lambda y, c: I['Cash collateral 2026'] if y == 2026 else f"{prev(y)}{r}*(1+{I['Collateral growth'][y]})", fmt="0.0")
line(dv, D, "spr", "    Net treasury spread (bps)", fc=lambda y, c: f"{q26('nti')}*{I['EURGBP']}/({c}{D['coll']}*1000)*10000" if y == 2026 else f"{prev(y)}{r}*(1+{I['NTI spread change'][y]}+IF({c}$4=2027,{I['nti_adj']},0))", fmt="0.00",
     hf=lambda y, c: f"{c}{r+1}*{I['EURGBP']}/({c}{D['coll']}*1000)*10000" if y in (2024, 2025) else None)
line(dv, D, "nti", "  Net Treasury Income", A.HIST_LINES["nti"], lambda y, c: q26("nti") if y == 2026 else f"{c}{D['coll']}*1000*{c}{D['spr']}/10000/{I['EURGBP']}")
MK = ("eq", "fido", "fx", "otc", "sr", "ncc", "nti")
line(dv, D, "rev_MKT", "Markets income", fc=lambda y, c: "+".join(f"{c}{D[k]}" for k in MK), hf=lambda y, c: "+".join(f"{c}{D[k]}" for k in MK) if y >= 2024 else None, bold=True, top=True)
head(dv, "Other")
line(dv, D, "oth", "  Other", A.HIST_LINES["oth"], lambda y, c: q26("oth") if y == 2026 else f"{prev(y)}{r}*(1+{I['Growth oth'][y]})")
line(dv, D, "rev_OTH", "Other income", fc=lambda y, c: f"{c}{D['oth']}", hf=lambda y, c: f"{c}{D['oth']}" if y >= 2024 else None, bold=True)

head(dv, "Group income")
DV = [d for d, _ in A.DIVISIONS]
line(dv, D, "tot", "Total income excl. recoveries", {2023: A.HIST["Total income"][2023]},
     lambda y, c: "+".join(f"{c}{D['rev_'+d]}" for d in DV), hf=lambda y, c: "+".join(f"{c}{D['rev_'+d]}" for d in DV) if y >= 2024 else None, bold=True)
line(dv, D, "g", "  growth", fc=lambda y, c: f"{c}{D['tot']}/{prev(y)}{D['tot']}-1", hf=lambda y, c: f"{c}{D['tot']}/{prev(y)}{D['tot']}-1" if y >= 2024 else None, fmt=PCT)
for d, nm in A.DIVISIONS[:4]:
    line(dv, D, "gd_" + d, f"  {nm} growth", fc=lambda y, c, d=d: f"{c}{D['rev_'+d]}/{prev(y)}{D['rev_'+d]}-1", hf=lambda y, c, d=d: f"{c}{D['rev_'+d]}/{prev(y)}{D['rev_'+d]}-1" if y == 2025 else None, fmt=PCT)

head(dv, "Divisional adjusted EBITDA")
for d, nm in A.DIVISIONS[:4]:
    line(dv, D, "m_" + d, f"  {nm} margin", fc=lambda y, c, d=d: f"{I['Margin '+d][y]}+IF({c}$4>=2027,{I['margin_adj']}*({c}$4-2026),0)",
         hf=lambda y, c, d=d: f"{c}{r+1}/{c}{D['rev_'+d]}" if y >= 2024 else None, fmt=PCT)
    line(dv, D, "e_" + d, f"  {nm} EBITDA", A.DIV_EBITDA_HIST[d],
         lambda y, c, d=d: (f"({c}{D['rev_D&A']}-{c}{D['oct']})" if d == "D&A" else f"{c}{D['rev_'+d]}") + f"*{c}{D['m_'+d]}")
line(dv, D, "e_oct", "  Octus EBITDA", fc=lambda y, c: f"{c}{D['oct']}*{I['Octus EBITDA margin']}")
line(dv, D, "e_OTH", "  Other EBITDA", A.DIV_EBITDA_HIST["OTH"], lambda y, c: I['Other EBITDA'])
EK = ("e_D&A", "e_FTSE", "e_RI", "e_MKT", "e_oct", "e_OTH")
line(dv, D, "ebitda", "Group adjusted EBITDA", {2023: A.HIST["Adj EBITDA"][2023]}, lambda y, c: "+".join(f"{c}{D[k]}" for k in EK),
     hf=lambda y, c: "+".join(f"{c}{D[k]}" for k in EK if k != "e_oct") if y >= 2024 else None, bold=True, top=True)
line(dv, D, "mg", "  Group EBITDA margin", fc=lambda y, c: f"{c}{D['ebitda']}/{c}{D['tot']}", hf=lambda y, c: f"{c}{D['ebitda']}/{c}{D['tot']}", fmt=PCT)
for row_ in dv.iter_rows(min_row=6):
    for cell in row_[2:]:
        if isinstance(cell.value, str) and cell.value.startswith("=Quarterly!"): cell.font = GREEN

# =============== Model ===============
setup(mdl, "LSEG – Integrated model", "Income and EBITDA link from Divisions. Historical cells are sourced (blue); forecasts are formulas.")
R = {}; r = 6
def dref(k): return lambda y, c: f"Divisions!{c}{D[k]}"
head(mdl, "Profit & loss (adjusted)")
line(mdl, R, "tot", "Total income excl. recoveries", fc=dref("tot"), hf=dref("tot"), bold=True)
line(mdl, R, "rec", "Recoveries", A.HIST["Recoveries"], lambda y, c: f"{prev(y)}{r}*(1+{I['Recoveries growth']})")
line(mdl, R, "ebitda", "Adjusted EBITDA", fc=dref("ebitda"), hf=dref("ebitda"), bold=True)
line(mdl, R, "mg", "  margin", fc=lambda y, c: f"{c}{R['ebitda']}/{c}{R['tot']}", hf=lambda y, c: f"{c}{R['ebitda']}/{c}{R['tot']}", fmt=PCT)
line(mdl, R, "da", "Adjusted D&A", A.HIST["Adj D&A"], lambda y, c: f"{c}{R['tot']}*{I['Adj D&A % income'][y]}")
line(mdl, R, "ebit", "Adjusted operating profit", fc=lambda y, c: f"{c}{R['ebitda']}-{c}{R['da']}", hf=lambda y, c: f"{c}{R['ebitda']}-{c}{R['da']}", bold=True, top=True)
line(mdl, R, "fin", "Net finance expense", A.HIST["Net finance"],
     lambda y, c: f"({prev(y)}{{debt}}-{prev(y)}{{cash}})*{I['Net finance rate']}+IF({c}$4>={I['Octus close year']},{I['Octus price']}/{I['GBPUSD']}*({I['Octus debt rate']}-{I['Net finance rate']}),0)")
line(mdl, R, "pbt", "Adjusted profit before tax", fc=lambda y, c: f"{c}{R['ebit']}-{c}{R['fin']}", hf=lambda y, c: f"{c}{R['ebit']}-{c}{R['fin']}" if y >= 2024 else None)
line(mdl, R, "tax", "Tax", fc=lambda y, c: f"{c}{R['pbt']}*{I['Tax rate']}")
line(mdl, R, "ni", "Adjusted net income", fc=lambda y, c: f"{c}{R['pbt']}-{c}{R['tax']}")
line(mdl, R, "nci", "  Non-controlling interests (Tradeweb)", A.HIST["NCI"], lambda y, c: f"{c}{R['ni']}*{I['NCI share of adj NI']}")
line(mdl, R, "ni_sh", "Adjusted net income to shareholders", fc=lambda y, c: f"{c}{R['ni']}-{c}{R['nci']}", bold=True, top=True)
line(mdl, R, "eps", "Adjusted EPS (p)", A.HIST["Adj EPS"], lambda y, c: f"{c}{R['ni_sh']}/{c}{{sh_avg}}*100", fmt=P1, bold=True)
line(mdl, R, "eps_g", "  EPS growth", fc=lambda y, c: f"{c}{R['eps']}/{prev(y)}{R['eps']}-1", hf=lambda y, c: f"{c}{R['eps']}/{prev(y)}{R['eps']}-1" if y >= 2024 else None, fmt=PCT)
head(mdl, "Reported bridge")
line(mdl, R, "pa_core", "  Purchased intangible amortisation (existing)", A.HIST["Purchased amortisation"],
     lambda y, c: I['Purchased amortisation 2026'] if y == YF[0] else f"{prev(y)}{r}*(1-{I['Purchased amortisation decline']})")
line(mdl, R, "pa_oct", "  Octus purchased amortisation", fc=lambda y, c: f"IF({c}$4>={I['Octus close year']},{I['Octus purchased amortisation']},0)")
line(mdl, R, "pa", "Total purchased amortisation", fc=lambda y, c: f"{c}{R['pa_core']}+{c}{R['pa_oct']}")
line(mdl, R, "rep_ni", "Reported net income (total)", fc=lambda y, c: f"({c}{R['pbt']}-{c}{R['pa']})*(1-{I['Tax rate']})")
head(mdl, "Cash flow")
line(mdl, R, "capex", "Capex", A.HIST["Capex"], lambda y, c: f"{c}{R['tot']}*{I['Capex % income'][y]}")
line(mdl, R, "other", "Other cash items (leases, WC, non-underlying)", fc=lambda y, c: f"{c}{R['ebitda']}*{I['Other cash items % EBITDA']}")
line(mdl, R, "eqfcf", "Equity free cash flow", A.HIST["Equity FCF"], lambda y, c: f"{c}{R['ebitda']}-{c}{R['capex']}-{c}{R['fin']}-{c}{R['tax']}-{c}{R['other']}", bold=True, top=True)
line(mdl, R, "acq", "Acquisitions (Octus)", fc=lambda y, c: f"IF({c}$4={I['Octus close year']},{I['Octus price']}/{I['GBPUSD']},0)")
line(mdl, R, "debt_add", "New debt raised", fc=lambda y, c: f"{c}{R['acq']}")
line(mdl, R, "div", "Dividends paid", fc=lambda y, c: f"{c}{{dps}}*{c}{{sh_open}}/100")
line(mdl, R, "nci_div", "Dividends to NCI", fc=lambda y, c: f"{c}{R['nci']}*{I['NCI payout']}")
line(mdl, R, "bb", "Share buybacks", A.HIST["Buybacks"],
     lambda y, c: f"IF(ISNUMBER({I['Buybacks (fixed)'][y]}),{I['Buybacks (fixed)'][y]},MAX(0,({c}{R['eqfcf']}-{c}{R['div']}-{c}{R['nci_div']})*{I['Buyback share of surplus FCF']}))")
line(mdl, R, "dcash", "Net change in cash", fc=lambda y, c: f"{c}{R['eqfcf']}-{c}{R['acq']}+{c}{R['debt_add']}-{c}{R['div']}-{c}{R['nci_div']}-{c}{R['bb']}", bold=True, top=True)
head(mdl, "Shares & returns")
line(mdl, R, "sh_open", "Opening shares (m)", fc=lambda y, c: I['Opening shares'] if y == YF[0] else f"{prev(y)}{{sh_close}}", fmt="0.0")
line(mdl, R, "px", "Average buyback price (p)", fc=lambda y, c: f"{I['Share price']}*(1+{I['Buyback price growth']})^({YF.index(y)}+0.5)", fmt=P0)
line(mdl, R, "sh_close", "Closing shares (m)", fc=lambda y, c: f"{c}{R['sh_open']}-{c}{R['bb']}/{c}{R['px']}*100", fmt="0.0")
line(mdl, R, "sh_avg", "Average shares (m)", A.HIST["WASO"], lambda y, c: f"({c}{R['sh_open']}+{c}{R['sh_close']})/2", fmt="0.0")
line(mdl, R, "dps", "DPS (p)", A.HIST["DPS"], lambda y, c: f"{c}{R['ni_sh']}/{c}{R['sh_open']}*100*{I['Dividend payout']}", fmt=P1)
head(mdl, "Balance sheet (economic; clearing balances excluded)")
OB = A.OPENING_BS
line(mdl, R, "cash", "Cash", {2025: OB["Cash"]}, lambda y, c: f"{prev(y)}{r}+{c}{R['dcash']}")
line(mdl, R, "intang", "Goodwill, intangibles & PP&E", {2025: OB["Goodwill & intangibles"]}, lambda y, c: f"{prev(y)}{r}+{c}{R['capex']}+{c}{R['acq']}-{c}{R['da']}-{c}{R['pa']}")
line(mdl, R, "othnet", "Other net assets / (liabilities)", fc=lambda y, c: f"{prev(y)}{r}+{c}{R['other']}+{c}{R['pa']}*{I['Tax rate']}")
line(mdl, R, "debt", "Borrowings incl. leases", {2025: OB["Borrowings incl leases"]}, lambda y, c: f"{prev(y)}{r}+{c}{R['debt_add']}")
line(mdl, R, "equity", "Total equity (incl. NCI)", {2025: OB["Total equity"]}, lambda y, c: f"{prev(y)}{r}+{c}{R['rep_ni']}-{c}{R['div']}-{c}{R['nci_div']}-{c}{R['bb']}")
line(mdl, R, "check", "Balance check (should be 0)", fc=lambda y, c: f"ROUND({c}{R['cash']}+{c}{R['intang']}+{c}{R['othnet']}-{c}{R['debt']}-{c}{R['equity']},3)", bold=True)
line(mdl, R, "nd", "Net debt", fc=lambda y, c: f"{c}{R['debt']}-{c}{R['cash']}", hf=lambda y, c: f"{c}{R['debt']}-{c}{R['cash']}" if y == 2025 else None, top=True)
line(mdl, R, "lev", "Net debt / adj EBITDA", fc=lambda y, c: f"{c}{R['nd']}/{c}{R['ebitda']}", hf=lambda y, c: f"{c}{R['nd']}/{c}{R['ebitda']}" if y == 2025 else None, fmt=X)
c25 = COLS[2025]
mdl[f"{c25}{R['othnet']}"] = f"={c25}{R['equity']}+{c25}{R['debt']}-{c25}{R['cash']}-{c25}{R['intang']}"; mdl[f"{c25}{R['othnet']}"].number_format = M
mdl[f"{c25}{R['check']}"] = f"=ROUND({c25}{R['cash']}+{c25}{R['intang']}+{c25}{R['othnet']}-{c25}{R['debt']}-{c25}{R['equity']},3)"
head(mdl, "Unlevered free cash flow (for DCF)")
line(mdl, R, "ufcf", "Unlevered FCF", fc=lambda y, c: f"{c}{R['ebitda']}-{c}{R['capex']}-{c}{R['ebit']}*{I['Tax rate']}-{c}{R['other']}", bold=True)
for row_ in mdl.iter_rows():
    for cell in row_:
        if isinstance(cell.value, str) and "{" in cell.value: cell.value = cell.value.format(**R)
        if isinstance(cell.value, str) and cell.value.startswith("=Divisions!"): cell.font = GREEN

# =============== DCF ===============
title(dcf, "LSEG – DCF (valuation date 31 Dec 2026, mid-year convention)")
rows = [("Cost of equity", f"={I['Risk-free rate']}+{I['Beta']}*{I['Equity risk premium']}", PCT),
        ("After-tax cost of debt", f"={I['Pre-tax cost of debt']}*(1-{I['Tax rate']})", PCT),
        ("WACC", f"=(1-{I['Debt weight']})*B3+{I['Debt weight']}*B4", PCT), ("Terminal growth", f"={I['tv_growth']}", PCT)]
for i, (lab, f, fmt) in enumerate(rows, start=3):
    dcf[f"A{i}"], dcf[f"B{i}"] = lab, f; dcf[f"B{i}"].number_format = fmt
DY = [y for y in YF if y > 2026]
hdr(dcf, 8, 1, "Year")
for j, y in enumerate(DY):
    c = CL(2 + j); mc = COLS[y]
    hdr(dcf, 8, 2 + j, y); dcf[f"{c}9"] = j + 1
    dcf[f"{c}10"] = f"=Model!{mc}{R['ufcf']}"; dcf[f"{c}10"].font = GREEN; dcf[f"{c}10"].number_format = M
    dcf[f"{c}11"] = f"=1/(1+$B$5)^({c}9-0.5)"; dcf[f"{c}11"].number_format = "0.000"
    dcf[f"{c}12"] = f"={c}10*{c}11"; dcf[f"{c}12"].number_format = M
dcf["A9"], dcf["A10"], dcf["A11"], dcf["A12"] = "Period", "Unlevered FCF", "Discount factor", "PV of FCF"
lc = CL(1 + len(DY)); lm = COLS[DY[-1]]
val = [("Sum of PV of FCF", f"=SUM(B12:{lc}12)", M), ("Terminal value (Gordon)", f"={lc}10*(1+B6)/(B5-B6)", M),
       ("PV of terminal value", f"=B16/(1+B5)^({lc}9-0.5)", M), ("Enterprise value", "=B15+B17", M),
       ("Less: net debt (end-2026)", f"=-Model!{COLS[2026]}{R['nd']}", M),
       ("Less: Tradeweb minority at market value", f"=-{I['Tradeweb share price']}*{I['Tradeweb shares']}*(1-{I['LSEG economic interest in Tradeweb']})/{I['GBPUSD']}", M),
       ("Equity value", "=B18+B19+B20", M), ("Shares (end-2026, m)", f"=Model!{COLS[2026]}{R['sh_close']}", "0.0"),
       ("Fair value per share (p)", "=B21/B22*100", P0), ("Current share price (p)", f"={I['Share price']}", P0),
       ("Upside / (downside)", "=B23/B24-1", PCT), ("TV as % of EV", "=B17/B18", PCT),
       ("Implied TV / 2030E EBITDA", f"=B16/Model!{lm}{R['ebitda']}", X), ("2027E P/E at current price", f"=B24/Model!{COLS[2027]}{R['eps']}", X)]
for i, (lab, f, fmt) in enumerate(val, start=15):
    dcf[f"A{i}"], dcf[f"B{i}"] = lab, f; dcf[f"B{i}"].number_format = fmt
for i in (18, 21, 23, 25): dcf[f"A{i}"].font = BOLD; dcf[f"B{i}"].font = BOLD
dcf["D14"] = "Fair value (p): WACC (down) × terminal growth (across)"; dcf["D14"].font = BOLD
gs = [0.020, 0.025, 0.030, 0.035, 0.040]; wsh = [-0.01, -0.005, 0, 0.005, 0.01]
for j, g in enumerate(gs): dcf[f"{CL(5+j)}15"] = g; dcf[f"{CL(5+j)}15"].number_format = PCT; dcf[f"{CL(5+j)}15"].font = BLUE
for i, w in enumerate(wsh):
    rr = 16 + i; dcf[f"D{rr}"] = f"=$B$5+{w}"; dcf[f"D{rr}"].number_format = '0.00%'
    for j in range(len(gs)):
        gc, wc = f"{CL(5+j)}$15", f"$D{rr}"
        pvf = f"SUMPRODUCT($B$10:${lc}$10/(1+{wc})^($B$9:${lc}$9-0.5))"
        tv = f"${lc}$10*(1+{gc})/({wc}-{gc})/(1+{wc})^(${lc}$9-0.5)"
        dcf[f"{CL(5+j)}{rr}"] = f"=({pvf}+{tv}+$B$19+$B$20)/$B$22*100"; dcf[f"{CL(5+j)}{rr}"].number_format = P0
bs = beta_sensitivity()
dcf["D23"] = "Beta check"; dcf["D23"].font = BOLD
dcf["D24"], dcf["E24"] = "Observed 5y beta", f"={I['Beta (observed, 5y)']}"
dcf["D25"], dcf["E25"] = "Blume-adjusted", f"={I['Beta (Blume-adjusted)']}"
dcf["D26"], dcf["E26"] = "Used in WACC", f"={I['Beta']}"
for rr in (24, 25, 26): dcf[f"E{rr}"].number_format = "0.00"
dcf["D28"] = "DCF value (p) by beta, base case (engine snapshot)"; dcf["D28"].font = BOLD
for j, (b, v) in enumerate(bs.items()):
    dcf.cell(29, 5 + j, b).number_format = "0.00"; dcf.cell(30, 5 + j, v).number_format = P0
dcf["D29"], dcf["D30"] = "Beta", "Value (p)"
dcf.column_dimensions["A"].width = 40; dcf.column_dimensions["B"].width = 12; dcf.column_dimensions["D"].width = 22

# =============== Comps ===============
title(cmp_, "LSEG – Trading comparables", A.COMPS_DATE + ". Forward P/E is the primary metric; trailing EV/EBITDA uses each provider's own EBITDA definition.")
for j, h in enumerate(["Company", "Ticker", "Peer group", "Ccy", "Mkt cap (bn)", "EV (bn)", "Fwd P/E", "EV/EBITDA TTM", "EBITDA margin"], start=1): hdr(cmp_, 4, j, h)
fm = [None, None, None, None, '0.0', '0.0', X, X, PCT]
CR = {}
for i, rv in enumerate(A.COMPS, start=5):
    CR[rv[1]] = i
    for j, v in enumerate(rv, start=1):
        c = cmp_.cell(i, j, v)
        if j >= 5: c.font = BLUE; c.number_format = fm[j - 1]
last = 4 + len(A.COMPS); r0 = last + 2
for k, (lab, fn) in enumerate([("Median – all peers", "MEDIAN"), ("Mean", "AVERAGE"), ("Max", "MAX"), ("Min", "MIN")]):  # noqa
    cmp_.cell(r0 + k, 1, lab).font = BOLD
    for col in "GHI": cmp_[f"{col}{r0+k}"] = f"={fn}({col}5:{col}{last})"; cmp_[f"{col}{r0+k}"].number_format = PCT if col == "I" else X
LS = A.LSEG_SAME_SOURCE; lr = r0 + 5
cmp_.cell(lr, 1, "LSEG (same source)").font = BOLD
for col, v, f in [("E", LS["mkt_cap"], '0.0'), ("F", LS["ev"], '0.0'), ("G", LS["fwd_pe"], X), ("H", LS["ev_ebitda"], X)]:
    cmp_[f"{col}{lr}"] = v; cmp_[f"{col}{lr}"].font = BLUE; cmp_[f"{col}{lr}"].number_format = f
cmp_.cell(lr + 1, 1, "LSEG discount to peer median (fwd P/E)"); cmp_[f"G{lr+1}"] = f"=G{lr}/G{r0}-1"; cmp_[f"G{lr+1}"].number_format = PCT
cmp_.cell(lr + 2, 1, "LSEG price on same source (p)"); cmp_[f"B{lr+2}"] = LS["price"]; cmp_[f"B{lr+2}"].font = BLUE; cmp_[f"B{lr+2}"].number_format = P0
cmp_.cell(lr + 3, 1, "Implied value at peer median fwd P/E (p)").font = BOLD; cmp_[f"B{lr+3}"] = f"=B{lr+2}*G{r0}/G{lr}"; cmp_[f"B{lr+3}"].number_format = P0
cmp_.column_dimensions["A"].width = 40; cmp_.column_dimensions["C"].width = 26

# =============== SOTP (live) ===============
title(sot, "LSEG – Sum of the parts (forward P/E basis, 2026E earnings mix)",
      "Each division's share of shareholder earnings × its peer median forward P/E → blended P/E × LSEG forward EPS (same data source as comps).")
for j, h in enumerate(["Division", "EBITDA 2026E", "D&A alloc.", "EBIT", "Interest alloc.", "Tax", "NCI", "Earnings", "Weight", "Peers", "Peer median P/E", "Weighted P/E"], start=1): hdr(sot, 4, j, h)
c26 = COLS[2026]; da_tot = sum(A.DIV_DA_2025.values())
for i, (dk, tick) in enumerate(A.SOTP_PEERS.items(), start=5):
    sot.cell(i, 1, DIVN[dk])
    sot[f"B{i}"] = f"=Divisions!{c26}{D['e_'+dk]}"; sot[f"B{i}"].font = GREEN
    sot[f"C{i}"] = f"=Model!{c26}{R['da']}*{A.DIV_DA_2025[dk]}/{da_tot}"
    sot[f"D{i}"] = f"=B{i}-C{i}"
    sot[f"E{i}"] = f"=Model!{c26}{R['fin']}*D{i}/SUM($D$5:$D$8)"
    sot[f"F{i}"] = f"=(D{i}-E{i})*{I['Tax rate']}"
    sot[f"G{i}"] = f"=Model!{c26}{R['nci']}" if dk == "MKT" else 0
    sot[f"H{i}"] = f"=D{i}-E{i}-F{i}-G{i}"
    sot[f"I{i}"] = f"=H{i}/SUM($H$5:$H$8)"
    sot[f"J{i}"] = ", ".join(tick)
    sot[f"K{i}"] = "=MEDIAN(" + ",".join(f"Comps!G{CR[t]}" for t in tick) + ")"
    sot[f"L{i}"] = f"=I{i}*K{i}"
    for col in "BCDEFGH": sot[f"{col}{i}"].number_format = M
    sot[f"I{i}"].number_format = PCT; sot[f"K{i}"].number_format = X; sot[f"L{i}"].number_format = '0.00"x"'
sot["A10"] = "Blended peer P/E"; sot["B10"] = "=SUM(L5:L8)"; sot["B10"].number_format = '0.0"x"'
sot["A11"] = "LSEG forward P/E (same source)"; sot["B11"] = f"=Comps!G{lr}"; sot["B11"].number_format = X
sot["A12"] = "LSEG forward EPS implied by source (p)"; sot["B12"] = f"=Comps!B{lr+2}/Comps!G{lr}"; sot["B12"].number_format = P1
sot["A13"] = "SOTP value per share (p)"; sot["B13"] = "=B10*B12"; sot["B13"].number_format = P0
sot["A14"] = "Upside vs price on same source"; sot["B14"] = f"=B13/Comps!B{lr+2}-1"; sot["B14"].number_format = PCT
for a in ("A13", "B13", "A14", "B14"): sot[a].font = BOLD
sot["A16"] = "EV/EBITDA SOTP not used: third-party trailing EBITDA definitions differ (LSEG shows 17.4x on the source vs c.13x on adjusted EBITDA)."
sot.column_dimensions["A"].width = 30; sot.column_dimensions["J"].width = 30
for col in "BCDEFGHIKL": sot.column_dimensions[col].width = 12

# =============== vs Consensus ===============
title(cs, "LSEG – Model vs company-compiled consensus", "Consensus: LSEG IR, 13 Oct 2026 (12 analysts), before the Octus deal and Q3 upgrade. Model income shown ex-Octus.")
CY = [2026, 2027, 2028]
for j, h in enumerate(["Line"] + [f"Model {y}" for y in CY] + [f"Cons {y}" for y in CY] + [f"Diff {y}" for y in CY], start=1): hdr(cs, 4, j, h)
mp = [("Data & Analytics", f"Divisions!{{c}}{D['rev_D&A']}-Divisions!{{c}}{D['oct']}", M), ("FTSE Russell", f"Divisions!{{c}}{D['rev_FTSE']}", M),
      ("Risk Intelligence", f"Divisions!{{c}}{D['rev_RI']}", M), ("Markets", f"Divisions!{{c}}{D['rev_MKT']}", M),
      ("Total income excl. recoveries", f"Divisions!{{c}}{D['tot']}-Divisions!{{c}}{D['oct']}", M),
      ("Adjusted EBITDA", f"Model!{{c}}{R['ebitda']}", M), ("Adjusted EPS (p)", f"Model!{{c}}{R['eps']}", P1), ("DPS (p)", f"Model!{{c}}{R['dps']}", P1)]
for i, (lab, f, fmt) in enumerate(mp, start=5):
    cs.cell(i, 1, lab)
    for j, y in enumerate(CY):
        m_ = cs.cell(i, 2 + j, "=" + f.format(c=COLS[y])); m_.font = GREEN; m_.number_format = fmt
        c_ = cs.cell(i, 5 + j, A.CONSENSUS[lab][y]); c_.font = BLUE; c_.number_format = fmt
        cs.cell(i, 8 + j, f"={CL(2+j)}{i}/{CL(5+j)}{i}-1").number_format = PCT
cs.column_dimensions["A"].width = 32

# =============== Reverse DCF & Scenarios (engine snapshots) ===============
res = {s: run(s) for s in (1, 2, 3)}
title(rev, "LSEG – What is priced in (reverse DCF)", "Snapshot from lseg/engine.py: each row moves one driver (base case otherwise) until DCF value = share price.")
for j, h in enumerate(["Driver (2027–2030)", "Base case", "Implied by share price", "Change needed", "Context"], start=1): hdr(rev, 4, j, h)
ra = solve("retention_adj", -0.06, 0.03); mv = solve("mkt_vol_adj", -0.20, 0.05); ma = solve("margin_adj", -0.03, 0.01); tg = solve("tv_growth", 0.0, 0.05)
rows_ = [("Revenue retention", A.RETENTION[1], A.RETENTION[1] + ra, ra, "Lowest disclosed level is 92.4% (Dec 2025)"),
         ("Markets volume growth, all drivers (shown on 2028 ADV growth)", A.TW_ADV_GROWTH[2], A.TW_ADV_GROWTH[2] + mv, mv, "Volumes shrink in real terms after a flat 2027"),
         ("Divisional margin change per year", 0.0, ma, ma, "Margins falling every year from here"),
         ("Terminal growth", A.SCEN["tv_growth"][2], tg, tg - A.SCEN["tv_growth"][2], "Below UK nominal GDP")]
for i, (lab, b, im, ch, note) in enumerate(rows_, start=5):
    for j, v in enumerate([lab, b, im, ch, note], start=1):
        c = rev.cell(i, j, v)
        if j in (2, 3, 4): c.number_format = '0.0%'
rev["A11"] = "DCF value (p) vs revenue retention, base case otherwise"; rev["A11"].font = BOLD
rev["A12"], rev["A13"] = "Retention (2027–2030)", "DCF value (p)"
for j, rt in enumerate([0.88, 0.89, 0.90, 0.91, 0.92, 0.928, 0.935], start=2):
    rev.cell(12, j, rt).number_format = '0.0%'
    rev.cell(13, j, run(2, {"retention_adj": rt - A.RETENTION[1]})["fair_value"]).number_format = P0
rev.column_dimensions["A"].width = 50; rev.column_dimensions["E"].width = 44
for j in range(2, 9): rev.column_dimensions[CL(j)].width = 12

title(scn, "LSEG – Scenarios", "Snapshot from the Python engine. Set Inputs!Scenario to 1/2/3 to reproduce any column live.")
for j, h in enumerate(["", "Bear", "Base", "Bull"], start=1): hdr(scn, 4, j, h)
srows = [("Probability", lambda s: A.SCEN_PROBS[s], PCT), ("Retention (2027+)", lambda s: A.RETENTION[1] + A.SCEN["retention_adj"][s], PCT),
         ("Markets volume growth adj.", lambda s: A.SCEN["mkt_vol_adj"][s], PCT), ("ETF AUM growth adj.", lambda s: A.SCEN["aum_adj"][s], PCT),
         ("Terminal growth", lambda s: A.SCEN["tv_growth"][s], PCT), ("2028E income", lambda s: res[s]["r"]["tot"][2028], M),
         ("2028E EBITDA margin", lambda s: res[s]["r"]["ebitda"][2028] / res[s]["r"]["tot"][2028], PCT),
         ("2028E adj EPS (p)", lambda s: res[s]["r"]["eps"][2028], P1), ("DCF value (p)", lambda s: res[s]["fair_value"], P0), ("Upside", lambda s: res[s]["upside"], PCT)]
for i, (lab, fn, fmt) in enumerate(srows, start=5):
    scn.cell(i, 1, lab)
    for j, s in enumerate((1, 2, 3)): scn.cell(i, 2 + j, fn(s)).number_format = fmt
pw = 5 + len(srows) + 1
scn.cell(pw, 1, "Probability-weighted value (p)").font = BOLD
scn.cell(pw, 2, f"=SUMPRODUCT(B5:D5,B{pw-3}:D{pw-3})").number_format = P0
scn.cell(pw + 1, 1, "Probability-weighted upside"); scn.cell(pw + 1, 2, f"=B{pw}/{I['Share price']}-1").number_format = PCT
scn.cell(pw + 3, 1, "Bear: AI substitution lifts churn (retention 91.0%), terminals shrink faster, volumes and ETF flows normalise, NTI spread cut 20%, margins drift down.")
scn.cell(pw + 4, 1, "Bull: data licensing into AI tools lifts retention to 93.5%, volumes stay firm, ETF AUM compounds, margin expansion continues.")
scn.column_dimensions["A"].width = 34

# =============== Pair trade ===============
P_ = A.PAIR
title(pair, "Trade expression: long LSEG / short FactSet (considered and rejected)", "Would isolate the AI-discount view and remove market beta. See the read below for why the outright long is preferred.")
prow = [("LSEG beta (5y)", P_["lseg_beta"], "0.00"), ("FactSet beta (5y)", P_["fds_beta"], "0.00"),
        ("Beta-neutral hedge: £ FactSet short per £1 LSEG long", "=B5/B6", "0.00"),
        ("LSEG forward P/E", P_["lseg_fwd_pe"], X), ("FactSet forward P/E", P_["fds_fwd_pe"], X),
        ("LSEG premium to FactSet", "=B8/B9-1", PCT), ("FactSet short interest (% float)", P_["fds_short_interest"], PCT),
        ("Share of LSEG income outside Data & Analytics (2026E)", f"=1-Divisions!{c26}{D['rev_D&A']}/Divisions!{c26}{D['tot']}", PCT)]
for i, (lab, v, fmt) in enumerate(prow, start=5):
    pair.cell(i, 1, lab); c = pair.cell(i, 2, v); c.number_format = fmt
    if not str(v).startswith("="): c.font = BLUE
pair["A15"] = "Read: the pair has already worked. Since Jan 2024 LSEG has beaten FactSet by c.53% in GBP (Trackers sheet), and FactSet ASV grew 7% with retention above 95%."
pair["A16"] = "Conclusion: prefer the outright long. FactSet short interest is c.9% of float, so the short leg carries squeeze risk with little valuation support left."
pair.column_dimensions["A"].width = 56

# =============== Stub ex-Tradeweb (live) ===============
title(stb, "LSEG excluding its Tradeweb stake", "Tradeweb is listed. Remove LSEG's 51.2% stake at market value and see what the rest of the group costs, on the same forward-earnings source as the comps.")
st_rows = [("LSEG market cap (£m)", f"=Comps!B{lr+2}*{I['LSEG shares outstanding']}/100", M),
           ("Tradeweb market cap (£m)", f"={I['Tradeweb share price']}*{I['Tradeweb shares']}/{I['GBPUSD']}", M),
           ("LSEG stake in Tradeweb (£m)", f"=B6*{I['LSEG economic interest in Tradeweb']}", M),
           ("  as % of LSEG market cap", "=B7/B5", PCT),
           ("Stub value: LSEG ex-Tradeweb (£m)", "=B5-B7", M),
           ("LSEG forward earnings (£m)", f"=B5/Comps!G{lr}", M),
           ("Tradeweb forward earnings attributable to LSEG (£m)", f"=B6/{I['Tradeweb forward P/E']}*{I['LSEG economic interest in Tradeweb']}", M),
           ("Stub forward earnings (£m)", "=B10-B11", M),
           ("Stub forward P/E", "=B9/B12", X),
           ("LSEG group forward P/E", f"=Comps!G{lr}", X),
           ("FactSet forward P/E", f"=Comps!G{CR['FDS']}", X),
           ("Data & analytics peer median", "=SOTP!K5", X),
           ("Stub discount to data & analytics peers", "=B13/B16-1", PCT)]
for i, (lab, f, fmt) in enumerate(st_rows, start=5):
    stb[f"A{i}"], stb[f"B{i}"] = lab, f; stb[f"B{i}"].number_format = fmt
for a in ("A13", "B13"): stb[a].font = BOLD
stb["A19"] = "Read: the rest of LSEG (Data & Analytics, FTSE Russell, Risk Intelligence, LCH, equities) costs less than FactSet on forward earnings."
stb.column_dimensions["A"].width = 52; stb.column_dimensions["B"].width = 14

# =============== Valuation history ===============
ph = pe_history()
title(hist, "LSEG trailing P/E, Jan 2022 – Oct 2026", "Month-end price ÷ LTM adjusted EPS (interpolated between reported half and full years; Dec 2026 = model). Prices: Alpha Vantage.")
for j, h in enumerate(["Month", "Price (p)", "LTM adj EPS (p)", "Trailing P/E", "5y average"], start=1): hdr(hist, 4, j, h)
for i, (mth, px, eps, pe) in enumerate(ph["rows"], start=5):
    hist.cell(i, 1, mth); hist.cell(i, 2, px).number_format = P0; hist.cell(i, 3, eps).number_format = P1
    hist.cell(i, 4, f"=B{i}/C{i}").number_format = X
    hist.cell(i, 5, f"=AVERAGE($D$5:$D${4+len(ph['rows'])})").number_format = X
n = 4 + len(ph["rows"])
for k, (lab, f) in enumerate([("Current", f"=D{n}"), ("5y average", f"=AVERAGE(D5:D{n})"), ("5y low", f"=MIN(D5:D{n})"), ("5y high", f"=MAX(D5:D{n})"),
                              ("Percentile of current", f"=PERCENTRANK(D5:D{n},D{n})")]):
    hist.cell(4 + k, 8, lab).font = BOLD; c = hist.cell(4 + k, 9, f); c.number_format = PCT if "Percentile" in lab else X
ch = LineChart(); ch.title = "LSEG trailing P/E"; ch.height, ch.width = 8, 18; ch.y_axis.title = "x"
ch.add_data(Reference(hist, min_col=4, min_row=4, max_col=5, max_row=n), titles_from_data=True)
ch.set_categories(Reference(hist, min_col=1, min_row=5, max_row=n))
hist.add_chart(ch, "H11")
hist.column_dimensions["A"].width = 10; hist.column_dimensions["H"].width = 22

# =============== SEC EDGAR cross-check on Comps ===============
edgar_path = Path(__file__).resolve().parents[3] / "data" / "edgar_us_peers.csv"
if edgar_path.exists():
    e0 = lr + 6
    cmp_.cell(e0, 1, "SEC EDGAR cross-check (US peers, latest 10-K, audited GAAP)").font = BOLD
    for j, h in enumerate(["Ticker", "FY end", "Revenue ($m)", "Operating income ($m)", "Operating margin", "Net income ($m)", "Diluted EPS ($)", "Cash ($m)", "Debt ($m)"], start=1): hdr(cmp_, e0 + 1, j, h)
    with edgar_path.open() as fh:
        for i, rw in enumerate(csv.DictReader(fh), start=e0 + 2):
            num = lambda k: float(rw[k]) / 1e6 if rw.get(k) else None
            debt = (num("debt_long") or 0) + (num("debt_current") or 0)
            vals = [rw["ticker"], rw["revenue_period_end"], num("revenue"), num("operating_income"), None, num("net_income"),
                    float(rw["eps_diluted"]) if rw["eps_diluted"] else None, num("cash"), debt or None]
            for j, v in enumerate(vals, start=1):
                c = cmp_.cell(i, j, v)
                if j in (3, 4, 6, 8, 9): c.number_format = M
                if j == 7: c.number_format = "0.00"
            cmp_.cell(i, 5, f"=D{i}/C{i}").number_format = PCT
    cmp_.cell(i + 1, 1, "Source: data.sec.gov XBRL company facts, refreshed weekly by GitHub Actions (common/edgar.py). D&A not used: XBRL tagging differs across filers.")

# =============== Industry evidence ===============
title(ev, "What third-party data says about AI and market-data demand", "Credible industry studies and filings, Apr–Oct 2026. These inform the retention and scenario assumptions; they are not inputs to formulas.")
for j, h in enumerate(["Source", "Date", "Sample", "Finding", "Read for LSEG", "Link"], start=1): hdr(ev, 4, j, h)
for i, row_ in enumerate(A.EVIDENCE, start=5):
    for j, v in enumerate(row_, start=1):
        c = ev.cell(i, j, v); c.alignment = Alignment(wrap_text=True, vertical="top")
for col, wdt in zip("ABCDEF", [30, 12, 22, 70, 40, 40]): ev.column_dimensions[col].width = wdt

# =============== Trackers (refreshed weekly by GitHub Actions) ===============
hg = hiring(); wk = weekly()
title(trk, "Trackers: hiring mix and the Tradeweb stub", "Data in /data, refreshed every Monday by .github/workflows/refresh-data.yml (Workday career sites; weekly prices).")
trk["A4"] = f"Open roles by function, snapshot {hg['date']}"; trk["A4"].font = BOLD
cos = list(hg["snap"])
hdr(trk, 5, 1, "Function")
for j, co in enumerate(cos):
    hdr(trk, 5, 2 + 2 * j, co); hdr(trk, 5, 3 + 2 * j, f"{co} %")
for i, cat in enumerate(hg["cats"], start=6):
    trk.cell(i, 1, cat)
    for j, co in enumerate(cos):
        n = hg["snap"][co].get(cat, 0); c1 = trk.cell(i, 2 + 2 * j, n)
        tot_r = 6 + len(hg["cats"])
        trk.cell(i, 3 + 2 * j, f"={CL(2+2*j)}{i}/{CL(2+2*j)}{tot_r}").number_format = PCT
tot_r = 6 + len(hg["cats"]); trk.cell(tot_r, 1, "Total").font = BOLD
for j, _ in enumerate(cos):
    trk.cell(tot_r, 2 + 2 * j, f"=SUM({CL(2+2*j)}6:{CL(2+2*j)}{tot_r-1})").font = BOLD
bc = BarChart(); bc.type = "bar"; bc.title = "Share of open roles by function"; bc.height, bc.width = 8, 14
for j, _ in enumerate(cos):
    bc.add_data(Reference(trk, min_col=3 + 2 * j, min_row=5, max_row=tot_r - 1), titles_from_data=True)
bc.set_categories(Reference(trk, min_col=1, min_row=6, max_row=tot_r - 1)); trk.add_chart(bc, "H4")
w0 = tot_r + 3
trk.cell(w0 - 1, 1, "Weekly: Tradeweb stake as % of LSEG market cap, and LSEG vs FactSet relative price in GBP (Jan 2024 = 100)").font = BOLD
for j, h in enumerate(["Week", "LSEG (p)", "Tradeweb ($)", "FactSet ($)", "GBPUSD", "Tradeweb stake % of LSEG", "LSEG vs FactSet (rebased)"], start=1): hdr(trk, w0, j, h)
for i, x in enumerate(wk, start=w0 + 1):
    vals = [x["date"], x["lseg"], x["tw"], x["fds"], x["gbpusd"], x["stake_pct"], x["rel"]]
    for j, v in enumerate(vals, start=1):
        c = trk.cell(i, j, v); c.number_format = ["@", P0, "0.00", "0.00", "0.0000", PCT, "0.0"][j - 1]
wl = w0 + len(wk)
lc1 = LineChart(); lc1.title = "Tradeweb stake as % of LSEG market cap"; lc1.height, lc1.width = 7, 14
lc1.add_data(Reference(trk, min_col=6, min_row=w0, max_row=wl), titles_from_data=True); lc1.set_categories(Reference(trk, min_col=1, min_row=w0 + 1, max_row=wl))
trk.add_chart(lc1, f"I{w0}")
lc2 = LineChart(); lc2.title = "LSEG vs FactSet, GBP, Jan 2024 = 100"; lc2.height, lc2.width = 7, 14
lc2.add_data(Reference(trk, min_col=7, min_row=w0, max_row=wl), titles_from_data=True); lc2.set_categories(Reference(trk, min_col=1, min_row=w0 + 1, max_row=wl))
trk.add_chart(lc2, f"I{w0+16}")
trk.cell(wl + 2, 1, "Tradeweb share count held at the latest 10-Q; LSEG share count interpolated between disclosed points. Prices: Yahoo Finance chart endpoint.")
trk.column_dimensions["A"].width = 22

# =============== Sources & Cover ===============
title(src, "Sources")
for i, (k, v) in enumerate(A.SOURCES.items(), start=3): src[f"A{i}"], src[f"B{i}"] = k, v
src["A12"] = "Conventions: blue = input, black = formula, green = link to another sheet. Not investment advice."
src.column_dimensions["B"].width = 90
title(cover, "London Stock Exchange Group plc (LSEG.L)")
cover["A2"] = "Driver-based model: quarterly build, divisional EBITDA, three statements, DCF, SOTP, reverse DCF, scenarios, pair trade"
cover["A3"] = "Tobenna Agubuche | github.com/Tobenna30/finance-models | Not investment advice"
items = [("Scenario selected", f"=CHOOSE({I['Scenario']},\"Bear\",\"Base\",\"Bull\")", None), ("Share price (p)", f"={I['Share price']}", P0),
         ("DCF fair value (p)", "=DCF!B23", P0), ("DCF upside", "=DCF!B25", PCT), ("SOTP value (p)", "=SOTP!B13", P0), ("SOTP upside", "=SOTP!B14", PCT),
         ("Probability-weighted DCF (p)", f"=Scenarios!B{pw}", P0), ("2026E adj EPS (p)", f"=Model!{COLS[2026]}{R['eps']}", P1),
         ("2027E P/E", "=DCF!B28", X), ("Net debt / EBITDA 2027E", f"=Model!{COLS[2027]}{R['lev']}", X),
         ("Retention implied by share price", "='Reverse DCF'!C5", PCT),
         ("Stub (ex-Tradeweb) forward P/E", "='Stub ex-Tradeweb'!B13", X),
         ("Trailing P/E vs 5y average", "='Valuation history'!I4", X),
         ("Balance sheet checks (sum, should be 0)", f"=SUM(Model!{COLS[2025]}{R['check']}:Model!{COLS[2030]}{R['check']})", '0.000')]
for i, (lab, f, fmt) in enumerate(items, start=5):
    cover[f"A{i}"], cover[f"B{i}"] = lab, f; cover[f"B{i}"].font = GREEN
    if fmt: cover[f"B{i}"].number_format = fmt
cover.column_dimensions["A"].width = 42; cover.column_dimensions["B"].width = 14

OUT.parent.mkdir(parents=True, exist_ok=True)
wb.save(OUT)
print("saved", OUT)
