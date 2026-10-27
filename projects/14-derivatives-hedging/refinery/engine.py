"""Refinery margin hedge engine. Pure Python, no Excel logic.

Pricing: Bachelier (normal model), because cracks can go negative. Black-76 runs alongside as a cross-check only.
Each 2027 month gets a collar on its average crack, settled in cash at month end.
Margin here is refining margin: crack x barrels. Opex is excluded, so it is not profit or cash flow.
"""
import calendar
import math
import random
from datetime import date, timedelta
from . import assumptions as A

SQ2 = math.sqrt(2)


def ncdf(x):
    return 0.5 * (1 + math.erf(x / SQ2))


def npdf(x):
    return math.exp(-x * x / 2) / math.sqrt(2 * math.pi)


# ---------------------------------------------------------------- pricing
def bachelier(f, k, vol, t, r, call=True):
    s = vol * math.sqrt(t); d = (f - k) / s; df = math.exp(-r * t)
    c = df * ((f - k) * ncdf(d) + s * npdf(d))
    return c if call else c - df * (f - k)


def black76(f, k, vol, t, r, call=True):
    if f <= 0 or k <= 0:
        raise ValueError("Black-76 needs a positive forward and strike")
    s = vol * math.sqrt(t); d1 = (math.log(f / k) + s * s / 2) / s; d2 = d1 - s; df = math.exp(-r * t)
    if call:
        return df * (f * ncdf(d1) - k * ncdf(d2))
    return df * (k * ncdf(-d2) - f * ncdf(-d1))


def zero_cost_call(price, f, kp, vol, t, r):
    """Call strike whose premium equals the put premium (bisection)."""
    target = price(f, kp, vol, t, r, call=False); lo, hi = f, f * 20 + 100
    for _ in range(200):
        mid = (lo + hi) / 2
        if price(f, mid, vol, t, r) > target: lo = mid
        else: hi = mid
    return (lo + hi) / 2


def months():
    """2027 settlement months: (month, days, year fraction from valuation to month end)."""
    out = []
    for m in range(1, 13):
        n = calendar.monthrange(A.HEDGE_YEAR, m)[1]
        t = (date(A.HEDGE_YEAR, m, n) - A.VALUATION_DATE).days / 365
        out.append((m, n, t))
    return out


def strikes(model="bachelier"):
    """Per product and month: put strike, call strike, put and call premiums ($/bbl)."""
    price = bachelier if model == "bachelier" else black76
    out = {}
    for p in A.PRODUCTS:
        f = A.FORWARD[p]; kp = f * (1 - A.PUT_DISTANCE)
        vol = A.NORMAL_VOL[p] if model == "bachelier" else A.NORMAL_VOL[p] / f   # same dollar vol at the money
        rows = []
        for m, n, t in months():
            kc = zero_cost_call(price, f, kp, vol, t, A.USD_RATE)
            rows.append(dict(month=m, put=kp, call=kc, put_prem=price(f, kp, vol, t, A.USD_RATE, call=False),
                             call_prem=price(f, kc, vol, t, A.USD_RATE)))
        out[p] = rows
    return out


# ---------------------------------------------------------------- volumes
def budget_bbl(p, days):
    return A.CAPACITY_BPD * A.AVAILABILITY * A.YIELD[p] * days


def annual_budget_margin():
    return sum(budget_bbl(p, n) * A.FORWARD[p] for p in A.PRODUCTS for _, n, _ in months()) / 1e6   # $m


def outage_days_in(m):
    end = A.OUTAGE_START + timedelta(days=A.OUTAGE_DAYS)
    return sum(A.OUTAGE_START <= date(A.HEDGE_YEAR, m, d) < end for d in range(1, calendar.monthrange(A.HEDGE_YEAR, m)[1] + 1))


def payoff(x, kp, kc):
    return max(kp - x, 0) - max(x - kc, 0)


# ---------------------------------------------------------------- scenarios
def case(cover, shock, outage=False, model="bachelier"):
    """Full-year 2027 refining margin under a parallel crack move, optionally with the six-week outage."""
    K = strikes(model); budget = annual_budget_margin()
    phys = hedge = unbacked = 0.0; rows = []
    for i, (m, n, _) in enumerate(months()):
        lost = outage_days_in(m) if outage else 0
        row = dict(month=m, days=n, lost=lost)
        for p in A.PRODUCTS:
            crack = A.FORWARD[p] * (1 + shock); k = K[p][i]
            b = budget_bbl(p, n); run = budget_bbl(p, n - lost); hedged = cover * b
            pay = payoff(crack, k["put"], k["call"])
            phys += run * crack; hedge += hedged * pay
            unbacked += cover * budget_bbl(p, lost) * min(pay, 0)        # sold calls with no barrels behind them
            row[p] = dict(budget=b, run=run, hedged=hedged, crack=crack, payoff=pay)
        rows.append(row)
    margin = (phys + hedge) / 1e6
    return dict(cover=cover, shock=shock, outage=outage, model=model, margin=margin, budget=budget,
                change=margin / budget - 1, unbacked_cost=-unbacked / 1e6 / budget, rows=rows)


