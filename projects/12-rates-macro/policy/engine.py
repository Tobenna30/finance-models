"""Curve accounting and daily OLS. No network or spreadsheet dependency."""
import calendar, datetime as dt, json, math
import numpy as np
import pandas as pd
import assumptions as A

def curves():
    return pd.read_csv(A.DATA/'daily_curves.csv',index_col='date')

def snapshot(kind, tag):
    d=pd.read_csv(A.DATA/'snapshot.csv');d=d[(d.curve==kind)&(d.type==tag)].sort_values('years')
    return d.years.to_numpy(),d.rate_pct.to_numpy()/100

def zero(kind,t):
    x,y=snapshot(kind,'shortspot' if kind=='ois' else 'spot')
    # Flat zero below the shortest observed tenor is an explicit extrapolation.
    return float(np.interp(t,x,y))

def integral(t):
    return t*zero('ois',t) if t else 0.0

def meeting_path():
    today=dt.date.fromisoformat(A.ASOF);end=today+dt.timedelta(days=365);result=[]
    for i,date in enumerate(A.MPC_FUTURE[:-1]):
        start=dt.date.fromisoformat(date);stop=min(dt.date.fromisoformat(A.MPC_FUTURE[i+1]),end)
        if start>=end:break
        t1=(start-today).days/365;t2=(stop-today).days/365
        # Integrated forward from published continuous zero rates. Convert to daily
        # compounded overnight equivalent, then add assumed Bank Rate/SONIA basis.
        f=(integral(t2)-integral(t1))/(t2-t1)
        rate=365*math.expm1(f/365)*100+A.BASIS_BP/100
        result.append({'date':date,'end':stop.isoformat(),'t1':t1,'t2':t2,'market':rate,'scenario':A.SCENARIO_END})
    return result

def coupon_dates(maturity,asof):
    end=dt.date.fromisoformat(maturity);dates=[];year,month=end.year,end.month
    while True:
        d=dt.date(year,month,min(end.day,calendar.monthrange(year,month)[1]))
        if d<=asof:break
        dates.append(d)
        month-=6
        if month<=0:year-=1;month+=12
    return sorted(dates)

def bond_cashflows(bond):
    isin,coupon,maturity=bond;today=dt.date.fromisoformat(A.ASOF)
    return [((d-today).days/365,coupon/2+(100 if d.isoformat()==maturity else 0)) for d in coupon_dates(maturity,today)]

def bond_price(cf,shift=0,elapsed=0,roll=True):
    return sum(c*math.exp(-(zero('gilt',t-elapsed if roll else t)+shift)*(t-elapsed)) for t,c in cf if t>elapsed)

def bond_stats(bond):
    cf=bond_cashflows(bond);p=bond_price(cf)
    dv=(bond_price(cf,-.0001)-bond_price(cf,.0001))/2
    # Frozen original cash-flow discount rates isolates carry; ageing down the
    # unchanged spot curve adds roll. Coupon receipts are held as cash to horizon.
    coupons=sum(c for t,c in cf if t<=A.HORIZON)
    carry=bond_price(cf,elapsed=A.HORIZON,roll=False)+coupons-p
    rolled=bond_price(cf,elapsed=A.HORIZON)+coupons-p
    financing=p*A.BANK_RATE/100*A.HORIZON
    return {'isin':bond[0],'price':p,'dv01_per100':dv,'carry':carry-financing,'roll':rolled-carry,'cf':cf}

def ols(x,y,lags=A.HAC_LAGS):
    x=np.asarray(x,float);y=np.asarray(y,float);n=len(x)
    if n<max(8,lags+3) or np.std(x)==0:return {'n':n,'slope':None,'t':None,'r2':None}
    X=np.column_stack([np.ones(n),x]);inv=np.linalg.inv(X.T@X);b=inv@X.T@y;e=y-X@b;u=X*e[:,None];meat=u.T@u
    for l in range(1,min(lags,n-1)+1):
        v=u[l:].T@u[:-l];meat+=(1-l/(lags+1))*(v+v.T)
    cov=inv@meat@inv*n/(n-2)
    return {'n':n,'slope':float(b[1]),'t':float(b[1]/math.sqrt(cov[1,1])),'r2':float(1-e@e/((y-y.mean())@(y-y.mean())))}

