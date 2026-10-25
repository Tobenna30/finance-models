"""Build the live LSEG Excel model (every forecast cell is a formula). Run: python -m lseg.build_excel"""
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter as L
from . import assumptions as A
from .engine import run, DIVS

BLUE, BLACK, GREEN = Font(color="0000FF"), Font(color="000000"), Font(color="008000")
BOLD = Font(bold=True)
HDR = PatternFill("solid", fgColor="1F3864"); HDRF = Font(bold=True, color="FFFFFF")
SEC = PatternFill("solid", fgColor="D9E1F2")
TOP = Border(top=Side(style="thin"))
M, PCT, X, P0, P1 = '#,##0;(#,##0);"–"', '0.0%;(0.0%);"–"', '0.0"x"', '#,##0"p"', '#,##0.0"p"'
OUT = Path(__file__).resolve().parents[1] / "models" / "LSEG_Model.xlsx"

wb = Workbook()
cover = wb.active; cover.title = "Cover"
inp = wb.create_sheet("Inputs"); mdl = wb.create_sheet("Model"); dcf = wb.create_sheet("DCF")
scn = wb.create_sheet("Scenarios"); src = wb.create_sheet("Sources")

# ---------------- Inputs ----------------
I = {}           # name -> absolute ref (scalar) or {year: ref} (series)
FC = {y: L(6 + i) for i, y in enumerate(A.YEARS_FCST)}   # Inputs series columns F..J
inp["A1"] = "LSEG – Model inputs"; inp["A1"].font = Font(bold=True, size=14)
inp["A2"] = "Blue = hard-coded input. Tag: S = sourced, A = assumption, D = derived. £m unless stated."
for c, h in zip("ABCDE", ["Input", "Unit", "Value", "Tag", "Source / note"]):
    inp[f"{c}4"] = h; inp[f"{c}4"].fill = HDR; inp[f"{c}4"].font = HDRF
for y, c in FC.items():
    inp[f"{c}4"] = y; inp[f"{c}4"].fill = HDR; inp[f"{c}4"].font = HDRF
row = 5
def scalar(name, val, unit, tag, note="", fmt=None):
    global row
    inp[f"A{row}"], inp[f"B{row}"], inp[f"C{row}"], inp[f"D{row}"], inp[f"E{row}"] = name, unit, val, tag, note
    inp[f"C{row}"].font = BLUE
    if fmt: inp[f"C{row}"].number_format = fmt
    I[name] = f"Inputs!$C${row}"; row += 1
def series(name, vals, unit, tag, note="", fmt=PCT):
    global row
    inp[f"A{row}"], inp[f"B{row}"], inp[f"D{row}"], inp[f"E{row}"] = name, unit, tag, note
    I[name] = {}
    for y, v in zip(A.YEARS_FCST, vals):
        c = inp[f"{FC[y]}{row}"]
        if v is not None: c.value = v
        c.font = BLUE; c.number_format = fmt
        I[name][y] = f"Inputs!${FC[y]}${row}"
    row += 1
def section(t):
    global row
    row += 1; inp[f"A{row}"] = t; inp[f"A{row}"].font = BOLD
    for c in "ABCDEFGHIJ": inp[f"{c}{row}"].fill = SEC
    row += 1

section("Scenario")
scalar("Scenario", A.SCENARIO, "1/2/3", "A", "1 = Bear, 2 = Base, 3 = Bull. Change this cell to flex the whole model.")
srow = row
for key, label, fmt in [("growth_adj", "Scenario growth adjustment (all divisions, all years)", PCT),
                        ("margin_adj", "Scenario EBITDA margin adjustment (from 2027)", PCT),
                        ("tv_growth", "Terminal growth", PCT)]:
    inp[f"A{row}"], inp[f"B{row}"], inp[f"D{row}"] = label, "%", "A"
    for j, s in enumerate((1, 2, 3)):
        c = inp[f"{L(6+j)}{row}"]; c.value = A.SCEN[key][s]; c.font = BLUE; c.number_format = fmt
    inp[f"C{row}"] = f"=CHOOSE({I['Scenario']},F{row},G{row},H{row})"; inp[f"C{row}"].number_format = fmt
    inp[f"E{row}"] = "Columns F/G/H = Bear/Base/Bull"
    I[key] = f"Inputs!$C${row}"; row += 1

section("Market data")
scalar("Share price", A.SHARE_PRICE, "p", "S", A.SOURCES["PX"], P0)
scalar("GBPUSD", A.GBPUSD, "$", "S", "Q3 2026 guidance FX assumption", "0.00")
scalar("Opening shares", A.OPENING_SHARES, "m", "S", "Shares in issue excl. treasury, 31 Dec 2025 (FY25 RNS)", "0.0")

section("Divisional growth (reported, base case)")
for d in DIVS:
    series(f"g {d}", A.GROWTH[d], "%", "A", "Guided 2026 organic cc ≥8% group; FX drag c.1–1.5pp (H1/Q3 2026)")
