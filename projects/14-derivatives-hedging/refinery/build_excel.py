"""Build the live refinery hedge workbook. Every pricing, scenario and FX cell is a formula pointing back to Inputs.
Run from projects/14-derivatives-hedging: python -m refinery.build_excel
Then recalculate with LibreOffice: python -m refinery.recalc"""
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter as CL
from . import assumptions as A, engine as E

BOLD = Font(bold=True)
HDR, HDRF = PatternFill("solid", fgColor="1F3864"), Font(bold=True, color="FFFFFF")
SEC = PatternFill("solid", fgColor="D9E1F2")
M1, PCT, USD, N0, DT = '#,##0.0;(#,##0.0);"-"', '0.0%;(0.0%);"-"', '$0.00;($0.00)', '#,##0', "dd mmm yyyy"
RAW = Path(__file__).resolve().parents[1] / "models" / "_raw_Refinery_Hedge.xlsx"
OUT = Path(__file__).resolve().parents[1] / "models" / "Refinery_Hedge.xlsx"

wb = Workbook()
cover = wb.active; cover.title = "Cover"
S = {n: wb.create_sheet(n) for n in ["Inputs", "Pricing", "Monthly", "Scenarios", "FX", "Sources"]}


def title(ws, t, sub=None):
    ws["A1"] = t; ws["A1"].font = Font(bold=True, size=14)
    if sub: ws["A2"] = sub


def hdr(ws, r, c, v):
    x = ws.cell(r, c, v); x.fill = HDR; x.font = HDRF; return x


def put(ws, ref, v, fmt=None, bold=False):
    c = ws[ref]; c.value = v
    if isinstance(v, str) and v.startswith("="):
        c.font = Font(color="008000", bold=bold) if "!" in v else Font(bold=bold)
    elif isinstance(v, (int, float)) or hasattr(v, "year"):
        c.font = Font(color="0000FF", bold=bold)
    elif bold:
        c.font = BOLD
    if fmt: c.number_format = fmt
    return c


# =============================================================== Inputs
inp = S["Inputs"]; I = {}
title(inp, "Inputs", "Blue = hard-coded input. Tag: S = sourced, A = assumption, D = derived. Cracks in $/bbl.")
for j, h in enumerate(["Input", "Unit", "Value", "Tag", "Source / note"], start=1): hdr(inp, 4, j, h)
row = 5


def section(t):
    global row
    row += 1; inp[f"A{row}"] = t; inp[f"A{row}"].font = BOLD
    for c in range(1, 6): inp.cell(row, c).fill = SEC
    row += 1


def scalar(key, label, val, unit, tag, note="", fmt=None):
    global row
    inp[f"A{row}"], inp[f"B{row}"], inp[f"D{row}"], inp[f"E{row}"] = label, unit, tag, note
    put(inp, f"C{row}", val, fmt); I[key] = f"Inputs!$C${row}"; row += 1


