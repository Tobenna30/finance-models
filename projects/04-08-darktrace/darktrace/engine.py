"""Pure-Python engine for Darktrace projects 04 (sell-side) and 08 (LBO).
Every function mirrors a block of formulas in build_excel.py; tests tie the two after a LibreOffice recalc."""
from . import assumptions as A


def pct(vals, q):
    """Excel PERCENTILE.INC."""
    s = sorted(vals); k = (len(s) - 1) * q; f = int(k); c = min(f + 1, len(s) - 1)
    return s[f] + (s[c] - s[f]) * (k - f)


def to_p(usd):
    return usd * 100 / A.FX


def per_share_p(ev):
    return to_p((ev + A.NET_CASH) / A.FD_SHARES)


# ------------------------------------------------------------------ 04: DCF
def wacc():
    d = A.DCF
    return d["rf"] + d["beta"] * d["erp"]


def dcf(wacc_adj=0.0, g_adj=0.0, sbp_cost=True):
    d = A.DCF; w = wacc() + wacc_adj; g = d["tv_growth"] + g_adj
    rev_prev = A.HIST["Revenue"][2024]; rows = []; pv = 0.0
    for i, y in enumerate(A.YEARS_DCF):
        rev = rev_prev * (1 + d["rev_growth"][i]); ebitda = rev * d["ebitda_margin"][i]
        sbp = rev * d["sbp_pct"][i]; da = rev * A.DA_PCT; ebit = ebitda - sbp - da
        tax = max(0.0, ebit) * A.TAX; capex = rev * A.CAPEX_PCT; dnwc = (rev - rev_prev) * d["nwc_pct_drev"]
        ufcf = ebitda - (sbp if sbp_cost else 0.0) - tax - capex + dnwc; df = 1 / (1 + w) ** (i + 0.5); pv += ufcf * df
        rows.append(dict(year=y, rev=rev, ebitda=ebitda, sbp=sbp, da=da, ebit=ebit, tax=tax, capex=capex,
                         dnwc=dnwc, ufcf=ufcf, df=df, pv=ufcf * df))
        rev_prev = rev
    tv = rows[-1]["ufcf"] * (1 + g) / (w - g); pv_tv = tv / (1 + w) ** len(A.YEARS_DCF)
    ev = pv + pv_tv
    return dict(rows=rows, wacc=w, g=g, pv_fcf=pv, tv=tv, pv_tv=pv_tv, ev=ev, equity=ev + A.NET_CASH,
                per_share_usd=(ev + A.NET_CASH) / A.FD_SHARES, per_share_p=per_share_p(ev),
                tv_share=pv_tv / ev, tv_ev_ebitda=tv / rows[-1]["ebitda"])


def dcf_grid():
    return [[dcf(w, g)["per_share_p"] for g in A.DCF_GRID_G] for w in A.DCF_GRID_WACC]


# ------------------------------------------------------------------ 04: comps
def comps():
    rows = []
    for name, tk, px, sh, cash, debt, ntm, last, gy, src in A.COMPS:
        mcap = px * sh; ev = mcap - cash + debt
        rows.append(dict(name=name, ticker=tk, mcap=mcap, ev=ev, ntm=ntm, growth=ntm / last - 1, ev_ntm=ev / ntm))
    m = [r["ev_ntm"] for r in rows]; gr = [r["growth"] for r in rows]
    n = len(m); mx = sum(gr) / n; my = sum(m) / n
    slope = sum((x - mx) * (y - my) for x, y in zip(gr, m)) / sum((x - mx) ** 2 for x in gr)
    intercept = my - slope * mx
    fy25 = dcf()["rows"][0]["rev"]
    dt_ntm = A.NTM_WEIGHT_FY24 * A.HIST["Revenue"][2024] + (1 - A.NTM_WEIGHT_FY24) * fy25
    dt_growth = A.DCF["rev_growth"][0]
    q = {k: pct(m, v) for k, v in (("q1", 0.25), ("med", 0.5), ("q3", 0.75))}
    reg_mult = intercept + slope * dt_growth
    return dict(rows=rows, q=q, slope=slope, intercept=intercept, dt_ntm=dt_ntm, dt_growth=dt_growth,
                reg_mult=reg_mult, offer_ev_ntm=A.DEAL["enterprise_value"] / dt_ntm,
                implied_p={k: per_share_p(v * dt_ntm) for k, v in q.items()},
                reg_p=(per_share_p((reg_mult - 1) * dt_ntm), per_share_p((reg_mult + 1) * dt_ntm)))


