"""Conditional liquidity and creditor economics; not legal recovery advice."""
import json
from .assumptions import ROOT,MONTHS,UPSIZE_MONTHS,values

def calculate(overrides=None):
    a=values();a.update(overrides or {})
    if a['funding_case'] not in (0,1,2) or a['maturity_case'] not in (0,1):raise ValueError('invalid funding or maturity case')
    if any(a[k]<0 for k in ('drawn','upsize','cash','burn','buffer','hedges','class_a','b_claim','b_rights','ev')) or a['equity']<=0 or a['facility']<a['drawn'] or not 0<=a['fee']<1 or not 0<=a['cost']<1:raise ValueError('invalid claim, liquidity, value or fee input')
    if min(a['drawn'],a['class_a'],a['b_claim'])<=0 or not 0<=a['march_claim']<a['class_a'] or a['equity_stress']<0 or not 0<=a['b_recovery']<=1:raise ValueError('positive claims and valid recovery required')
    cash=a['cash'];new_debt=0.;rows=[]
    for i,date in enumerate(MONTHS):
        old_draw=a['facility']-a['drawn'] if i==0 and a['funding_case']>=1 else 0.
        up_draw=a['upsize']/len(UPSIZE_MONTHS) if i in UPSIZE_MONTHS and a['funding_case']==2 else 0.
        draw=old_draw+up_draw;fee=up_draw*a['fee']
        interest=(new_debt+draw/2)*a['ss_rate']/12
        repay=a['march_claim'] if i==4 and a['maturity_case']==0 else 0.
        end=cash+draw-a['burn']-fee-interest-repay
        rows.append(dict(month=date.isoformat(),opening_cash=cash,existing_draw=old_draw,upsize_draw=up_draw,fees=fee,incremental_interest=interest,principal=repay,closing_cash=end,buffer_gap=max(0,a['buffer']-end),ss_debt=a['drawn']+new_debt+draw))
        new_debt+=draw;cash=end
    minimum=min(r['closing_cash'] for r in rows)
    first=next((r['month'] for r in rows if r['closing_cash']<a['buffer']),None)
    # A cash shortfall is left exposed. No fictitious funding is added.
    ss=a['drawn']+new_debt
    pot=a['ev']*(1-a['cost']);priority=min(pot,a['hedges']);remain=pot-priority
    ss_pay=min(remain,ss);remain-=ss_pay
    # A maturity is a cash requirement, not evidence that redemption was funded.
    # Keep the independent waterfall claim proxy intact until payment is proved.
    a_claim=a['class_a']
    a_pay=min(remain,a_claim);remain-=a_pay
    b_pay=min(remain,a['b_claim']);remain-=b_pay
    legacy_value=a['b_claim']*a['b_recovery']
    legacy_fraction=legacy_value/a['equity'];new_fraction=a['b_rights']/a['equity']
    realised=a['equity']*a['equity_stress']
    legacy_mark=legacy_fraction*realised;new_mark=new_fraction*realised
    return dict(months=rows,minimum_cash=minimum,ending_cash=cash,first_buffer_breach=first,peak_buffer_gap=max(r['buffer_gap'] for r in rows),new_draws=new_debt,ss_claim=ss,
                total_interest=sum(r['incremental_interest'] for r in rows),total_fees=sum(r['fees'] for r in rows),
                a_claim=a_claim,waterfall=dict(distributable=pot,priority_paid=priority,ss_paid=ss_pay,a_paid=a_pay,b_paid=b_pay,equity=remain,a_recovery=a_pay/a_claim,b_recovery=b_pay/a['b_claim']),
                a_break_even_ev=(a['hedges']+ss+a_claim)/(1-a['cost']),
                historical_quote_implied_ev=(a['hedges']+ss+a_claim*a['a_quote'])/(1-a['cost']),
                b_legacy_value=legacy_value,b_legacy_fraction=legacy_fraction,b_new_fraction=new_fraction,
                b_marked_legacy=legacy_mark,b_marked_new=new_mark,b_net_package=legacy_mark+new_mark-a['b_rights'],
                b_marked_recovery=legacy_mark/a['b_claim'],b_full_par_equity=a['b_claim']/legacy_fraction)

def main():
    results={name:calculate(change) for name,change in {
      'blocked':{'funding_case':0},'existing_only':{'funding_case':1},'upsize_assumed':{'funding_case':2},
      'extension_fails':{'funding_case':2,'maturity_case':0},'burn_down':{'burn':250},'burn_up':{'burn':150}}.items()}
    (ROOT/'outputs/results.json').write_text(json.dumps(results,indent=2)+'\n')
    b=results['upsize_assumed'];print(json.dumps({k:b[k] for k in ('ending_cash','minimum_cash','ss_claim','b_legacy_value','b_legacy_fraction','b_full_par_equity')},indent=2))

if __name__=='__main__':main()