scalar("Recoveries growth", A.RECOVERIES_GROWTH, "%", "A", "", PCT)

section("Margins, capex, D&A")
series("EBITDA margin (ex-Octus)", A.EBITDA_MARGIN, "%", "A", "2025A 50.3%; 2026 guide +100–120bp cc; H1 2026 52.7%")
series("Adj D&A % income", A.ADJ_DA_PCT, "%", "A", "2025A 11.3%")
series("Capex % income", A.CAPEX_PCT, "%", "A/S", "2026 guided c.9.5% (Q3 2026)")
scalar("Purchased amortisation 2026", A.PURCH_AMORT_2026, "£m", "A", "2025A non-underlying D&A £1,221m", M)
scalar("Purchased amortisation decline", A.PURCH_AMORT_DECLINE, "%/yr", "A", "", PCT)

section("Tax, financing, NCI, cash")
scalar("Tax rate", A.TAX_RATE, "%", "S", "Guided 24–25% underlying", PCT)
scalar("NCI share of adj NI", A.NCI_SHARE, "%", "D", "Tradeweb minority; 2025: adj NI £2,529m vs adj EPS×WASO £2,204m", PCT)
scalar("NCI payout", A.NCI_PAYOUT, "%", "A", "", PCT)
scalar("Net finance rate", A.NET_FIN_RATE, "%", "D", "2025 net finance £179m / avg net debt", '0.00%')
scalar("Other cash items % EBITDA", A.OTHER_CASH_PCT, "%", "A", "Leases, WC, non-underlying; calibrated to 2026 EqFCF guide ≥£2.8bn", PCT)

section("Shareholder returns")
scalar("Dividend payout", A.DIV_PAYOUT, "% adj EPS", "D", "2025: 150p / 420.6p", PCT)
series("Buybacks (fixed)", [A.BUYBACKS_FIXED.get(y) for y in A.YEARS_FCST], "£m", "S/A",
       "2026: £2.6bn YTD + Q4; 2027: £0.4bn remaining + £1.25bn (mid of £1.0–1.5bn). Blank = formula", M)
scalar("Buyback share of surplus FCF", A.BUYBACK_SHARE_OF_SURPLUS, "%", "A", "2028+", PCT)
scalar("Buyback price growth", A.BUYBACK_PRICE_GROWTH, "%/yr", "A", "", PCT)

section("Octus acquisition")
o = A.OCTUS
scalar("Octus price", o["price_usd_m"], "$m", "S", "Q3 2026 trading update; debt-funded (Reuters)", M)
scalar("Octus close year", o["close_year"], "year", "A", "Not disclosed; assumed 1 Jan 2027", "0")
scalar("Octus 2026 revenue", o["rev_2026_usd_m"], "$m", "S", "$300–320m expected this year (Reuters), midpoint", M)
scalar("Octus growth", o["growth"], "%", "A", "'Double-digit revenue growth' (LSEG RNS)", PCT)
scalar("Octus EBITDA margin", o["ebitda_margin"], "%", "A", "", PCT)
scalar("Octus purchased amortisation", o["purch_amort"], "£m", "A", "", M)
scalar("Octus debt rate", o["debt_rate"], "%", "A", "Incremental cost of acquisition debt", PCT)

section("Valuation")
d = A.DCF
scalar("Risk-free rate", d["rf"], "%", "A", "UK 10y gilt area", PCT)
scalar("Beta", d["beta"], "x", "A", "", "0.00")
scalar("Equity risk premium", d["erp"], "%", "A", "", PCT)
scalar("Pre-tax cost of debt", d["kd_pre"], "%", "A", "", PCT)
scalar("Debt weight", d["debt_weight"], "%", "A", "Target D/(D+E)", PCT)
scalar("NCI multiple", d["nci_multiple"], "x P/E", "A", "Applied to Tradeweb minority earnings", X)
inp.column_dimensions["A"].width = 46; inp.column_dimensions["E"].width = 70
for c in "BCDFGHIJ": inp.column_dimensions[c].width = 11

# ---------------- Model ----------------
YH, YF = A.YEARS_HIST, A.YEARS_FCST
COLS = {y: L(3 + i) for i, y in enumerate(YH + YF)}       # C..I
mdl["A1"] = "LSEG – Integrated model"; mdl["A1"].font = Font(bold=True, size=14)
mdl["A2"] = "£m unless stated. A = actual, E = estimate. Historical cells are sourced values (blue); forecast cells are formulas."
mdl["A4"] = "Year"; mdl["A4"].fill = HDR; mdl["A4"].font = HDRF; mdl["B4"].fill = HDR
for y, c in COLS.items():
    mdl[f"{c}4"] = y; mdl[f"{c}4"].fill = HDR; mdl[f"{c}4"].font = HDRF
    mdl[f"{c}5"] = "A" if y in YH else "E"; mdl[f"{c}5"].alignment = Alignment(horizontal="right")
