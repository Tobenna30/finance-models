"""Pure-Python LSEG model (v2, driver-based). Mirrors the Excel formulas; used for scenarios, reverse DCF and CI."""
from statistics import median
from . import assumptions as A

KEYS = [k for k, _, _ in A.LINES]
DIV_OF = {k: d for k, _, d in A.LINES}


def run(scenario: int = A.SCENARIO, overrides: dict | None = None) -> dict:
    sc = {k: v[scenario] for k, v in A.SCEN.items()}
    if overrides: sc.update(overrides)
    Y = A.YEARS_FCST
    r = {}
    def put(k, y, v): r.setdefault(k, {})[y] = v
    prev = {k: A.HIST_LINES[k][2025] for k in KEYS}
    o = A.OCTUS
    cash, intang = A.OPENING_BS["Cash"], A.OPENING_BS["Goodwill & intangibles"]
    debt, equity = A.OPENING_BS["Borrowings incl leases"], A.OPENING_BS["Total equity"]
    other_net = equity + debt - cash - intang
    sh, rec, pa_core, oct_rev = A.OPENING_SHARES, A.HIST["Recoveries"][2025], A.PURCH_AMORT_2026, 0.0
    aum = adv = coll = yld = capt = spr = None
    for i, y in enumerate(Y):
        L = {}
        if y == 2026:
            for k in KEYS:
                L[k] = sum(A.Q[k][4:7]) + A.Q[k][3] * (1 + A.Q4_GROWTH[k])
            aum, adv, coll = A.ETF_AUM_AVG_2026, A.TW_ADV_2026, A.COLLATERAL_2026
            yld = L["fa"] * A.GBPUSD / (aum * 1000) * 1e4          # bps
            capt = L["fido"] / adv                                  # £m per $bn ADV
            spr = L["nti"] * A.EURGBP / (coll * 1000) * 1e4         # bps
            asv = None
        else:
            ret = A.RETENTION[i] + sc["retention_adj"]
            asv = A.GROSS_SALES_PCT[i] + A.PRICE_OTHER[i] - (1 - ret)
            put("ret", y, ret)
            L["wf"] = prev["wf"] * (1 + asv + A.SPREAD["wf"][i] + sc["wf_spread_adj"])
            for k in ("df", "an", "fs", "ri"):
                L[k] = prev[k] * (1 + asv + A.SPREAD[k][i])
            aum = aum * (1 + A.ETF_AUM_GROWTH[i] + sc["aum_adj"]); yld = yld * (1 + A.ETF_YIELD_CHANGE[i])
            L["fa"] = aum * 1000 * yld / 1e4 / A.GBPUSD
            adv = adv * (1 + A.TW_ADV_GROWTH[i] + sc["mkt_vol_adj"]); capt = capt * (1 + A.FIDO_CAPTURE_CHANGE[i])
            L["fido"] = adv * capt
            L["otc"] = prev["otc"] * (1 + A.SWAPCLEAR_GROWTH[i] + sc["mkt_vol_adj"]) * (1 + A.OTC_CAPTURE_CHANGE[i])
            coll = coll * (1 + A.COLLATERAL_GROWTH[i])
            spr = spr * (1 + A.NTI_SPREAD_CHANGE[i] + (sc["nti_adj"] if y == 2027 else 0))
            L["nti"] = coll * 1000 * spr / 1e4 / A.EURGBP
            for k in ("eq", "fx"):
                L[k] = prev[k] * (1 + A.OTHER_GROWTH[k][i] + sc["mkt_vol_adj"])
            for k in ("sr", "ncc", "oth"):
                L[k] = prev[k] * (1 + A.OTHER_GROWTH[k][i])
        for k in KEYS: put(k, y, L[k])
        put("asv", y, asv); put("aum", y, aum); put("yld", y, yld); put("adv", y, adv); put("capt", y, capt)
        put("coll", y, coll); put("spr", y, spr)
        prev = L
        if y == o["close_year"]:
            oct_rev = o["rev_2026_usd_m"] / A.GBPUSD * (1 + o["growth"]) ** (y - 2026)
        elif y > o["close_year"]:
            oct_rev *= 1 + o["growth"]
        put("oct", y, oct_rev)
        div_rev = {d: sum(L[k] for k in KEYS if DIV_OF[k] == d) for d, _ in A.DIVISIONS}
        div_rev["D&A"] += oct_rev
        ebitda = A.OTHER_EBITDA + oct_rev * o["ebitda_margin"]
        for d in ("D&A", "FTSE", "RI", "MKT"):
            m = A.DIV_MARGIN[d][i] + (sc["margin_adj"] * (y - 2026) if y >= 2027 else 0)
            core = div_rev[d] - (oct_rev if d == "D&A" else 0)
            put("m_" + d, y, m); put("e_" + d, y, core * m)
            ebitda += core * m
        for d, _ in A.DIVISIONS: put("rev_" + d, y, div_rev[d])
        tot = sum(div_rev.values())
        rec *= 1 + A.RECOVERIES_GROWTH
        da = tot * A.ADJ_DA_PCT[i]
        pa = pa_core + (o["purch_amort"] if y >= o["close_year"] else 0)
        ebit = ebitda - da
        acq = o["price_usd_m"] / A.GBPUSD if y == o["close_year"] else 0.0
        fin = (debt - cash) * A.NET_FIN_RATE + ((o["price_usd_m"] / A.GBPUSD) * (o["debt_rate"] - A.NET_FIN_RATE) if y >= o["close_year"] else 0)
        pbt = ebit - fin; tax = pbt * A.TAX_RATE; ni = pbt - tax
        nci = ni * A.NCI_SHARE; ni_sh = ni - nci
        rep_ni = (pbt - pa) * (1 - A.TAX_RATE)
        capex = tot * A.CAPEX_PCT[i]; other = ebitda * A.OTHER_CASH_PCT
        eqfcf = ebitda - capex - fin - tax - other
        px = A.SHARE_PRICE * (1 + A.BUYBACK_PRICE_GROWTH) ** (i + 0.5)
        dps = ni_sh / sh * 100 * A.DIV_PAYOUT; div_cash = dps * sh / 100; nci_div = nci * A.NCI_PAYOUT
        bb = A.BUYBACKS_FIXED.get(y, max(0.0, (eqfcf - div_cash - nci_div) * A.BUYBACK_SHARE_OF_SURPLUS))
        sh_close = sh - bb / px * 100; sh_avg = (sh + sh_close) / 2; eps = ni_sh / sh_avg * 100
        debt += acq
        cash += eqfcf - div_cash - nci_div - bb
        intang += capex + acq - da - pa
        equity += rep_ni - div_cash - nci_div - bb
        other_net += other + pa * A.TAX_RATE
        ufcf = ebitda - capex - ebit * A.TAX_RATE - other
        for k, v in dict(tot=tot, rec=rec, ebitda=ebitda, da=da, pa=pa, ebit=ebit, fin=fin, pbt=pbt, tax=tax,
                         ni=ni, nci=nci, ni_sh=ni_sh, eps=eps, rep_ni=rep_ni, capex=capex, other=other,
                         eqfcf=eqfcf, acq=acq, div_cash=div_cash, nci_div=nci_div, bb=bb, px=px, sh_open=sh,
                         sh_close=sh_close, sh_avg=sh_avg, dps=dps, cash=cash, intang=intang, debt=debt,
                         equity=equity, othnet=other_net, net_debt=debt - cash, lev=(debt - cash) / ebitda,
                         check=cash + intang + other_net - debt - equity, ufcf=ufcf).items():
            put(k, y, v)
        sh = sh_close; pa_core *= 1 - A.PURCH_AMORT_DECLINE
    # DCF at 31 Dec 2026, mid-year convention
    d = A.DCF
    ke = d["rf"] + d["beta"] * d["erp"]
    wacc = (1 - d["debt_weight"]) * ke + d["debt_weight"] * d["kd_pre"] * (1 - A.TAX_RATE)
    tvg = sc["tv_growth"]
    dy = [y for y in Y if y > 2026]
    pv = sum(r["ufcf"][y] / (1 + wacc) ** (t - 0.5) for t, y in enumerate(dy, start=1))
    tv = r["ufcf"][dy[-1]] * (1 + tvg) / (wacc - tvg)
    pv_tv = tv / (1 + wacc) ** (len(dy) - 0.5)
    ev = pv + pv_tv
    nci_val = A.TW_PRICE_USD * A.TW_SHARES_M * (1 - A.LSEG_TW_ECON) / A.GBPUSD   # £m, minority at market value
    eq = ev - r["net_debt"][2026] - nci_val
    fv = eq / r["sh_close"][2026] * 100
    return dict(r=r, ke=ke, wacc=wacc, pv_fcf=pv, tv=tv, pv_tv=pv_tv, ev=ev, nci_val=nci_val, equity_value=eq,
                fair_value=fv, upside=fv / A.SHARE_PRICE - 1, tv_share=pv_tv / ev, tv_ebitda=tv / r["ebitda"][dy[-1]])


