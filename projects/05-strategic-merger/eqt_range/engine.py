"""Constant-earnings merger lens, not a forecast or SEC pro forma statement."""
import json
from .assumptions import ROOT, values

def calculate(overrides=None):
    a = values()
    a.update(overrides or {})
    if a['case'] not in (1, 2, 3):
        raise ValueError('case must be 1, 2 or 3')
    if min(a['eqt_shares'], a['rrc_shares'], a['life'], a['discount']) <= 0 or not 0 <= a['tax'] < 1:
        raise ValueError('positive shares, life and discount; tax in [0,1) required')
    if a['ratio'] < 0 or not 0 <= a['ramp1'] <= 1 or not 0 <= a['cost1'] <= 1:
        raise ValueError('invalid ratio, synergy ramp or integration allocation')
    case = ('down', 'base', 'up')[int(a['case']) - 1]
    r_mult, s_mult = a['r_' + case], a['s_' + case]
    ltm = {k: a[k+'25'] + a[k+'126'] - a[k+'125'] for k in ('e_adj','e_gaap','r_adj','r_gaap','r_sbc')}
    keep_sbc = ltm['r_sbc'] * (1-a['tax'])
    r_normal = (ltm['r_adj'] - keep_sbc) * r_mult
    e_eps = ltm['e_adj'] / a['eqt_shares']
    issued = a['rrc_shares'] * a['ratio']
    shares = a['eqt_shares'] + issued
    annual_da = a['stepup'] / a['life']
    years = []
    for y in range(1, 4):
        synergy = a['synergy'] * s_mult * (a['ramp1'] if y == 1 else 1)
        cost = a['integration'] * (a['cost1'] if y == 1 else 1-a['cost1'] if y == 2 else 0)
        fees = a['fees'] if y == 1 else 0
        recurring = ltm['e_adj'] + r_normal + (synergy-annual_da)*(1-a['tax'])
        incl_costs = recurring - cost*(1-a['tax']) - fees
        company = ltm['e_adj'] + ltm['r_adj']*r_mult + synergy*(1-a['tax'])
        gaap = ltm['e_gaap'] + ltm['r_gaap']*r_mult + (synergy-annual_da-cost)*(1-a['tax']) - fees
        years.append(dict(year=y, synergy=synergy, integration=cost, fees=fees,
                          recurring_ni=recurring, recurring_eps=recurring/shares,
                          recurring_accretion=(recurring/shares)/e_eps-1,
                          inclusive_ni=incl_costs, inclusive_eps=incl_costs/shares,
                          inclusive_accretion=(incl_costs/shares)/e_eps-1,
                          company_eps=company/shares, company_accretion=(company/shares)/e_eps-1,
                          gaap_lens_eps=gaap/shares,
                          gaap_lens_accretion=(gaap/shares)/(ltm['e_gaap']/a['eqt_shares'])-1))
    d, tax = a['discount'], a['tax']
    # End-year cash timing. All synergies assumed cash with no incremental capex.
    unit_pv = (1-tax)*(a['ramp1']/(1+d)+1/(d*(1+d)))
    finite_unit = (1-tax)*sum((a['ramp1'] if y==1 else 1)/(1+d)**y for y in range(1,16))
    cost_pv = a['integration']*(1-tax)*(a['cost1']/(1+d)+(1-a['cost1'])/(1+d)**2)+a['fees']
    gross_pv = a['synergy']*s_mult*unit_pv
    offer = a['ratio']*a['eqt_price']
    premium = (offer-a['rrc_price'])*a['rrc_shares']
    breakeven = (e_eps*issued-r_normal)/(1-tax)+annual_da
    return dict(case=case, ltm=ltm, r_normal=r_normal, eqt_eps=e_eps, new_shares=issued,
                total_shares=shares, target_ownership=issued/shares, annual_da=annual_da,
                offer_price=offer, equity_consideration=offer*a['rrc_shares'], premium=premium,
                premium_pct=offer/a['rrc_price']-1, years=years,
                no_synergy_accretion=((ltm['e_adj']+r_normal-annual_da*(1-tax))/shares)/e_eps-1,
                eps_breakeven_synergy=breakeven, cost_pv=cost_pv, gross_synergy_pv=gross_pv,
                net_synergy_pv=gross_pv-cost_pv, value_surplus=gross_pv-cost_pv-premium,
                finite_surplus=a['synergy']*s_mult*finite_unit-cost_pv-premium,
                value_breakeven_synergy=(premium+cost_pv)/unit_pv,
                max_value_ratio=(a['rrc_price']+(gross_pv-cost_pv)/a['rrc_shares'])/a['eqt_price'])

def main():
    out = ROOT/'outputs'/'results.json'
    out.parent.mkdir(exist_ok=True)
    result = {c: calculate({'case': i}) for i,c in enumerate(('down','base','up'), 1)}
    out.write_text(json.dumps(result, indent=2)+'\n')
    b = result['base']
    print(json.dumps({k:b[k] for k in ('eqt_eps','offer_price','eps_breakeven_synergy','value_breakeven_synergy','value_surplus','max_value_ratio')}, indent=2))
    print('Year 1 including costs / year 3 recurring:', b['years'][0]['inclusive_accretion'], b['years'][2]['recurring_accretion'])

if __name__ == '__main__':
    main()
