"""Funding economics, not valuation of Meta or an executable securities quote."""
import json
from .assumptions import ROOT, values, CLOSE, SETTLE, CONVERT, DIVIDEND_DATES

def year30(start,end):
    """Analyst 30/360 approximation; final prospectus day count unverified."""
    return ((end.year-start.year)*360+(end.month-start.month)*30+min(end.day,30)-min(start.day,30))/360

def bond_price(coupon,yield_,term):
    return sum(coupon*100/(1+yield_)**y for y in range(1,term+1))+100/(1+yield_)**term

def solve_yield(price,coupon,term):
    lo,hi=-.5,1.
    for _ in range(150):
        m=(lo+hi)/2
        if bond_price(coupon,m,term)>price:lo=m
        else:hi=m
    return (lo+hi)/2

def calculate(overrides=None):
    a=values();a.update(overrides or {})
    if a['case'] not in (1,2,3) or a['bond_term']!=5:
        raise ValueError('invalid case or bond term')
    if min(a['deposit_price'],a['deposits_per_pref'],a['liquidation'],a['offer_price'],a['forward_price'])<=0 or a['bond_yield']<=-1:
        raise ValueError('positive prices and yield above -100% required')
    if any(not 0<=a[k]<1 for k in ('pref_fee','equity_fee','bond_fee','tax')) or a['forward_change']<=-1:
        raise ValueError('invalid fees, tax or forward adjustment')
    p=a[('price_down','price_base','price_up')[int(a['case'])-1]]
    if p<=0 or a['min_rate']<=0 or a['max_rate']<a['min_rate']:raise ValueError('invalid conversion inputs')
    pref_gross=a['deposits']*a['deposit_price'];pref_count=a['deposits']/a['deposits_per_pref']
    pref_net=pref_gross*(1-a['pref_fee'])
    forward_net=a['common_shares']*a['forward_price']*(1+a['forward_change'])-a['forward_expense']
    net=pref_net+forward_net
    common_gross=a['common_shares']*a['offer_price']
    coupons=[];previous=CLOSE
    for date in DIVIDEND_DATES:
        amount=pref_count*a['liquidation']*a['dividend']*year30(previous,date)
        coupons.append({'date':date.isoformat(),'amount':amount});previous=date
    rate=round(max(a['min_rate'],min(a['max_rate'],a['liquidation']/p)),4)
    conversion_shares=pref_count*rate
    converted_value=conversion_shares*p
    div_total=sum(c['amount'] for c in coupons)
    div_pv=sum(c['amount']/(1+a['investor_hurdle'])**((__import__('datetime').date.fromisoformat(c['date'])-CLOSE).days/365) for c in coupons)
    required_value=(pref_gross-div_pv)*(1+a['investor_hurdle'])**((CONVERT-CLOSE).days/365)
    # Fixed-value middle zone means no unique stock price there. Outside it use
    # the appropriate capped conversion rate for a deterministic hurdle.
    hurdle_price=required_value/(pref_count*(a['min_rate'] if required_value>pref_count*a['liquidation'] else a['max_rate']))
    equity_gross=net/(1-a['equity_fee']);equity_shares=equity_gross/a['offer_price']
    face=net/(1-a['bond_fee']);coupon_cash=face*a['bond_coupon']
    effective=solve_yield(100*(1-a['bond_fee']),a['bond_coupon'],int(a['bond_term']))
    schedule=[];carrying=net
    for y in range(1,int(a['bond_term'])+1):
        interest=carrying*effective;amort=interest-coupon_cash
        repayment=face if y==a['bond_term'] else 0
        end=carrying+amort-repayment
        schedule.append(dict(year=y,opening=carrying,coupon=coupon_cash,interest=interest,amortisation=amort,principal=repayment,closing=end));carrying=end
    bridge_interest=forward_net*a['bridge_rate']*(SETTLE-CLOSE).days/365
    bridge_fee=forward_net*a['bridge_fee']
    # Sizing comparison: issuance proceeds retained as cash, before deployment.
    # Net debt carrying value deducts new fees. No historic pro forma rollforward.
    positions={}
    for name,cash_in,liab_in,equity_in in [('package_close',pref_net,0,pref_net),('package_settled',net,0,net),('immediate_equity',net,0,net),('straight_debt',net,net,0)]:
        positions[name]=dict(cash=a['cash']+cash_in,assets=a['assets']+cash_in,liabilities=a['liabilities']+liab_in,equity=a['equity']+equity_in)
    return dict(price=p,pref_gross=pref_gross,pref_count=pref_count,pref_net=pref_net,common_gross=common_gross,
                gross_package=pref_gross+common_gross,forward_net=forward_net,net_total=net,initial_cash=pref_net,
                deferred_share=forward_net/net,annual_dividend=pref_count*a['liquidation']*a['dividend'],dividends=coupons,dividend_total=div_total,
                min_price=a['liquidation']/a['max_rate'],max_price=a['liquidation']/a['min_rate'],conversion_rate=rate,
                conversion_shares=conversion_shares,total_new_initial_term_shares=a['common_shares']+conversion_shares,
                converted_value=converted_value,pref_total_return=(converted_value+div_total)/pref_gross-1,
                dividend_pv=div_pv,required_terminal_value=required_value,investor_hurdle_price=hurdle_price,
                equity_gross=equity_gross,equity_shares=equity_shares,bond_face=face,bond_coupon_cash=coupon_cash,
                bond_after_tax_coupon=coupon_cash*(1-a['tax']),bond_effective_yield=effective,bond_price=bond_price(a['bond_coupon'],a['bond_yield'],int(a['bond_term'])),
                bond_schedule=schedule,bridge_interest=bridge_interest,bridge_fee=bridge_fee,
                bridge_after_tax_cost=(bridge_interest+bridge_fee)*(1-a['tax']),positions=positions,
                historical_fcf=a['ocf9']-a['ppe9']-a['lease9'],liquid_resources=a['cash']+a['securities'],
                capex_remaining_low=a['capex_low']-a['ppe9']-a['lease9'],capex_remaining_high=a['capex_high']-a['ppe9']-a['lease9'])

def main():
    cases={label:calculate({'case':i}) for i,label in enumerate(('down','base','up'),1)}
    (ROOT/'outputs'/'results.json').write_text(json.dumps(cases,indent=2)+'\n')
    print(json.dumps({k:cases['base'][k] for k in ('initial_cash','forward_net','net_total','annual_dividend','dividend_total','bond_face','bond_after_tax_coupon','bridge_after_tax_cost')},indent=2))

if __name__=='__main__':main()
