"""Pure-Python LSEG model. Mirrors the Excel formulas exactly; used for scenario outputs and CI tests."""
from . import assumptions as A

DIVS = ["Data & Analytics", "FTSE Russell", "Risk Intelligence", "Markets", "Other"]


def run(scenario: int = A.SCENARIO) -> dict:
    Y = A.YEARS_FCST
    g_adj = A.SCEN["growth_adj"][scenario]
    m_adj = A.SCEN["margin_adj"][scenario]
    tvg = A.SCEN["tv_growth"][scenario]
    o = A.OCTUS
    r = {k: {} for k in ["div", "inc", "rec", "oct_rev", "tot", "ebitda", "da", "pa", "ebit",
                         "fin", "pbt", "tax", "ni", "nci", "ni_sh", "eps", "rep_ni_sh",
                         "capex", "other", "eqfcf", "acq", "debt_add", "div_cash", "nci_div",
                         "bb", "px", "sh_open", "sh_close", "sh_avg", "dps",
                         "cash", "intang", "debt", "equity", "net_debt", "lev", "check", "ufcf"]}
    prev = {d: A.HIST[d][2025] for d in DIVS}
    cash, intang = A.OPENING_BS["Cash"], A.OPENING_BS["Goodwill & intangibles"]
    debt, equity = A.OPENING_BS["Borrowings incl leases"], A.OPENING_BS["Total equity"]
    other_net = equity + debt - cash - intang          # other net assets (plug, held constant)
    sh = A.OPENING_SHARES
    rec = A.HIST["Recoveries"][2025]
    pa_core = A.PURCH_AMORT_2026
    oct_rev = 0.0
    for i, y in enumerate(Y):
        divs = {d: prev[d] * (1 + A.GROWTH[d][i] + (g_adj if d != "Other" else 0)) for d in DIVS}
        prev = divs
        inc = sum(divs.values())
        if y == o["close_year"]:
            oct_rev = o["rev_2026_usd_m"] / A.GBPUSD * (1 + o["growth"]) ** (y - 2026)
        elif y > o["close_year"]:
            oct_rev = oct_rev * (1 + o["growth"])
        inc_tot = inc + oct_rev
        rec = rec * (1 + A.RECOVERIES_GROWTH)
        margin = A.EBITDA_MARGIN[i] + (m_adj if y >= 2027 else 0)
        ebitda = inc * margin + oct_rev * o["ebitda_margin"]
        da = inc_tot * A.ADJ_DA_PCT[i]
        pa = pa_core + (o["purch_amort"] if y >= o["close_year"] else 0)
        ebit = ebitda - da
        net_debt_open = debt - cash
        acq = o["price_usd_m"] / A.GBPUSD if y == o["close_year"] else 0.0
        fin = net_debt_open * A.NET_FIN_RATE + ((o["price_usd_m"] / A.GBPUSD) * (o["debt_rate"] - A.NET_FIN_RATE) if y >= o["close_year"] else 0)
        pbt = ebit - fin
        tax = pbt * A.TAX_RATE
        ni = pbt - tax
        nci = ni * A.NCI_SHARE
        ni_sh = ni - nci
        rep_ni = (pbt - pa) * (1 - A.TAX_RATE)
        rep_ni_sh = rep_ni * (1 - A.NCI_SHARE)
        capex = inc_tot * A.CAPEX_PCT[i]
        other = ebitda * A.OTHER_CASH_PCT
        eqfcf = ebitda - capex - fin - tax - other
        px = A.SHARE_PRICE * (1 + A.BUYBACK_PRICE_GROWTH) ** (i + 0.5)
        # dividends on prior-year-style payout of this year's EPS (uses opening shares to avoid circularity)
        eps_pre = ni_sh / sh * 100
        dps = eps_pre * A.DIV_PAYOUT
        div_cash = dps * sh / 100
        nci_div = nci * A.NCI_PAYOUT
        bb = A.BUYBACKS_FIXED.get(y, max(0.0, (eqfcf - div_cash - nci_div) * A.BUYBACK_SHARE_OF_SURPLUS))
        sh_close = sh - bb / px * 100
        sh_avg = (sh + sh_close) / 2
        eps = ni_sh / sh_avg * 100
        # balance sheet roll
        debt = debt + acq
        cash = cash + eqfcf - acq + acq - div_cash - nci_div - bb      # acquisition debt-funded
        intang = intang + capex + acq - da - pa
        equity = equity + rep_ni - div_cash - nci_div - bb
        # other net assets: other cash items settle liabilities (leases, provisions); deferred tax
        # liability on purchased intangibles unwinds as they amortise
        other_net = other_net + other + pa * A.TAX_RATE
        check = cash + intang + other_net - debt - equity
        ufcf = ebitda - capex - ebit * A.TAX_RATE - other
        for k, v in dict(div=divs, inc=inc, rec=rec, oct_rev=oct_rev, tot=inc_tot, ebitda=ebitda, da=da, pa=pa,
                         ebit=ebit, fin=fin, pbt=pbt, tax=tax, ni=ni, nci=nci, ni_sh=ni_sh, eps=eps,
                         rep_ni_sh=rep_ni_sh, capex=capex, other=other, eqfcf=eqfcf, acq=acq,
                         debt_add=acq, div_cash=div_cash, nci_div=nci_div, bb=bb, px=px, sh_open=sh,
                         sh_close=sh_close, sh_avg=sh_avg, dps=dps, cash=cash, intang=intang, debt=debt,
                         equity=equity, net_debt=debt - cash, lev=(debt - cash) / ebitda, check=check,
                         ufcf=ufcf).items():
            r[k][y] = v
        sh = sh_close
        pa_core = pa_core * (1 - A.PURCH_AMORT_DECLINE)
    # ---------- DCF at 31 Dec 2026 ----------
    d = A.DCF
    ke = d["rf"] + d["beta"] * d["erp"]
    wacc = (1 - d["debt_weight"]) * ke + d["debt_weight"] * d["kd_pre"] * (1 - A.TAX_RATE)
    pv = 0.0
    dyears = [y for y in Y if y > 2026]
    for t, y in enumerate(dyears, start=1):
        pv += r["ufcf"][y] / (1 + wacc) ** (t - 0.5)
    last = dyears[-1]
    tv = r["ufcf"][last] * (1 + tvg) / (wacc - tvg)
    pv_tv = tv / (1 + wacc) ** (len(dyears) - 0.5)
    ev = pv + pv_tv
    nci_val = r["nci"][2027] * d["nci_multiple"]
    eq = ev - r["net_debt"][2026] - nci_val
    fv = eq / r["sh_close"][2026] * 100
    return dict(r=r, ke=ke, wacc=wacc, pv_fcf=pv, tv=tv, pv_tv=pv_tv, ev=ev, nci_val=nci_val,
                equity_value=eq, fair_value=fv, upside=fv / A.SHARE_PRICE - 1,
                tv_share=pv_tv / ev, tv_ebitda=tv / r["ebitda"][last],
                pe_2027=A.SHARE_PRICE / r["eps"][2027])


if __name__ == "__main__":
    for s in (1, 2, 3):
        o = run(s)
        r = o["r"]
        print(A.SCEN_NAMES[s], f"FV {o['fair_value']:.0f}p upside {o['upside']:+.1%} WACC {o['wacc']:.2%} TV% {o['tv_share']:.0%} TV/EBITDA {o['tv_ebitda']:.1f}x")
        if s == 2:
            for y in A.YEARS_FCST:
                print(y, f"inc {r['inc'][y]:.0f} g {r['tot'][y]/(r['tot'][y-1] if y>2026 else 8986)-1:+.1%} EBITDA {r['ebitda'][y]:.0f} EPS {r['eps'][y]:.1f} DPS {r['dps'][y]:.1f} EqFCF {r['eqfcf'][y]:.0f} BB {r['bb'][y]:.0f} sh {r['sh_close'][y]:.1f} ND {r['net_debt'][y]:.0f} lev {r['lev'][y]:.2f} chk {r['check'][y]:.6f}")