section("Market (build date 27 Oct 2026)")
scalar("val", "Valuation date", A.VALUATION_DATE, "date", "A", "Build date", DT)
scalar("F_diesel", "2027 forward crack, diesel and jet", A.FORWARD["diesel"], "$/bbl", "S", "GS: 2027 average above $40. Spot NYH ULSD crack $%.2f (D)" % A.SPOT["diesel_crack"], USD)
scalar("F_petrol", "2027 forward crack, petrol", A.FORWARD["petrol"], "$/bbl", "D", "Trailing 12-month NYH gasoline crack vs Brent (FRED DGASNYH, DCOILBRENTEU)", USD)
scalar("vol_diesel", "Normal vol, diesel crack", A.NORMAL_VOL["diesel"], "$/bbl/yr", "D", "Month-average crack changes, Oct 2025 to Oct 2026, x sqrt(12)", USD)
scalar("vol_petrol", "Normal vol, petrol crack", A.NORMAL_VOL["petrol"], "$/bbl/yr", "D", "Month-average crack changes, Oct 2025 to Oct 2026, x sqrt(12)", USD)
scalar("r_usd", "USD discount rate", A.USD_RATE, "%", "S", "Fed funds effective, 23 Oct 2026 (FRED DFF)", PCT)
scalar("r_zar", "ZAR rate", A.ZAR_RATE, "%", "S", "SARB repo after 23 Sep 2026 hike (eNCA, secondary)", PCT)
scalar("spot", "USD/ZAR spot", A.USDZAR_SPOT, "ZAR per $", "S", "Close 26 Oct 2026 (Alpha Vantage)", "0.0000")
section("Refinery (illustrative)")
scalar("cap", "Crude capacity", A.CAPACITY_BPD, "bbl/day", "A", "Illustrative coastal South African refinery", N0)
scalar("avail", "Expected availability", A.AVAILABILITY, "%", "A", "On-stream factor after planned maintenance", PCT)
scalar("y_diesel", "Yield, diesel and jet", A.YIELD["diesel"], "%", "A", "Share of crude run", PCT)
scalar("y_petrol", "Yield, petrol", A.YIELD["petrol"], "%", "A", "Other 20% (LPG, fuel oil) taken at zero crack", PCT)
scalar("opex", "Cash opex", A.OPEX_ZAR_PER_BBL, "ZAR/bbl", "A", "About $6/bbl at spot", N0)
section("Hedge design")
scalar("putd", "Put distance below forward", A.PUT_DISTANCE, "%", "A", "Buy a put 5% below the forward crack", PCT)
scalar("appetite", "Outage risk appetite", A.OUTAGE_APPETITE, "% of margin", "A", "Max cost of unbacked sold calls in one outage", PCT)
scalar("odays", "Outage length", A.OUTAGE_DAYS, "days", "A", "Six-week unplanned outage", N0)
scalar("ostart", "Outage start", A.OUTAGE_START, "date", "A", "Settled month by month", DT)
scalar("spike", "Crack spike during outage", A.OUTAGE_SPIKE, "%", "A", "Cracks often rise when a refinery trips", PCT)
section("Selected case for the Monthly sheet")
scalar("cover", "Hedge cover", 0.8, "%", "A", "Change to test other ratios", PCT)
scalar("shock", "Parallel crack move", A.OUTAGE_SPIKE, "%", "A", "Applies to both products for all of 2027", PCT)
scalar("outage", "Outage on (1) or off (0)", 1, "flag", "A", "", N0)
inp.column_dimensions["A"].width = 38; inp.column_dimensions["E"].width = 80
for c in "BCD": inp.column_dimensions[c].width = 13

# =============================================================== Pricing
pr = S["Pricing"]
title(pr, "Collar pricing by settlement month",
      "Bachelier (normal) prices the collar. Black-76 is a cross-check: its zero-cost call strike is solved in engine.py and the check column proves zero premium.")
heads = ["Month", "Month end", "t (yrs)"]
blk = ["Forward", "Put strike", "Call strike", "sigma*sqrt(t)", "Put prem", "Call prem", "Net prem",
       "B76 call strike", "B76 vol", "B76 put prem", "B76 call prem", "B76 net prem"]