R = {}; r = 6
def prev(y): return COLS[y - 1]
def line(key, label, hist=None, fc=None, fmt=M, bold=False, top=False, hist_formula=None):
    """hist: {year: value}; fc: function(y, col) -> formula string (without '=')"""
    global r
    mdl[f"A{r}"] = label
    if bold: mdl[f"A{r}"].font = BOLD
    for y, c in COLS.items():
        cell = mdl[f"{c}{r}"]
        if y in YH:
            if hist_formula and hist_formula(y, c) is not None:
                cell.value = "=" + hist_formula(y, c)
            elif hist and y in hist:
                cell.value = hist[y]; cell.font = BLUE
        elif fc:
            f = fc(y, c); cell.value = "=" + f
        cell.number_format = fmt
        if bold:
            from copy import copy as _c; f_ = _c(cell.font); f_.bold = True; cell.font = f_
        if top: cell.border = TOP
    R[key] = r; r += 1
def blank(): 
    global r; r += 1
def head(t):
    global r
    blank(); mdl[f"A{r}"] = t; mdl[f"A{r}"].font = BOLD
    for c in ["A", "B"] + list(COLS.values()): mdl[f"{c}{r}"].fill = SEC
    r += 1
def ref(key, y): return f"{COLS[y]}{R[key]}"
def idx(y): return YF.index(y)

head("Income")
for dv in DIVS:
    adj = f"+{I['growth_adj']}" if dv != "Other" else ""
    line(dv, f"  {dv}", A.HIST[dv], lambda y, c, dv=dv, adj=adj: f"{prev(y)}{r}*(1+{I['g '+dv][y]}{adj})")
line("inc", "Income excl. recoveries (ex-Octus)", fc=lambda y, c: f"SUM({c}{R['Data & Analytics']}:{c}{R['Other']})",
     hist_formula=lambda y, c: f"SUM({c}{R['Data & Analytics']}:{c}{R['Other']})", bold=True, top=True)
line("oct", "  Octus", fc=lambda y, c: f"IF({c}$4={I['Octus close year']},{I['Octus 2026 revenue']}/{I['GBPUSD']}*(1+{I['Octus growth']})^({c}$4-2026),IF({c}$4>{I['Octus close year']},{prev(y)}{r}*(1+{I['Octus growth']}),0))")
line("tot", "Total income excl. recoveries", fc=lambda y, c: f"{c}{R['inc']}+{c}{R['oct']}",
     hist_formula=lambda y, c: f"{c}{R['inc']}", bold=True)
line("g", "  growth", fc=lambda y, c: f"{c}{R['tot']}/{prev(y)}{R['tot']}-1",
     hist_formula=lambda y, c: f"{c}{R['tot']}/{prev(y)}{R['tot']}-1" if y > YH[0] else None, fmt=PCT)
line("rec", "Recoveries", A.HIST["Recoveries"], lambda y, c: f"{prev(y)}{r}*(1+{I['Recoveries growth']})")

head("Profit & loss (adjusted)")
line("mgn", "  EBITDA margin ex-Octus", fc=lambda y, c: f"{I['EBITDA margin (ex-Octus)'][y]}+IF({c}$4>=2027,{I['margin_adj']},0)", fmt=PCT)
line("ebitda", "Adjusted EBITDA", A.HIST["Adj EBITDA"], lambda y, c: f"{c}{R['inc']}*{c}{R['mgn']}+{c}{R['oct']}*{I['Octus EBITDA margin']}", bold=True)
line("mgn_t", "  EBITDA margin", fc=lambda y, c: f"{c}{R['ebitda']}/{c}{R['tot']}",
     hist_formula=lambda y, c: f"{c}{R['ebitda']}/{c}{R['tot']}", fmt=PCT)
line("da", "Adjusted D&A", A.HIST["Adj D&A"], lambda y, c: f"{c}{R['tot']}*{I['Adj D&A % income'][y]}")
line("ebit", "Adjusted operating profit", fc=lambda y, c: f"{c}{R['ebitda']}-{c}{R['da']}",
     hist_formula=lambda y, c: f"{c}{R['ebitda']}-{c}{R['da']}", bold=True, top=True)
line("fin", "Net finance expense", A.HIST["Net finance"],
     lambda y, c: f"({prev(y)}{{debt}}-{prev(y)}{{cash}})*{I['Net finance rate']}+IF({c}$4>={I['Octus close year']},{I['Octus price']}/{I['GBPUSD']}*({I['Octus debt rate']}-{I['Net finance rate']}),0)")
line("pbt", "Adjusted profit before tax", fc=lambda y, c: f"{c}{R['ebit']}-{c}{R['fin']}",
     hist_formula=lambda y, c: f"{c}{R['ebit']}-{c}{R['fin']}")