def grid(model="bachelier"):
    return {c: {s: case(c, s, model=model)["change"] for s in A.SHOCKS} for c in A.COVERS}


def outage_table(model="bachelier"):
    out = {}
    for c in A.COVERS:
        r = case(c, A.OUTAGE_SPIKE, outage=True, model=model)
        out[c] = dict(unbacked_cost=r["unbacked_cost"], total_change=r["change"], fall30=case(c, -0.30, model=model)["change"])
    return out


def recommend():
    """Most downside protection whose outage cost stays inside the stated appetite."""
    t = outage_table()
    ok = [c for c in A.COVERS if t[c]["unbacked_cost"] <= A.OUTAGE_APPETITE]
    return max(ok)


# ---------------------------------------------------------------- FX overlay
def fx_forward(t=None):
    """USD/ZAR forward by covered interest parity, compounded annually."""
    out = []
    for m, n, tm in months():
        tt = tm if t is None else t
        out.append(A.USDZAR_SPOT * ((1 + A.ZAR_RATE) / (1 + A.USD_RATE)) ** tt)
    return out


def fx_overlay(cover):
    """Sell USD forward month by month against the rand cost budget. Rand margin after opex, hedged and not."""
    fwd = fx_forward(); res = {}
    for shock in A.FX_SHOCKS:
        hedged = unhedged = 0.0
        for i, (m, n, _) in enumerate(months()):
            usd = sum(budget_bbl(p, n) * A.FORWARD[p] for p in A.PRODUCTS)
            rand_cost = A.CAPACITY_BPD * A.AVAILABILITY * n * A.OPEX_ZAR_PER_BBL
            spot = fwd[i] * (1 + shock)
            usd_sold = rand_cost / fwd[i]
            unhedged += usd * spot - rand_cost
            hedged += (usd - usd_sold) * spot + usd_sold * fwd[i] - rand_cost
        res[shock] = dict(unhedged=unhedged / 1e6, hedged=hedged / 1e6)
    return res


# ---------------------------------------------------------------- Monte Carlo
def monte_carlo(cover=None):
    """Annual average cracks as correlated normals. Stylised, not a calibrated forecast."""
    cover = A.COVERS[2] if cover is None else cover
    K = strikes(); rng = random.Random(A.MC_SEED); budget = annual_budget_margin()
    t = sum(x[2] for x in months()) / 12
    unh, hed = [], []
    for _ in range(A.MC_DRAWS):
        z1 = rng.gauss(0, 1); z2 = A.MC_CORR * z1 + math.sqrt(1 - A.MC_CORR ** 2) * rng.gauss(0, 1)
        u = h = 0.0
        for p, z in zip(A.PRODUCTS, (z1, z2)):
            x = A.FORWARD[p] + A.NORMAL_VOL[p] * math.sqrt(t) * z
            bbl = sum(budget_bbl(p, n) for _, n, _ in months())
            u += bbl * x; h += bbl * x + cover * bbl * payoff(x, K[p][0]["put"], K[p][0]["call"])
        unh.append(u / 1e6 / budget - 1); hed.append(h / 1e6 / budget - 1)
    unh.sort(); hed.sort(); i5 = int(0.05 * A.MC_DRAWS)
    return dict(cover=cover, unhedged_p05=unh[i5], hedged_p05=hed[i5],
                unhedged_mean=sum(unh) / len(unh), hedged_mean=sum(hed) / len(hed))


def summary():
    rec = recommend(); ot = outage_table(); b76 = outage_table("black76"); K = strikes(); KB = strikes("black76")
    return {
        "Annual budget refining margin ($m)": annual_budget_margin(),
        "Recommended cover": rec,
        "30% fall, recommended cover": ot[rec]["fall30"],
        "30% fall, unhedged": case(0, -0.30)["change"],
        "Outage cost on unbacked calls, recommended cover": ot[rec]["unbacked_cost"],
        "Outage + spike total change, recommended cover": ot[rec]["total_change"],
        "Diesel put strike ($/bbl)": K["diesel"][0]["put"],
        "Diesel call strike, Bachelier ($/bbl)": K["diesel"][0]["call"],
        "Diesel call strike Dec, Black-76 ($/bbl)": KB["diesel"][-1]["call"],
        "Outage cost, Black-76 check": b76[rec]["unbacked_cost"],
        "30% fall, Black-76 check": b76[rec]["fall30"],
    }


if __name__ == "__main__":
    for k, v in summary().items():
        print(f"{k:50s} {v:,.4f}")