for p in A.PRODUCTS: heads += [f"{A.PRODUCT_LABEL[p]}: {h}" for h in blk]
for j, h in enumerate(heads, start=1): hdr(pr, 4, j, h)
KB = E.strikes("black76"); PC = {}
for i, (m, n, _) in enumerate(E.months()):
    r = 5 + i
    put(pr, f"A{r}", m); pr[f"A{r}"].font = Font()
    put(pr, f"B{r}", f"=DATE({A.HEDGE_YEAR},A{r}+1,1)-1", DT)
    put(pr, f"C{r}", f"=(B{r}-{I['val']})/365", "0.000")
    for k, p in enumerate(A.PRODUCTS):
        c0 = 4 + k * len(blk); col = {h: CL(c0 + j) for j, h in enumerate(blk)}
        PC[p] = col
        F, Kp, Kc, s = (f"{col[h]}{r}" for h in ("Forward", "Put strike", "Call strike", "sigma*sqrt(t)"))
        df = f"EXP(-{I['r_usd']}*C{r})"
        put(pr, F, f"={I['F_' + p]}", USD)
        put(pr, Kp, f"={F}*(1-{I['putd']})", USD)
        put(pr, Kc, f"=2*{F}-{Kp}", USD)                    # Bachelier is symmetric, so the zero-cost call mirrors the put
        put(pr, s, f"={I['vol_' + p]}*SQRT(C{r})", USD)
        put(pr, f"{col['Put prem']}{r}", f"={df}*(({Kp}-{F})*_xlfn.NORM.S.DIST(({Kp}-{F})/{s},TRUE)+{s}*_xlfn.NORM.S.DIST(({Kp}-{F})/{s},FALSE))", "0.0000")
        put(pr, f"{col['Call prem']}{r}", f"={df}*(({F}-{Kc})*_xlfn.NORM.S.DIST(({F}-{Kc})/{s},TRUE)+{s}*_xlfn.NORM.S.DIST(({F}-{Kc})/{s},FALSE))", "0.0000")
        put(pr, f"{col['Net prem']}{r}", f"={col['Put prem']}{r}-{col['Call prem']}{r}", "0.0000")
        kb, vb = f"{col['B76 call strike']}{r}", f"{col['B76 vol']}{r}"
        put(pr, kb, round(KB[p][i]["call"], 6), USD)
        put(pr, vb, f"={I['vol_' + p]}/{F}", PCT)
        d1 = lambda K: f"((LN({F}/{K})+{vb}^2*C{r}/2)/({vb}*SQRT(C{r})))"
        d2 = lambda K: f"({d1(K)}-{vb}*SQRT(C{r}))"
        put(pr, f"{col['B76 put prem']}{r}", f"={df}*({Kp}*_xlfn.NORM.S.DIST(-{d2(Kp)},TRUE)-{F}*_xlfn.NORM.S.DIST(-{d1(Kp)},TRUE))", "0.0000")
        put(pr, f"{col['B76 call prem']}{r}", f"={df}*({F}*_xlfn.NORM.S.DIST({d1(kb)},TRUE)-{kb}*_xlfn.NORM.S.DIST({d2(kb)},TRUE))", "0.0000")
        put(pr, f"{col['B76 net prem']}{r}", f"={col['B76 put prem']}{r}-{col['B76 call prem']}{r}", "0.0000")
for j in range(1, len(heads) + 1): pr.column_dimensions[CL(j)].width = 13
P = {p: {h: f"Pricing!${PC[p][h]}$5" for h in ("Put strike", "Call strike")} for p in A.PRODUCTS}

# =============================================================== Monthly (selected case)
mo = S["Monthly"]
title(mo, "2027 month by month, selected case",
      "Hedged barrels are fixed on budget volumes. During an outage the sold calls have no barrels behind them. $ unless stated.")