def solve(key: str, lo: float, hi: float, target: float = A.SHARE_PRICE) -> float:
    """Value of a scenario delta (base case otherwise) at which DCF fair value equals the share price."""
    f = lambda x: run(2, {key: x})["fair_value"] - target
    flo = f(lo)
    for _ in range(80):
        mid = (lo + hi) / 2
        if (f(mid) > 0) == (flo > 0): lo, flo = mid, f(mid)
        else: hi = mid
    return (lo + hi) / 2


def stub() -> dict:
    """LSEG excluding its Tradeweb stake at market value, on the same forward-earnings source as the comps."""
    ls = A.LSEG_SAME_SOURCE
    mcap = ls["price"] * A.LSEG_MKT_SHARES / 100                      # £m
    tw_mcap = A.TW_PRICE_USD * A.TW_SHARES_M / A.GBPUSD               # £m
    stake = tw_mcap * A.LSEG_TW_ECON
    lseg_earn = mcap / ls["fwd_pe"]
    tw_share_earn = tw_mcap / A.TW_FWD_PE * A.LSEG_TW_ECON
    stub_val, stub_earn = mcap - stake, lseg_earn - tw_share_earn
    return dict(mcap=mcap, tw_mcap=tw_mcap, stake=stake, stake_pct=stake / mcap, stub_value=stub_val,
                stub_earnings=stub_earn, stub_pe=stub_val / stub_earn, group_pe=ls["fwd_pe"])


