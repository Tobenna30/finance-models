"""Curve-to-forward and Bachelier receiver comparison; no spreadsheet dependency."""
import math,bisect,json
try:
 from .assumptions import CURVES,ASOF,DEFAULTS
except ImportError:
 from assumptions import CURVES,ASOF,DEFAULTS
def cdf(x):return .5*(1+math.erf(x/math.sqrt(2)))
def pdf(x):return math.exp(-x*x/2)/math.sqrt(2*math.pi)
def df(t,shock=0):
 if t==0:return 1.
 curve=CURVES['curves'][ASOF];x=[v[0] for v in curve];y=[v[1]/100 for v in curve]
 if not x[0]<=t<=x[-1]:raise ValueError('Curve extrapolation prohibited')
 i=max(1,min(len(x)-1,bisect.bisect_left(x,t)))
 z=y[i-1]+(y[i]-y[i-1])*(t-x[i-1])/(x[i]-x[i-1])+shock/10000
 return math.exp(-z*t)
def put(f,k,sigma,t):
 if sigma<0 or t<0:raise ValueError('Invalid volatility or expiry')
 if sigma*t==0:return max(k-f,0.)
 s=sigma*math.sqrt(t);d=(k-f)/s
 return (k-f)*cdf(d)+s*pdf(d)
def calculate(**updates):
 p=DEFAULTS|updates
 n,t,tenor=p['notional'],p['expiry'],p['tenor']
 if n<=0 or t<1/12 or t>2 or tenor!=int(tenor) or not 1<=tenor<=10 or p['width_bp']<=0 or p['cost_bp']<0:
  raise ValueError('Invalid sizing, expiry, tenor, width or costs')
 if p['forward_mode'] not in (0,1) or p['vol_mode'] not in (0,1):raise ValueError('Invalid mode')
 if p['forward_mode'] or p['vol_mode']:
  if not p['quote_time'] or not p['quote_source']:raise ValueError('Dealer source and timestamp required')
 if p['forward_mode'] and p['dealer_forward'] is None:raise ValueError('Dealer forward missing')
 if p['vol_mode'] and (p['dealer_long_vol_bp'] is None or p['dealer_short_vol_bp'] is None):raise ValueError('Dealer volatility missing')
 vl=p['dealer_long_vol_bp'] if p['vol_mode'] else p['long_vol_bp']
 vs=p['dealer_short_vol_bp'] if p['vol_mode'] else p['short_vol_bp']
 if vl<0 or vs<0:raise ValueError('Negative volatility')
 a=sum(df(t+i,p['curve_shock_bp']) for i in range(1,int(tenor)+1))
 fcurve=(df(t,p['curve_shock_bp'])-df(t+tenor,p['curve_shock_bp']))/a
 f=p['dealer_forward'] if p['forward_mode'] else fcurve
 width=p['width_bp']/10000;k=f-width
 long=put(f,f,vl/10000,t);short=put(f,k,vs/10000,t);spread=long-short
 valid=0<=spread<=width
 # Separate strike vols can violate vertical-spread bounds; flag, never repair prices.
 delta=-.5 if vl>0 else -.5
 ds=-cdf((k-f)/(vs/10000*math.sqrt(t))) if vs>0 else 0.
 vg=n*a*math.sqrt(t)*pdf(0)/10000 if vl>0 else 0.
 vgs=n*a*math.sqrt(t)*pdf((k-f)/(vs/10000*math.sqrt(t)))/10000 if vs>0 else 0.
 pv01=n*a*.0001;cost=p['cost_bp'];shift=p['scenario_shift_bp'];rally=-shift
 return dict(asof=ASOF,forward=f,curve_forward=fcurve,annuity=a,pv01=pv01,long_vol_bp=vl,short_vol_bp=vs,
  long_strike=f,short_strike=k,outright_bp=long*10000,spread_bp=spread*10000,
  outright_debit=(long*10000+cost)*pv01,spread_debit=(spread*10000+cost)*pv01,
  spread_max_profit=(p['width_bp']-spread*10000-cost)*pv01,
  spread_breakeven_bp=spread*10000+cost,crossover_bp=p['width_bp']+(long-spread)*10000,
  outright_delta=delta*pv01,spread_delta=(delta-ds)*pv01,outright_vega=vg,spread_vega=vg-vgs,
  linear_pnl=(rally-cost)*pv01,outright_pnl=(max(rally,0)-long*10000-cost)*pv01,
  spread_pnl=(min(max(rally,0),p['width_bp'])-spread*10000-cost)*pv01,
  vertical_valid=valid,limited_profit_positive=(p['width_bp']-spread*10000-cost)>0,
  status='ILLUSTRATIVE INPUTS' if not p['vol_mode'] else 'DEALER INPUTS: verify schedule/settlement; not an automatic recommendation')
if __name__=='__main__':print(json.dumps(calculate(),indent=2))