mh = ["Month", "Days", "Outage days"]
pb = ["Budget bbl", "Run bbl", "Hedged bbl", "Crack", "Payoff /bbl", "Physical $", "Hedge $", "Unbacked call $"]
for p in A.PRODUCTS: mh += [f"{A.PRODUCT_LABEL[p]}: {h}" for h in pb]
mh += ["Budget margin $", "Actual margin $"]
for j, h in enumerate(mh, start=1): hdr(mo, 4, j, h)
for i in range(12):
    r = 5 + i
    put(mo, f"A{r}", f"=Pricing!A{r}"); put(mo, f"B{r}", f"=DAY(Pricing!B{r})", N0)
    ms, me = f"DATE({A.HEDGE_YEAR},A{r},1)", f"Pricing!B{r}"
    oe = f"({I['ostart']}+{I['odays']}-1)"
    put(mo, f"C{r}", f"={I['outage']}*MAX(0,MIN({me},{oe})-MAX({ms},{I['ostart']})+1)", N0)
    for k, p in enumerate(A.PRODUCTS):
        c0 = 4 + k * len(pb); col = {h: CL(c0 + j) for j, h in enumerate(pb)}
        daily = f"{I['cap']}*{I['avail']}*{I['y_' + p]}"
        put(mo, f"{col['Budget bbl']}{r}", f"={daily}*B{r}", N0)
        put(mo, f"{col['Run bbl']}{r}", f"={daily}*(B{r}-C{r})", N0)
        put(mo, f"{col['Hedged bbl']}{r}", f"={I['cover']}*{col['Budget bbl']}{r}", N0)
        put(mo, f"{col['Crack']}{r}", f"={I['F_' + p]}*(1+{I['shock']})", USD)
        x = f"{col['Crack']}{r}"
        put(mo, f"{col['Payoff /bbl']}{r}", f"=MAX({P[p]['Put strike']}-{x},0)-MAX({x}-{P[p]['Call strike']},0)", USD)
        put(mo, f"{col['Physical $']}{r}", f"={col['Run bbl']}{r}*{x}", N0)
        put(mo, f"{col['Hedge $']}{r}", f"={col['Hedged bbl']}{r}*{col['Payoff /bbl']}{r}", N0)
        put(mo, f"{col['Unbacked call $']}{r}", f"={I['cover']}*{daily}*C{r}*MIN({col['Payoff /bbl']}{r},0)", N0)
        PC.setdefault("mo", {})[p] = col
    bud = "+".join(f"{PC['mo'][p]['Budget bbl']}{r}*{I['F_' + p]}" for p in A.PRODUCTS)
    act = "+".join(f"{PC['mo'][p]['Physical $']}{r}+{PC['mo'][p]['Hedge $']}{r}" for p in A.PRODUCTS)
    nb = len(mh)
    put(mo, f"{CL(nb - 1)}{r}", f"={bud}", N0); put(mo, f"{CL(nb)}{r}", f"={act}", N0)
r = 17; put(mo, f"A{r}", "Total", bold=True)
for j in range(2, len(mh) + 1):
    if "Crack" in mh[j - 1] or "Payoff" in mh[j - 1]: continue
    put(mo, f"{CL(j)}{r}", f"=SUM({CL(j)}5:{CL(j)}16)", N0, bold=True)
nb = len(mh); BUD, ACT = f"{CL(nb - 1)}17", f"{CL(nb)}17"
unb = "+".join(f"{PC['mo'][p]['Unbacked call $']}17" for p in A.PRODUCTS)
put(mo, "A19", "Margin change vs budget", bold=True); put(mo, "C19", f"={ACT}/{BUD}-1", PCT, bold=True)
put(mo, "A20", "Unbacked call cost / budget margin", bold=True); put(mo, "C20", f"=-({unb})/{BUD}", PCT, bold=True)
for j in range(1, nb + 1): mo.column_dimensions[CL(j)].width = 14

# =============================================================== Scenarios
sc = S["Scenarios"]
title(sc, "Hedge ratio scenarios", "Refining margin change vs budget for a parallel 2027 crack move. Uses January strikes (Bachelier strikes are the same in every month).")
put(sc, "A4", "Margin weight, diesel and jet", bold=True)
put(sc, "C4", f"={I['y_diesel']}*{I['F_diesel']}/({I['y_diesel']}*{I['F_diesel']}+{I['y_petrol']}*{I['F_petrol']})", PCT)
put(sc, "A5", "Margin weight, petrol", bold=True); put(sc, "C5", "=1-C4", PCT)
W = {"diesel": "$C$4", "petrol": "$C$5"}


def hedge_pct(cov, s):
    """Collar payoff as a share of budget margin for a crack move s."""
    parts = []
    for p in A.PRODUCTS:
        f = I["F_" + p]; x = f"{f}*(1+{s})"
        parts.append(f"{W[p]}*(MAX({P[p]['Put strike']}-{x},0)-MAX({x}-{P[p]['Call strike']},0))/{f}")
    return f"{cov}*(" + "+".join(parts) + ")"