line("tax", "Tax", fc=lambda y, c: f"{c}{R['pbt']}*{I['Tax rate']}")
line("ni", "Adjusted net income", fc=lambda y, c: f"{c}{R['pbt']}-{c}{R['tax']}")
line("nci", "  Non-controlling interests (Tradeweb)", fc=lambda y, c: f"{c}{R['ni']}*{I['NCI share of adj NI']}")
line("ni_sh", "Adjusted net income to shareholders", fc=lambda y, c: f"{c}{R['ni']}-{c}{R['nci']}", bold=True, top=True)
line("eps", "Adjusted EPS (p)", A.HIST["Adj EPS"], lambda y, c: f"{c}{R['ni_sh']}/{c}{{sh_avg}}*100", fmt=P1, bold=True)
line("eps_g", "  EPS growth", fc=lambda y, c: f"{c}{R['eps']}/{prev(y)}{R['eps']}-1",
     hist_formula=lambda y, c: f"{c}{R['eps']}/{prev(y)}{R['eps']}-1" if y > YH[0] else None, fmt=PCT)

head("Reported bridge")
line("pa_core", "  Purchased intangible amortisation (existing)", A.HIST["Purchased amortisation"],
     lambda y, c: I['Purchased amortisation 2026'] if y == YF[0] else f"{prev(y)}{r}*(1-{I['Purchased amortisation decline']})")
line("pa_oct", "  Octus purchased amortisation", fc=lambda y, c: f"IF({c}$4>={I['Octus close year']},{I['Octus purchased amortisation']},0)")
line("pa", "Total purchased amortisation", fc=lambda y, c: f"{c}{R['pa_core']}+{c}{R['pa_oct']}")
line("rep_ni", "Reported net income (total)", fc=lambda y, c: f"({c}{R['pbt']}-{c}{R['pa']})*(1-{I['Tax rate']})")
line("rep_ni_sh", "Reported net income to shareholders", fc=lambda y, c: f"{c}{R['rep_ni']}*(1-{I['NCI share of adj NI']})")

head("Cash flow")
line("cf_ebitda", "Adjusted EBITDA", fc=lambda y, c: f"{c}{R['ebitda']}")
line("capex", "Capex", A.HIST["Capex"], lambda y, c: f"{c}{R['tot']}*{I['Capex % income'][y]}")
line("cf_fin", "Net finance paid", fc=lambda y, c: f"{c}{R['fin']}")
line("cf_tax", "Tax paid", fc=lambda y, c: f"{c}{R['tax']}")
line("other", "Other cash items (leases, WC, non-underlying)", fc=lambda y, c: f"{c}{R['ebitda']}*{I['Other cash items % EBITDA']}")
line("eqfcf", "Equity free cash flow", A.HIST["Equity FCF"],
     lambda y, c: f"{c}{R['cf_ebitda']}-{c}{R['capex']}-{c}{R['cf_fin']}-{c}{R['cf_tax']}-{c}{R['other']}", bold=True, top=True)
line("acq", "Acquisitions (Octus)", fc=lambda y, c: f"IF({c}$4={I['Octus close year']},{I['Octus price']}/{I['GBPUSD']},0)")
line("debt_add", "New debt raised", fc=lambda y, c: f"{c}{R['acq']}")
line("div", "Dividends paid", fc=lambda y, c: f"{c}{{dps}}*{c}{{sh_open}}/100")
line("nci_div", "Dividends to NCI", fc=lambda y, c: f"{c}{R['nci']}*{I['NCI payout']}")
line("bb", "Share buybacks", A.HIST["Buybacks"],
     lambda y, c: f"IF(ISNUMBER({I['Buybacks (fixed)'][y]}),{I['Buybacks (fixed)'][y]},MAX(0,({c}{R['eqfcf']}-{c}{R['div']}-{c}{R['nci_div']})*{I['Buyback share of surplus FCF']}))")
line("dcash", "Net change in cash", fc=lambda y, c: f"{c}{R['eqfcf']}-{c}{R['acq']}+{c}{R['debt_add']}-{c}{R['div']}-{c}{R['nci_div']}-{c}{R['bb']}", bold=True, top=True)

head("Shares & returns")
line("sh_open", "Opening shares (m)", fc=lambda y, c: I['Opening shares'] if y == YF[0] else f"{prev(y)}{{sh_close}}", fmt="0.0")
line("px", "Average buyback price (p)", fc=lambda y, c: f"{I['Share price']}*(1+{I['Buyback price growth']})^({idx(y)}+0.5)", fmt=P0)
line("sh_close", "Closing shares (m)", fc=lambda y, c: f"{c}{R['sh_open']}-{c}{R['bb']}/{c}{R['px']}*100", fmt="0.0")
line("sh_avg", "Average shares (m)", A.HIST["WASO"], lambda y, c: f"({c}{R['sh_open']}+{c}{R['sh_close']})/2", fmt="0.0")
line("dps", "DPS (p)", A.HIST["DPS"], lambda y, c: f"{c}{R['ni_sh']}/{c}{R['sh_open']}*100*{I['Dividend payout']}", fmt=P1)