def fx_panel():
    d=pd.read_csv(A.DATA/'fx_rates.csv',index_col='date')
    d=d.join(curves()[['ois_fwd_1']],how='inner').dropna()
    # Changes are made BEFORE filtering observations. No invented holiday returns.
    d['repricing_10bp']=d.ois_fwd_1.diff()*10
    d['GBP_USD']=np.log(d.gbp_usd).diff()*100
    d['GBP_EUR']=np.log(d.gbp_usd/d.eur_usd).diff()*100
    return d.dropna()

def fx_results():
    d=fx_panel();events=pd.read_csv(A.DATA/'events.csv');result={}
    for pair in ['GBP_USD','GBP_EUR']:
        reg={}
        for key,mask in [('full',np.ones(len(d),bool)),('ex2022',~d.index.str.startswith('2022')),('LDI',(d.index>=A.REPLAY_START)&(d.index<=A.REPLAY_END))]:
            q=d.loc[mask];reg[key]=ols(q.repricing_10bp,q[pair])
        for typ in ['MPC','CPI']:
            q=d.loc[d.index.isin(events.loc[events.type==typ,'date'])];reg[typ]=ols(q.repricing_10bp,q[pair])
        tail=d.iloc[-A.VOL_DAYS:];vol=float(tail[pair].std(ddof=1)*math.sqrt(A.VOL_DAYS));foreign=float(d.iloc[-1].sofr if pair=='GBP_USD' else d.iloc[-1].estr)
        carry=A.BANK_RATE-foreign
        result[pair]={'regressions':reg,'carry_pct':carry,'vol_pct':vol,'carry_to_vol':carry/vol,'asof':d.index[-1]}
    return result

def results():
    h=curves();row=h.loc[A.ASOF];spread=(row.gilt_spot_10-row.gilt_spot_2)*100
    # Hold-policy scenario versus 12m terminal market rate determines the
    # direction, not a fitted return optimiser: lower scenario => steepener.
    implied=365*math.expm1(row.ois_fwd_1/100/365)*100+A.BASIS_BP/100
    direction=1 if A.SCENARIO_END<implied else -1
    bonds=[bond_stats(b) for b in A.BONDS]
    for i,b in enumerate(bonds):b['nominal_gbp']=A.BUDGET/2/b['dv01_per100']*100*(direction if i==0 else -direction)
    carry=sum(b['nominal_gbp']/100*b['carry'] for b in bonds)
    roll=sum(b['nominal_gbp']/100*b['roll'] for b in bonds)
    stress={}
    for label,end in [('peak',A.REPLAY_PEAK),('end',A.REPLAY_END)]:
        delta=(h.loc[end,['gilt_spot_2','gilt_spot_10']]-h.loc[A.REPLAY_START,['gilt_spot_2','gilt_spot_10']])/100
        pnl=sum(b['nominal_gbp']/100*(bond_price(b['cf'],float(delta.iloc[i]))-b['price']) for i,b in enumerate(bonds))
        stress[label]={'end':end,'shocks_bp':[float(v*10000) for v in delta],'pnl_gbp':pnl}
    return {'asof':A.ASOF,'implied_bank_rate_12m_pct':implied,'implied_cuts_bp':(A.BANK_RATE-implied)*100,'scenario_cuts_bp':(A.BANK_RATE-A.SCENARIO_END)*100,'spread_bp':float(spread),'direction':direction,'trade':'2s10s steepener' if direction==1 else '2s10s flattener','stop_bp':float(spread-direction*A.STOP_BP),'target_bp':float(spread+direction*A.TARGET_BP),'bonds':bonds,'carry_gbp':carry,'roll_gbp':roll,'carry_roll_bp':(carry+roll)/(A.BUDGET/2),'replay':stress,'meetings':meeting_path(),'fx':fx_results()}

if __name__=='__main__':print(json.dumps(results(),indent=2))
