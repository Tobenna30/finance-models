"""Pure-Python cash underwriting. No asserted covenant or audited balance sheet."""
from . import assumptions as A


def capacity(ebitda=None, rate=None):
    """Gross debt capacity: minimum of leverage and interest-cover policy limits."""
    v = A.value
    e = A.EBITDA if ebitda is None else ebitda
    r = v("base_rate") + v("spread") if rate is None else rate
    if e <= 0 or r <= 0:
        raise ValueError("Positive EBITDA and interest rate required")
    cash_e = e * (1-v("cash_haircut"))
    lev = cash_e * v("max_leverage")
    cov = (cash_e / v("min_cover") - A.RCF*v("commit_fee")) / r
    return dict(leverage=lev, cover=cov, capacity=max(0, min(lev, cov)),
                requested=A.TLB, excess=A.TLB-max(0, min(lev, cov)),
                break_even_ebitda=A.TLB/v("max_leverage")/(1-v("cash_haircut")))


def run(case="Base"):
    v=A.value; c=A.CASES[case]
    rev_prev=A.REVENUE; cash=v("opening_cash"); debt=A.TLB; revolver=0.0; rows=[]
    for i, year in enumerate(A.YEARS):
        opening_cash, opening_debt, opening_rcf = cash, debt, revolver
        rev=rev_prev*(1+c["growth"][i]); ebitda=rev*c["margin"][i]
        cash_ebitda=ebitda*(1-v("cash_haircut"))
        interest=debt*(v("base_rate")+v("spread")+c["rate_shock"])
        interest+=revolver*(v("base_rate")+v("rcf_spread")+c["rate_shock"])
        fee=(A.RCF-revolver)*v("commit_fee")
        da=rev*v("da"); tax=max(0,cash_ebitda-da-interest-fee)*v("tax")
        capex=((v("capex_low")+v("capex_high"))/2 if i==0 else rev*v("capex_normal"))*c["capex_multiplier"]
        nwc=(rev-rev_prev)*v("nwc"); transaction=v("transaction_cost") if i==0 else 0.0
        fcf=cash_ebitda-interest-fee-tax-capex-nwc-transaction
        amort=min(debt,A.TLB*v("amort")); available=cash+fcf-amort
        draw=min(max(0,v("minimum_cash")-available),A.RCF-revolver)
        repay=min(max(0,available-v("minimum_cash")),revolver)
        sweep=min(max(0,available-repay-v("minimum_cash"))*v("sweep"),debt-amort)
        debt-=amort+sweep; revolver+=draw-repay; cash=available+draw-repay-sweep
        liquidity=cash+A.RCF-revolver; gross=debt+revolver
        rows.append(dict(year=year,revenue=rev,ebitda=ebitda,cash_ebitda=cash_ebitda,
                         interest=interest,fee=fee,da=da,tax=tax,capex=capex,nwc=nwc,transaction=transaction,fcf=fcf,
                         opening_cash=opening_cash,opening_debt=opening_debt,opening_rcf=opening_rcf,
                         amort=amort,available=available,draw=draw,repay=repay,sweep=sweep,
                         debt=debt,revolver=revolver,cash=cash,gross=gross,net=gross-cash,
                         liquidity=liquidity,leverage=gross/cash_ebitda,cover=cash_ebitda/(interest+fee),
                         lev_headroom=v("max_leverage")-gross/cash_ebitda,
                         cover_headroom=cash_ebitda/(interest+fee)-v("min_cover"),
                         unfunded=max(0,v("minimum_cash")-cash),
                         cash_check=cash-opening_cash-fcf+amort-draw+repay+sweep,
                         debt_check=gross-opening_debt-opening_rcf+amort+sweep-draw+repay))
        rev_prev=rev
    return rows


def recovery(multiple=None, haircut=None, rcf_draw=None):
    """Default waterfall. RCF assumed pari passu; claims and priorities unverified."""
    v=A.value
    m=v("recovery_multiple") if multiple is None else multiple
    h=v("recovery_haircut") if haircut is None else haircut
    draw=v("recovery_rcf_draw") if rcf_draw is None else rcf_draw
    if m<0 or not 0<=h<=1 or not 0<=draw<=1:
        raise ValueError("Invalid recovery stress")
    e=A.EBITDA*(1-v("cash_haircut"))*(1-h); ev=e*m
    costs=ev*v("recovery_cost"); pool=max(0,ev-costs-v("priority_claims"))
    claims=A.TLB+A.RCF*draw; distributed=min(pool,claims); recovery=distributed/claims
    return dict(ebitda=e,ev=ev,costs=costs,pool=pool,claims=claims,
                recovery=recovery,tlb_proceeds=A.TLB*recovery,rcf_proceeds=A.RCF*draw*recovery,
                shortfall=claims-distributed,equity=max(0,pool-claims))


def summary():
    b=run(); d=run("Downside"); cap=capacity(); rec=recovery()
    return {"Term loan (SEKm)":A.TLB,"Capacity under policy (SEKm)":cap["capacity"],
            "Requested less capacity (SEKm)":cap["excess"],
            "Base 2026 cash EBITDA (SEKm)":b[0]["cash_ebitda"],
            "Base 2026 FCF (SEKm)":b[0]["fcf"],"Base peak revolver (SEKm)":max(r["revolver"] for r in b),
            "Base 2026 gross leverage":b[0]["leverage"],"Base 2026 interest cover":b[0]["cover"],
            "Base 2030 gross leverage":b[-1]["leverage"],
            "Downside peak revolver (SEKm)":max(r["revolver"] for r in d),
            "Downside minimum liquidity (SEKm)":min(r["liquidity"] for r in d),
            "Downside peak unfunded cash (SEKm)":max(r["unfunded"] for r in d),
            "Default first-lien recovery":rec["recovery"],
            "EBITDA for entry policy ceiling (SEKm)":cap["break_even_ebitda"]}


if __name__=="__main__":
    import json
    print(json.dumps(summary(),indent=2))