def ltm_eps(month: str) -> float:
    """LTM adjusted EPS at a month-end: linear between fiscal year-ends, using H1 figures where available."""
    y, m = int(month[:4]), int(month[5:])
    pts = {f"{yy}-12": e for yy, e in A.ADJ_EPS_FY.items()}
    for yy, h in A.H1_EPS.items():
        if yy - 1 in A.ADJ_EPS_FY and yy - 1 in A.H1_EPS:
            pts[f"{yy}-06"] = A.ADJ_EPS_FY[yy - 1] - A.H1_EPS[yy - 1] + h
    pts[f"2026-12"] = run(2)["r"]["eps"][2026]
    keys = sorted(pts, key=lambda k: (int(k[:4]), int(k[5:])))
    idx = lambda k: int(k[:4]) * 12 + int(k[5:])
    t = y * 12 + m
    for a, b in zip(keys, keys[1:]):
        if idx(a) <= t <= idx(b):
            w = (t - idx(a)) / (idx(b) - idx(a)); return pts[a] * (1 - w) + pts[b] * w
    raise ValueError(month)


def pe_history() -> dict:
    rows = [(mth, px, ltm_eps(mth), px / ltm_eps(mth)) for mth, px in A.MONTHLY_CLOSE.items()]
    pes = [x[3] for x in rows]
    return dict(rows=rows, avg=sum(pes) / len(pes), lo=min(pes), hi=max(pes), now=pes[-1],
                pct_rank=sum(p <= pes[-1] for p in pes) / len(pes))