# ------------------------------------------------------------------ 04: precedents and premiums
def precedents():
    rows = [dict(target=t, buyer=b, date=dt, ev=ev, rev=rv, ev_rev=ev / rv, prem=p, basis=bs)
            for t, b, dt, ev, rv, p, bs, *_ in A.PRECEDENTS]
    m = [r["ev_rev"] for r in rows]; p = [r["prem"] for r in rows]
    qm = {k: pct(m, v) for k, v in (("q1", 0.25), ("med", 0.5), ("q3", 0.75))}
    qp = {k: pct(p, v) for k, v in (("q1", 0.25), ("med", 0.5), ("q3", 0.75))}
    ltm = A.DEAL["ltm_revenue"]
    return dict(rows=rows, qm=qm, qp=qp, implied_p={k: per_share_p(v * ltm) for k, v in qm.items()},
                prem_p={k: A.DEAL["undisturbed_p"] * (1 + v) for k, v in qp.items()},
                prem_vwap_p={k: A.DEAL["vwap3m_p"] * (1 + v) for k, v in qp.items()},
                offer_ev_ltm=A.DEAL["enterprise_value"] / ltm)


# ------------------------------------------------------------------ 08: LBO
def lbo(case="Base", debt_total=None, exit_multiple=None, price_usd=None):
    c = A.CASES[case]; D = A.DEBT
    price = A.DEAL["offer_usd"] if price_usd is None else price_usd
    debt_total = D["tlb"] + D["sl"] if debt_total is None else debt_total
    tlb0 = debt_total * D["tlb"] / (D["tlb"] + D["sl"]); sl0 = debt_total - tlb0
    exit_x = c["exit_multiple"] if exit_multiple is None else exit_multiple
    eq_purchase = price * A.FD_SHARES; ev_entry = eq_purchase - A.NET_CASH
    oid = tlb0 * (1 - D["tlb_oid"]) + sl0 * (1 - D["sl_oid"])
    fin_fees = debt_total * A.FEES["financing_pct"]; adv_fees = ev_entry * A.FEES["advisory_pct_ev"]
    cash_used = A.CASH_AT_CLOSE - A.MIN_CASH
    uses = eq_purchase + oid + fin_fees + adv_fees
    sponsor = uses - debt_total - cash_used
    rev_prev = A.HIST["Revenue"][2024]; tlb, sl, cash = tlb0, sl0, A.MIN_CASH; rows = []
    for i, y in enumerate(A.YEARS_LBO):
        stub = A.CLOSE_STUB if i == 0 else 1.0
        rev = rev_prev * (1 + c["rev_growth"][i]); ebitda = rev * c["ebitda_margin"][i]
        capex = rev * A.CAPEX_PCT; dnwc = (rev - rev_prev) * A.NWC_PCT_DREV; da = rev * A.DA_PCT
        int_tlb = tlb * (A.SOFR[i] + D["tlb_margin"]) * stub; int_sl = sl * (A.SOFR[i] + D["sl_margin"]) * stub
        interest = int_tlb + int_sl
        deductible = min(interest, A.CIR_CAP * ebitda * stub)
        tax = max(0.0, (ebitda - da) * stub - deductible) * A.TAX
        fcf = (ebitda - capex + dnwc - A.LEASE_CASH) * stub - interest - tax
        amort = min(tlb, tlb0 * D["tlb_amort"] * stub)
        avail = cash + fcf - amort
        sweep = min(max(0.0, avail - A.MIN_CASH) * A.SWEEP, tlb - amort)
        tlb = tlb - amort - sweep; cash = avail - sweep
        rows.append(dict(year=y, rev=rev, ebitda=ebitda, capex=capex, dnwc=dnwc, da=da, int_tlb=int_tlb,
                         int_sl=int_sl, interest=interest, deductible=deductible, tax=tax, fcf=fcf, amort=amort,
                         sweep=sweep, tlb=tlb, sl=sl, cash=cash, net_debt=tlb + sl - cash,
                         lev=(tlb + sl) / ebitda, cover=ebitda * stub / interest))
        rev_prev = rev
    last = rows[-1]; exit_ev = exit_x * last["ebitda"]; exit_eq = exit_ev - last["net_debt"] - A.LEASES_EXIT
    sponsor_exit = exit_eq * (1 - A.MIP); moic = sponsor_exit / sponsor; irr = moic ** (1 / A.HOLD_YEARS) - 1
    return dict(rows=rows, eq_purchase=eq_purchase, ev_entry=ev_entry, oid=oid, fin_fees=fin_fees,
                adv_fees=adv_fees, uses=uses, tlb0=tlb0, sl0=sl0, cash_used=cash_used, sponsor=sponsor,
                equity_pct=sponsor / uses, entry_lev_ltm=debt_total / A.DEAL["ltm_ebitda"],
                entry_lev_arr=debt_total / A.HIST["ARR (cc)"][2024], exit_ev=exit_ev, exit_eq=exit_eq,
                sponsor_exit=sponsor_exit, moic=moic, irr=irr, exit_x=exit_x)


def bridge(case="Base"):
    """Sponsor value bridge: entry equity to sponsor exit proceeds."""
    r = lbo(case); last = r["rows"][-1]; e0 = A.DEAL["ltm_ebitda"]; x0 = r["ev_entry"] / e0
    nd0 = r["tlb0"] + r["sl0"] - A.MIN_CASH + A.H1["leases_dec23"]; nd1 = last["net_debt"] + A.LEASES_EXIT
    steps = [("Sponsor equity in", r["sponsor"]),
             ("EBITDA growth at entry multiple", (last["ebitda"] - e0) * x0),
             ("Multiple change (34x LTM to exit)", (r["exit_x"] - x0) * last["ebitda"]),
             ("Net debt paid down", nd0 - nd1),
             ("Fees and OID", -(r["oid"] + r["fin_fees"] + r["adv_fees"])),
             ("Management incentive plan", -r["exit_eq"] * A.MIP)]
    return steps, r["sponsor_exit"]