head("Balance sheet (economic; clearing balances excluded)")
OB = A.OPENING_BS
line("cash", "Cash", {2025: OB["Cash"]}, lambda y, c: f"{prev(y)}{r}+{c}{R['dcash']}")
line("intang", "Goodwill, intangibles & PP&E", {2025: OB["Goodwill & intangibles"]},
     lambda y, c: f"{prev(y)}{r}+{c}{R['capex']}+{c}{R['acq']}-{c}{R['da']}-{c}{R['pa']}")
line("othnet", "Other net assets / (liabilities)", fc=lambda y, c: f"{prev(y)}{r}+{c}{R['other']}+{c}{R['pa']}*{I['Tax rate']}",
     hist_formula=lambda y, c: None)
line("debt", "Borrowings incl. leases", {2025: OB["Borrowings incl leases"]}, lambda y, c: f"{prev(y)}{r}+{c}{R['debt_add']}")
line("equity", "Total equity (incl. NCI)", {2025: OB["Total equity"]},
     lambda y, c: f"{prev(y)}{r}+{c}{R['rep_ni']}-{c}{R['div']}-{c}{R['nci_div']}-{c}{R['bb']}")
line("check", "Balance check (should be 0)", fc=lambda y, c: f"ROUND({c}{R['cash']}+{c}{R['intang']}+{c}{R['othnet']}-{c}{R['debt']}-{c}{R['equity']},3)", bold=True)
line("nd", "Net debt", fc=lambda y, c: f"{c}{R['debt']}-{c}{R['cash']}",
     hist_formula=lambda y, c: f"{c}{R['debt']}-{c}{R['cash']}" if y == 2025 else None, top=True)
line("lev", "Net debt / adj EBITDA", fc=lambda y, c: f"{c}{R['nd']}/{c}{R['ebitda']}",
     hist_formula=lambda y, c: f"{c}{R['nd']}/{c}{R['ebitda']}" if y == 2025 else None, fmt=X)
# 2025 other net assets plug and balance check
mdl[f"D{R['othnet']}"] = f"=D{R['equity']}+D{R['debt']}-D{R['cash']}-D{R['intang']}"; mdl[f"D{R['othnet']}"].number_format = M
mdl[f"D{R['check']}"] = f"=ROUND(D{R['cash']}+D{R['intang']}+D{R['othnet']}-D{R['debt']}-D{R['equity']},3)"

head("Unlevered free cash flow (for DCF)")
line("ufcf", "Unlevered FCF", fc=lambda y, c: f"{c}{R['ebitda']}-{c}{R['capex']}-{c}{R['ebit']}*{I['Tax rate']}-{c}{R['other']}", bold=True)

# resolve forward references like {debt}
for row_ in mdl.iter_rows():
    for cell in row_:
        if isinstance(cell.value, str) and "{" in cell.value:
            cell.value = cell.value.format(**R)
# links to Inputs in green
for row_ in mdl.iter_rows(min_row=6):
    for cell in row_[2:]:
        if isinstance(cell.value, str) and cell.value.startswith("=") and "Inputs!" in cell.value and "+" not in cell.value and "*" not in cell.value:
            cell.font = GREEN
mdl.column_dimensions["A"].width = 50
for c in COLS.values(): mdl.column_dimensions[c].width = 11
mdl.freeze_panes = "C6"

# ---------------- DCF ----------------
dcf["A1"] = "LSEG – DCF (valuation date 31 Dec 2026, mid-year convention)"; dcf["A1"].font = Font(bold=True, size=14)
rows = [("Cost of equity", f"={I['Risk-free rate']}+{I['Beta']}*{I['Equity risk premium']}", PCT),
        ("After-tax cost of debt", f"={I['Pre-tax cost of debt']}*(1-{I['Tax rate']})", PCT),
        ("WACC", f"=(1-{I['Debt weight']})*B3+{I['Debt weight']}*B4", PCT),
        ("Terminal growth", f"={I['tv_growth']}", PCT)]
for i, (lab, f, fmt) in enumerate(rows, start=3):
    dcf[f"A{i}"], dcf[f"B{i}"] = lab, f; dcf[f"B{i}"].number_format = fmt
dcf["B5"].font = BOLD
DY = [y for y in YF if y > 2026]
dcf["A8"] = "Year"
for j, y in enumerate(DY):
    c = L(2 + j); mc = COLS[y]
    dcf[f"{c}8"] = y; dcf[f"{c}8"].font = HDRF; dcf[f"{c}8"].fill = HDR
    dcf[f"{c}9"] = j + 1
    dcf[f"{c}10"] = f"=Model!{mc}{R['ufcf']}"; dcf[f"{c}10"].font = GREEN; dcf[f"{c}10"].number_format = M
    dcf[f"{c}11"] = f"=1/(1+$B$5)^({c}9-0.5)"; dcf[f"{c}11"].number_format = "0.000"
    dcf[f"{c}12"] = f"={c}10*{c}11"; dcf[f"{c}12"].number_format = M