hdr(sc, 7, 1, "Cover \\ crack move")
for j, s in enumerate(A.SHOCKS): put(sc, f"{CL(2 + j)}7", s, PCT); sc[f"{CL(2 + j)}7"].fill = HDR; sc[f"{CL(2 + j)}7"].font = HDRF
for i, c in enumerate([0.0] + A.COVERS):
    r = 8 + i; put(sc, f"A{r}", c, PCT)
    for j in range(len(A.SHOCKS)):
        s = f"{CL(2 + j)}$7"
        put(sc, f"{CL(2 + j)}{r}", f"={s}+{hedge_pct(f'$A{r}', s)}", PCT)
r0 = 15
for j, h in enumerate(["Cover", "30% fall", "Outage: unbacked call cost", "Outage + spike: total change", "Within appetite"], start=1): hdr(sc, r0, j, h)
for i, c in enumerate(A.COVERS):
    r = r0 + 1 + i; put(sc, f"A{r}", c, PCT)
    put(sc, f"B{r}", f"=-0.3+{hedge_pct(f'$A{r}', '-0.3')}", PCT)
    lost = f"{I['odays']}/365"
    unb = "+".join(f"{W[p]}*MIN(MAX({P[p]['Put strike']}-{I['F_' + p]}*(1+{I['spike']}),0)-MAX({I['F_' + p]}*(1+{I['spike']})-{P[p]['Call strike']},0),0)/{I['F_' + p]}" for p in A.PRODUCTS)
    put(sc, f"C{r}", f"=-$A{r}*{lost}*({unb})", PCT)
    put(sc, f"D{r}", f"=(1+{I['spike']})*(1-{lost})+{hedge_pct(f'$A{r}', I['spike'])}-1", PCT)
    put(sc, f"E{r}", f"=IF(C{r}<={I['appetite']},1,0)", N0)
rl = r0 + len(A.COVERS)
put(sc, f"A{rl + 2}", "Recommended cover (most protection within appetite)", bold=True)
put(sc, f"D{rl + 2}", f"=_xlfn.MAXIFS(A{r0 + 1}:A{rl},E{r0 + 1}:E{rl},1)", PCT, bold=True)
REC = f"Scenarios!$D${rl + 2}"
sc.column_dimensions["A"].width = 30
for c in "BCDEF": sc.column_dimensions[c].width = 18

# =============================================================== FX
fx = S["FX"]
title(fx, "ZAR overlay: sell USD forward against the rand cost budget",
      "The refinery earns dollars and pays rand costs. Selling dollars forward locks the rand value of the cost budget. ZAR millions.")
fh = ["Month", "t (yrs)", "USD/ZAR forward", "USD margin $m", "Rand cost Rm", "USD sold $m"]
for sh in A.FX_SHOCKS: fh += [f"Unhedged {sh:+.0%}", f"Hedged {sh:+.0%}"]
for j, h in enumerate(fh, start=1): hdr(fx, 4, j, h)
for i in range(12):
    r = 5 + i
    put(fx, f"A{r}", f"=Pricing!A{r}"); put(fx, f"B{r}", f"=Pricing!C{r}", "0.000")
    put(fx, f"C{r}", f"={I['spot']}*((1+{I['r_zar']})/(1+{I['r_usd']}))^B{r}", "0.0000")
    put(fx, f"D{r}", "=(" + "+".join(f"Monthly!{PC['mo'][p]['Budget bbl']}{r}*{I['F_' + p]}" for p in A.PRODUCTS) + ")/1e6", M1)
    put(fx, f"E{r}", f"={I['cap']}*{I['avail']}*Monthly!B{r}*{I['opex']}/1e6", M1)
    put(fx, f"F{r}", f"=E{r}/C{r}", M1)
    for k, sh in enumerate(A.FX_SHOCKS):
        cu, ch = CL(7 + 2 * k), CL(8 + 2 * k); spot = f"C{r}*(1+{sh})"
        put(fx, f"{cu}{r}", f"=D{r}*{spot}-E{r}", M1)
        put(fx, f"{ch}{r}", f"=(D{r}-F{r})*{spot}+F{r}*C{r}-E{r}", M1)