def lbo_grid(case="Base"):
    return [[lbo(case, d, x)["irr"] for d in A.GRID_DEBT] for x in A.GRID_EXIT]


def ability_to_pay(irr, case="Base"):
    """Max offer price per share ($) a sponsor can pay for a given IRR. Exit equity does not depend on price,
    so sponsor equity in = exit / (1+irr)^T and the price is solved in closed form (same formula in Excel)."""
    r = lbo(case); D = A.DEBT; debt = D["tlb"] + D["sl"]
    e_in = r["sponsor_exit"] / (1 + irr) ** A.HOLD_YEARS
    k = A.FEES["advisory_pct_ev"]
    return (e_in + debt + r["cash_used"] - r["oid"] - r["fin_fees"] + k * A.NET_CASH) / (A.FD_SHARES * (1 + k))


def solve_margin_for_irr(target=0.20, case="Base"):
    """Uniform shift to the base margin path that gives the target IRR (bisection)."""
    base = list(A.CASES[case]["ebitda_margin"]); lo, hi = -0.15, 0.15
    try:
        for _ in range(60):
            mid = (lo + hi) / 2; A.CASES[case]["ebitda_margin"] = [m + mid for m in base]
            if lbo(case)["irr"] < target: lo = mid
            else: hi = mid
    finally:
        A.CASES[case]["ebitda_margin"] = base
    return base[-1] + (lo + hi) / 2


# ------------------------------------------------------------------ 04: rival bid and football field
def rival():
    R = A.RIVAL; d = dcf(); fy25 = d["rows"][0]["rev"]
    syn = R["synergy_pct_rev"] * fy25
    syn_value = syn * (1 - A.TAX) * R["synergy_multiple"] - syn * R["integration_cost_x"]
    strat_ev = d["ev"] + R["strategic_share_kept"] * syn_value
    return dict(synergies=syn, syn_value=syn_value, strategic_p=per_share_p(strat_ev),
                pe_p=to_p(ability_to_pay(R["competing_pe_irr"])))


def football():
    D = A.DEAL; g = dcf_grid(); c = comps(); p = precedents()
    return [
        ("52-week trading (placing to 12m high)", D["placing_p"], D["high12m_p"]),
        ("DCF (WACC +/-1%, g +/-0.5%)", g[4][1], g[0][3]),
        ("Trading comps EV/NTM revenue (Q1-Q3)", c["implied_p"]["q1"], c["implied_p"]["q3"]),
        ("Growth-adjusted comps (regression +/-1x)", c["reg_p"][0], c["reg_p"][1]),
        ("Precedent take-privates EV/LTM revenue (Q1-Q3)", p["implied_p"]["q1"], p["implied_p"]["q3"]),
        ("Precedent premiums on undisturbed 517p (Q1-Q3)", p["prem_p"]["q1"], p["prem_p"]["q3"]),
        ("LBO ability to pay (25% to 20% IRR)", to_p(ability_to_pay(0.25)), to_p(ability_to_pay(0.20))),
    ]


def summary():
    d = dcf(); c = comps(); p = precedents(); b = lbo("Base"); dn = lbo("Downside"); rv = rival()
    return dict(dcf_p=d["per_share_p"], dcf_ex_sbp_p=dcf(sbp_cost=False)["per_share_p"], wacc=d["wacc"], comps_med_p=c["implied_p"]["med"], reg_mult=c["reg_mult"],
                offer_ev_ntm=c["offer_ev_ntm"], prec_med_p=p["implied_p"]["med"], prem_med=p["qp"]["med"],
                base_irr=b["irr"], base_moic=b["moic"], down_irr=dn["irr"], down_moic=dn["moic"],
                atp20_p=to_p(ability_to_pay(0.20)), atp25_p=to_p(ability_to_pay(0.25)),
                strategic_p=rv["strategic_p"], margin_for_20=solve_margin_for_irr(0.20))


if __name__ == "__main__":
    import json
    print(json.dumps(summary(), indent=1, default=float))
    for row in football(): print(f"{row[0]:50s} {row[1]:7.0f} {row[2]:7.0f}")
    b = lbo(); print({k: round(v, 1) for k, v in b.items() if isinstance(v, float)})
    for r in b["rows"]: print({k: round(v, 1) for k, v in r.items()})
    for x, row in zip(A.GRID_EXIT, lbo_grid()): print(x, [f"{v:.1%}" for v in row])
    print("downside", [f"{v:.1%}" for v in lbo_grid("Downside")[0]])
    c = comps(); [print(r["ticker"], round(r["ev"]), round(r["ev_ntm"], 1), f"{r['growth']:.1%}") for r in c["rows"]]
    print(c["q"], c["slope"], c["intercept"], c["dt_ntm"])