dcf["A8"].fill = HDR; dcf["A8"].font = HDRF
dcf["A9"], dcf["A10"], dcf["A11"], dcf["A12"] = "Period", "Unlevered FCF", "Discount factor", "PV of FCF"
lc = L(1 + len(DY)); lm = COLS[DY[-1]]
val = [("Sum of PV of FCF", f"=SUM(B12:{lc}12)", M),
       ("Terminal value (Gordon)", f"={lc}10*(1+B6)/(B5-B6)", M),
       ("PV of terminal value", f"=B16/(1+B5)^({lc}9-0.5)", M),
       ("Enterprise value", "=B15+B17", M),
       ("Less: net debt (end-2026)", f"=-Model!{COLS[2026]}{R['nd']}", M),
       ("Less: NCI (Tradeweb minority) at P/E", f"=-Model!{COLS[2027]}{R['nci']}*{I['NCI multiple']}", M),
       ("Equity value", "=B18+B19+B20", M),
       ("Shares (end-2026, m)", f"=Model!{COLS[2026]}{R['sh_close']}", "0.0"),
       ("Fair value per share (p)", "=B21/B22*100", P0),
       ("Current share price (p)", f"={I['Share price']}", P0),
       ("Upside / (downside)", "=B23/B24-1", PCT),
       ("TV as % of EV", "=B17/B18", PCT),
       ("Implied TV / 2030E EBITDA", f"=B16/Model!{lm}{R['ebitda']}", X),
       ("Implied 2027E P/E at current price", f"=B24/Model!{COLS[2027]}{R['eps']}", X)]
for i, (lab, f, fmt) in enumerate(val, start=15):
    dcf[f"A{i}"], dcf[f"B{i}"] = lab, f; dcf[f"B{i}"].number_format = fmt
for i in (18, 21, 23, 25): dcf[f"A{i}"].font = BOLD; dcf[f"B{i}"].font = BOLD
# live sensitivity: fair value (p) for WACC x terminal growth
dcf["D14"] = "Fair value (p): WACC (down) × terminal growth (across)"; dcf["D14"].font = BOLD
gs = [0.020, 0.025, 0.030, 0.035, 0.040]; ws = [0.0734, 0.0784, 0.0834, 0.0884, 0.0934]
for j, g in enumerate(gs):
    dcf[f"{L(5+j)}15"] = g; dcf[f"{L(5+j)}15"].number_format = PCT; dcf[f"{L(5+j)}15"].font = BLUE
for i, w in enumerate(ws):
    rr = 16 + i; dcf[f"D{rr}"] = w; dcf[f"D{rr}"].number_format = '0.00%'; dcf[f"D{rr}"].font = BLUE
    for j in range(len(gs)):
        gc = f"{L(5+j)}$15"; wc = f"$D{rr}"
        pvf = f"SUMPRODUCT($B$10:${lc}$10/(1+{wc})^($B$9:${lc}$9-0.5))"
        tv = f"${lc}$10*(1+{gc})/({wc}-{gc})/(1+{wc})^(${lc}$9-0.5)"
        dcf[f"{L(5+j)}{rr}"] = f"=({pvf}+{tv}+$B$19+$B$20)/$B$22*100"
        dcf[f"{L(5+j)}{rr}"].number_format = P0
dcf.column_dimensions["A"].width = 40; dcf.column_dimensions["B"].width = 12; dcf.column_dimensions["D"].width = 12

# ---------------- Scenarios (snapshot from Python engine) ----------------
res = {s: run(s) for s in (1, 2, 3)}
probs = {1: 0.25, 2: 0.50, 3: 0.25}
scn["A1"] = "LSEG – Scenario outputs"; scn["A1"].font = Font(bold=True, size=14)
scn["A2"] = "Snapshot computed by the Python engine (lseg/engine.py). To reproduce live, set Inputs!Scenario to 1/2/3."
hdr = ["", "Bear", "Base", "Bull"]
for j, h in enumerate(hdr): scn.cell(4, 1 + j, h).font = HDRF; scn.cell(4, 1 + j).fill = HDR
lines = [("Probability", lambda s: probs[s], PCT),
         ("Income growth adj. (pp)", lambda s: A.SCEN["growth_adj"][s], PCT),
         ("EBITDA margin adj.", lambda s: A.SCEN["margin_adj"][s], PCT),
         ("Terminal growth", lambda s: A.SCEN["tv_growth"][s], PCT),
         ("2028E total income", lambda s: res[s]["r"]["tot"][2028], M),
         ("2028E EBITDA margin", lambda s: res[s]["r"]["ebitda"][2028] / res[s]["r"]["tot"][2028], PCT),
         ("2028E adj EPS (p)", lambda s: res[s]["r"]["eps"][2028], P1),
         ("Fair value (p)", lambda s: res[s]["fair_value"], P0),
         ("Upside / (downside)", lambda s: res[s]["upside"], PCT)]