put(fx, "A17", "Total", bold=True)
for j in range(4, len(fh) + 1): put(fx, f"{CL(j)}17", f"=SUM({CL(j)}5:{CL(j)}16)", M1, bold=True)
for j in range(1, len(fh) + 1): fx.column_dimensions[CL(j)].width = 15

# =============================================================== Sources
so = S["Sources"]; title(so, "Sources", "Read 27 Oct 2026. Secondary sources are labelled and used as cross-checks or where no primary source was found.")
for j, h in enumerate(["Key", "Source", "URL"], start=1): hdr(so, 4, j, h)
for i, (k, (d, u)) in enumerate(A.SOURCES.items()):
    so[f"A{5 + i}"], so[f"B{5 + i}"], so[f"C{5 + i}"] = k, d, u
so.column_dimensions["B"].width = 110; so.column_dimensions["C"].width = 90

# =============================================================== Cover
title(cover, "Refinery margin hedge: 2027 zero-cost crack collars",
      "Illustrative South African refinery. Bachelier pricing, Black-76 cross-check. Not a real asset, not executable quotes.")
for j, h in enumerate(["Output", "Value", "Cell"], start=1): hdr(cover, 4, j, h)
rec_row = lambda col: f"INDEX(Scenarios!{col}{r0 + 1}:{col}{rl},MATCH({REC},Scenarios!A{r0 + 1}:A{rl},0))"
outs = [
    ("Annual budget refining margin ($m)", f"=Monthly!{BUD}/1e6", M1),
    ("Recommended cover", f"={REC}", PCT),
    ("30% fall, recommended cover", f"={rec_row('B')}", PCT),
    ("30% fall, unhedged", "=Scenarios!B8", PCT),
    ("Outage cost on unbacked calls, recommended cover", f"={rec_row('C')}", PCT),
    ("Outage + spike total change, recommended cover", f"={rec_row('D')}", PCT),
    ("Diesel put strike ($/bbl)", f"={P['diesel']['Put strike']}", USD),
    ("Diesel call strike, Bachelier ($/bbl)", f"={P['diesel']['Call strike']}", USD),
    ("Diesel call strike Dec, Black-76 ($/bbl)", f"=Pricing!{PC['diesel']['B76 call strike']}16", USD),
    ("Selected case: margin change", "=Monthly!C19", PCT),
    ("Selected case: unbacked call cost", "=Monthly!C20", PCT),
    ("Max abs Bachelier net premium ($/bbl)", "=MAX(" + ",".join(f"MAX(Pricing!{PC[p]['Net prem']}5:{PC[p]['Net prem']}16),-MIN(Pricing!{PC[p]['Net prem']}5:{PC[p]['Net prem']}16)" for p in A.PRODUCTS) + ")", "0.000000"),
    ("Max abs Black-76 net premium ($/bbl)", "=MAX(" + ",".join(f"MAX(Pricing!{PC[p]['B76 net prem']}5:{PC[p]['B76 net prem']}16),-MIN(Pricing!{PC[p]['B76 net prem']}5:{PC[p]['B76 net prem']}16)" for p in A.PRODUCTS) + ")", "0.000000"),
]
for i, (lab, f, fmt) in enumerate(outs):
    r = 5 + i; cover[f"A{r}"] = lab; put(cover, f"B{r}", f, fmt)
mc = E.monte_carlo(); b76 = E.outage_table("black76")[E.recommend()]
r = 5 + len(outs) + 1
cover[f"A{r}"] = "Python engine only (values, not formulas)"; cover[f"A{r}"].font = BOLD
for lab, v in [("Monte Carlo 5th percentile, unhedged", mc["unhedged_p05"]), ("Monte Carlo 5th percentile, 80% cover", mc["hedged_p05"]),
               ("Outage cost, Black-76 strikes", b76["unbacked_cost"])]:
    r += 1; cover[f"A{r}"] = lab; put(cover, f"B{r}", v, PCT)
cover.column_dimensions["A"].width = 52; cover.column_dimensions["B"].width = 16

if __name__ == "__main__":
    RAW.parent.mkdir(exist_ok=True); wb.save(RAW); print("built", RAW)
