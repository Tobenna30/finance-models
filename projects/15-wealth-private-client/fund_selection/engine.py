from .assumptions import INPUTS

def calculate(gross_return=None, use_gross_fees=False):
    a={k:v[0] for k,v in INPUTS.items()}
    r=a['gross_return'] if gross_return is None else gross_return
    fi=a['i_gross_fee'] if use_gross_fees else a['i_net_fee']
    fr=a['r_gross_fee'] if use_gross_fees else a['r_net_fee']
    return dict(fee_gap_bp=(fr-fi)*10000,annual_fee_gap=a['capital']*(fr-fi),
       i_end=a['capital']*(1+r-fi)**a['years'],r_end=a['capital']*(1+r-fr)**a['years'],
       i_eligible=bool(a['family_institutional'] and a['capital']>=a['i_minimum']),
       r_minimum_met=a['capital']>=a['r_minimum'],
       shock_100bp=-a['duration']*.01,
       call='PASS Class I for this retail family; retain Class R only for further suitability review')