for i, (lab, fn, fmt) in enumerate(lines, start=5):
    scn.cell(i, 1, lab)
    for j, s in enumerate((1, 2, 3)):
        c = scn.cell(i, 2 + j, fn(s)); c.number_format = fmt
scn["A15"] = "Probability-weighted fair value (p)"; scn["A15"].font = BOLD
scn["B15"] = "=SUMPRODUCT(B5:D5,B12:D12)"; scn["B15"].number_format = P0; scn["B15"].font = BOLD
scn["A16"] = "Probability-weighted upside"; scn["B16"] = f"=B15/{I['Share price']}-1"; scn["B16"].number_format = PCT
scn["A18"] = "Bear: AI substitutes for terminal/workflow seats → D&A growth stalls; Markets volumes normalise; margin gains reverse."
scn["A19"] = "Bull: AI-ready data licensing (LSEG Everywhere, MCP) re-accelerates D&A; Octus + Markets compound; margin expansion continues."
scn.column_dimensions["A"].width = 40

# ---------------- Comps ----------------
cmp_ = wb.create_sheet("Comps", 4)
cmp_["A1"] = "LSEG – Trading comparables"; cmp_["A1"].font = Font(bold=True, size=14)
cmp_["A2"] = A.COMPS_DATE + ". Forward P/E is the primary metric (consistent consensus basis); EV/EBITDA is trailing, provider-defined."
hd = ["Company", "Ticker", "Peer group", "Ccy", "Mkt cap (bn)", "EV (bn)", "Fwd P/E", "EV/EBITDA TTM", "EBITDA margin"]
for j, h in enumerate(hd, start=1):
    c = cmp_.cell(4, j, h); c.font = HDRF; c.fill = HDR
fmts = [None, None, None, None, '0.0', '0.0', X, X, PCT]
for i, rowv in enumerate(A.COMPS, start=5):
    for j, v in enumerate(rowv, start=1):
        c = cmp_.cell(i, j, v)
        if j >= 5: c.font = BLUE; c.number_format = fmts[j - 1]
last = 4 + len(A.COMPS)
rng = lambda col: f"{col}5:{col}{last}"
stats = [("Median – all peers", "MEDIAN"), ("Mean – all peers", "AVERAGE"), ("Max", "MAX"), ("Min", "MIN")]
r0 = last + 2
for k, (lab, fn) in enumerate(stats):
    cmp_.cell(r0 + k, 1, lab).font = BOLD
    for col in "GHI":
        c = cmp_[f"{col}{r0+k}"]; c.value = f"={fn}({rng(col)})"; c.number_format = PCT if col == "I" else X
g = r0 + len(stats)
for k, grp in enumerate(["Data & analytics", "Exchanges & infrastructure"]):
    cmp_.cell(g + k, 1, f"Median – {grp}").font = BOLD
    for col in "GH":
        # MEDIAN(IF()) array formula
        rows_g = [i for i, rv in enumerate(A.COMPS, start=5) if rv[2] == grp]
        cmp_[f"{col}{g+k}"] = f"=MEDIAN({col}{min(rows_g)}:{col}{max(rows_g)})"   # peers listed grouped
        cmp_[f"{col}{g+k}"].number_format = X
lr = g + 3
L_ = A.LSEG_SAME_SOURCE
cmp_.cell(lr, 1, "LSEG (same source)").font = BOLD
for col, v, f in [("E", L_["mkt_cap"], '0.0'), ("F", L_["ev"], '0.0'), ("G", L_["fwd_pe"], X), ("H", L_["ev_ebitda"], X)]:
    c = cmp_[f"{col}{lr}"]; c.value = v; c.font = BLUE; c.number_format = f
cmp_.cell(lr, 4, "GBP")
cmp_.cell(lr + 1, 1, "LSEG discount to peer median (fwd P/E)")
cmp_[f"G{lr+1}"] = f"=G{lr}/G{r0}-1"; cmp_[f"G{lr+1}"].number_format = PCT
cmp_.cell(lr + 3, 1, "Implied LSEG value per share (p)").font = BOLD
cmp_.cell(lr + 4, 1, "  LSEG price on same source (p)"); cmp_[f"B{lr+4}"] = L_["price"]; cmp_[f"B{lr+4}"].font = BLUE; cmp_[f"B{lr+4}"].number_format = P0
impl = [("  at all-peer median fwd P/E", f"=B{lr+4}*G{r0}/G{lr}"),
        ("  at data & analytics median", f"=B{lr+4}*G{g}/G{lr}"),
        ("  at exchanges median", f"=B{lr+4}*G{g+1}/G{lr}"),
        ("  at peer minimum (bear cross-check)", f"=B{lr+4}*G{r0+3}/G{lr}")]