def beta_sensitivity(betas=(0.60, 0.85, 1.00)) -> dict:
    out = {}
    base = A.DCF["beta"]
    for b in betas:
        A.DCF["beta"] = b; out[b] = run(2)["fair_value"]
    A.DCF["beta"] = base
    return out


def comps_by_ticker():
    return {row[1]: row for row in A.COMPS}


def sotp(res: dict | None = None, year: int = 2026) -> dict:
    res = res or run(2)
    r, cb = res["r"], comps_by_ticker()
    da_tot = sum(A.DIV_DA_2025.values())
    ebit = {d: r["e_" + d][year] - r["da"][year] * A.DIV_DA_2025[d] / da_tot for d in A.SOTP_PEERS}
    ebit_sum = sum(ebit.values())
    earn = {d: (ebit[d] - r["fin"][year] * ebit[d] / ebit_sum) * (1 - A.TAX_RATE) for d in ebit}
    earn["MKT"] -= r["nci"][year]
    tot = sum(earn.values())
    parts, blended = {}, 0.0
    for d, tick in A.SOTP_PEERS.items():
        pe = median(cb[t][6] for t in tick); w = earn[d] / tot
        parts[d] = dict(earnings=earn[d], weight=w, pe=pe); blended += w * pe
    ntm_eps = A.LSEG_SAME_SOURCE["price"] / A.LSEG_SAME_SOURCE["fwd_pe"]
    value = blended * ntm_eps
    return dict(parts=parts, blended_pe=blended, ntm_eps=ntm_eps, per_share=value,
                upside=value / A.LSEG_SAME_SOURCE["price"] - 1)


if __name__ == "__main__":
    for s in (1, 2, 3):
        o = run(s); r = o["r"]
        print(A.SCEN_NAMES[s], f"FV {o['fair_value']:.0f}p {o['upside']:+.1%} TV% {o['tv_share']:.0%} TV/EBITDA {o['tv_ebitda']:.1f}x")
    o = run(2); r = o["r"]
    for y in A.YEARS_FCST:
        print(y, f"tot {r['tot'][y]:.0f} g {r['tot'][y]/(r['tot'][y-1] if y>2026 else 8986)-1:+.1%} ASV {r['asv'][y] if r['asv'][y] else 0:.1%} EBITDA {r['ebitda'][y]:.0f} m {r['ebitda'][y]/r['tot'][y]:.1%} EPS {r['eps'][y]:.1f} FCF {r['eqfcf'][y]:.0f} lev {r['lev'][y]:.2f} chk {r['check'][y]:.6f}")
    print({d: round(r['rev_'+d][2026]) for d,_ in A.DIVISIONS}, {d: round(r['rev_'+d][2027]) for d,_ in A.DIVISIONS})
    st = stub(); ph = pe_history(); print("stub", {k: round(v, 2) for k, v in st.items()}); print("PE hist now/avg/lo/hi/rank", round(ph["now"],1), round(ph["avg"],1), round(ph["lo"],1), round(ph["hi"],1), round(ph["pct_rank"],2)); print("beta sens", {k: round(v) for k, v in beta_sensitivity().items()})
    so = sotp(o); print("NCI val", round(o["nci_val"]), "SOTP", {k: (round(v['weight'],3), v['pe']) for k,v in so['parts'].items()}, round(so['blended_pe'],2), round(so['per_share']), f"{so['upside']:+.1%}")
    print("implied retention adj", round(solve('retention_adj', -0.05, 0.02), 4), "implied mkt vol adj", round(solve('mkt_vol_adj', -0.15, 0.05), 4))