for k, (lab, f) in enumerate(impl):
    cmp_.cell(lr + 5 + k, 1, lab); cmp_[f"B{lr+5+k}"] = f; cmp_[f"B{lr+5+k}"].number_format = P0
cmp_.cell(lr + 10, 1, "Read: LSEG trades at a discount to both data and exchange peers, closest to FactSet – the market is pricing it as an AI-exposed terminal business, although c.half of income is Markets, FTSE Russell and Risk Intelligence.")
cmp_.column_dimensions["A"].width = 40; cmp_.column_dimensions["C"].width = 26
for col in "EFGHI": cmp_.column_dimensions[col].width = 13

# ---------------- Model vs consensus ----------------
cs = wb.create_sheet("vs Consensus", 5)
cs["A1"] = "LSEG – Model vs company-compiled consensus"; cs["A1"].font = Font(bold=True, size=14)
cs["A2"] = "Consensus: LSEG IR, compiled 13 Oct 2026 (12 analysts) – before the Octus deal and Q3 guidance upgrade. Model figures are live links."
CY = [2026, 2027, 2028]
hdr = ["Line"] + [f"Model {y}" for y in CY] + [f"Cons {y}" for y in CY] + [f"Diff {y}" for y in CY]
for j, h in enumerate(hdr, start=1):
    c = cs.cell(4, j, h); c.font = HDRF; c.fill = HDR
mp = [("Data & Analytics", "Data & Analytics", M), ("FTSE Russell", "FTSE Russell", M),
      ("Risk Intelligence", "Risk Intelligence", M), ("Markets", "Markets", M),
      ("Total income excl. recoveries", "tot", M), ("Adjusted EBITDA", "ebitda", M),
      ("Adjusted EPS (p)", "eps", P1), ("DPS (p)", "dps", P1)]
for i, (lab, key, fmt) in enumerate(mp, start=5):
    cs.cell(i, 1, lab)
    for j, y in enumerate(CY):
        m_ = cs.cell(i, 2 + j, f"=Model!{COLS[y]}{R[key]}"); m_.font = GREEN; m_.number_format = fmt
        c_ = cs.cell(i, 5 + j, A.CONSENSUS[lab][y]); c_.font = BLUE; c_.number_format = fmt
        d_ = cs.cell(i, 8 + j, f"={L(2+j)}{i}/{L(5+j)}{i}-1"); d_.number_format = PCT
cs["A14"] = "Read: model sits close to consensus on income and EBITDA; EPS a little above (lower NCI drag, buyback timing). The variant view is in the multiple, not the numbers."
cs.column_dimensions["A"].width = 32
for k in range(2, 11): cs.column_dimensions[L(k)].width = 11

# ---------------- Sources & Cover ----------------
src["A1"] = "Sources"; src["A1"].font = Font(bold=True, size=14)
for i, (k, v) in enumerate(A.SOURCES.items(), start=3): src[f"A{i}"], src[f"B{i}"] = k, v
src["A10"] = "Model conventions: blue = input, black = formula, green = link to another sheet. Not investment advice."
src.column_dimensions["B"].width = 90
cover["A1"] = "London Stock Exchange Group plc (LSEG.L)"; cover["A1"].font = Font(bold=True, size=16)
cover["A2"] = "Long/short equity pitch kit – integrated three-statement model, DCF and scenarios"
cover["A3"] = "Prepared by Tobenna Agubuche | github.com/Tobenna30/finance-models | Not investment advice"
items = [("Scenario selected", f"=CHOOSE({I['Scenario']},\"Bear\",\"Base\",\"Bull\")", None),
         ("Share price (p)", f"={I['Share price']}", P0),
         ("DCF fair value (p)", "=DCF!B23", P0),
         ("Upside / (downside)", "=DCF!B25", PCT),
         ("Probability-weighted fair value (p)", "=Scenarios!B15", P0),
         ("2026E adj EPS (p)", f"=Model!{COLS[2026]}{R['eps']}", P1),
         ("2027E P/E", "=DCF!B28", X),
         ("Net debt / EBITDA 2027E", f"=Model!{COLS[2027]}{R['lev']}", X),
         ("Peer median fwd P/E", f"=Comps!G{r0}", X),
         ("Implied value at peer median (p)", f"=Comps!B{lr+5}", P0),
         ("Balance sheet checks (sum, should be 0)", f"=SUM(Model!{COLS[2025]}{R['check']}:Model!{COLS[2030]}{R['check']})", '0.000')]
for i, (lab, f, fmt) in enumerate(items, start=5):
    cover[f"A{i}"], cover[f"B{i}"] = lab, f; cover[f"B{i}"].font = GREEN
    if fmt: cover[f"B{i}"].number_format = fmt
cover.column_dimensions["A"].width = 42; cover.column_dimensions["B"].width = 14

OUT.parent.mkdir(parents=True, exist_ok=True)
wb.save(OUT)
print("saved", OUT, "rows", R["ufcf"])
