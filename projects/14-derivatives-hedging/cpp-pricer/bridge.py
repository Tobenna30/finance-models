"""Small CLI bridge. All market inputs come from unchanged refinery Python modules."""
import math,os,random,subprocess,sys,time,statistics
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from refinery import engine as E
from refinery import assumptions as A

def executable():
    return os.environ.get('REFINERY_PRICER','/tmp/refinery_pricer')

def run(commands,binary=None):
    r=subprocess.run([str(binary or executable())],input=commands,text=True,capture_output=True,check=True)
    return [[float(x) for x in line.split()] for line in r.stdout.splitlines()]

def quotes(model,f,k,vol,t,r,call=True,binary=None):
    code='N' if model=='bachelier' else 'B'
    return run(f'price {code} {f:.17g} {k:.17g} {vol:.17g} {t:.17g} {r:.17g} {int(call)}\n',binary)[0]

def parity(binary=None):
    rows=[]
    for model in ['bachelier','black76']:
        code='N' if model=='bachelier' else 'B';strike=E.strikes(model)
        for p in A.PRODUCTS:
            f=A.FORWARD[p];v=A.NORMAL_VOL[p] if model=='bachelier' else A.NORMAL_VOL[p]/f
            for month,days,t in E.months():
                ref=strike[p][month-1];kp=ref['put'];kc=run(f'strike {code} {f:.17g} {kp:.17g} {v:.17g} {t:.17g} {A.USD_RATE:.17g} 1\n',binary)[0][0]
                pp=quotes(model,f,kp,v,t,A.USD_RATE,False,binary)[0];cp=quotes(model,f,kc,v,t,A.USD_RATE,True,binary)[0]
                price=E.bachelier if model=='bachelier' else E.black76
                errors=[abs(kc-ref['call']),abs(pp-price(f,kp,v,t,A.USD_RATE,False)),abs(cp-price(f,ref['call'],v,t,A.USD_RATE,True))]
                rows.append(dict(model=model,product=p,month=month,put_strike=kp,call_strike_python=ref['call'],call_strike_cpp=kc,put_premium_cpp=pp,call_premium_cpp=cp,max_abs_difference=max(errors)))
    return rows

def inputs(n=A.MC_DRAWS,seed=A.MC_SEED):
    rng=random.Random(seed);shocks=[]
    for _ in range(n):
        z1=rng.gauss(0,1);z2=A.MC_CORR*z1+math.sqrt(1-A.MC_CORR**2)*rng.gauss(0,1);shocks.append((z1,z2))
    k=E.strikes();t=sum(x[2] for x in E.months())/12
    products=[(A.FORWARD[p],A.NORMAL_VOL[p]*math.sqrt(t),sum(E.budget_bbl(p,n) for _,n,_ in E.months()),k[p][0]['put'],k[p][0]['call']) for p in A.PRODUCTS]
    return shocks,products

def python_kernel(shocks,products):
    u=[];h=[];budget=E.annual_budget_margin();cover=A.COVERS[2]
    for z in shocks:
        unhedged=hedged=0.0
        for a,xz in zip(products,z):
            f,s,b,kp,kc=a;x=f+s*xz
            unhedged+=b*x;hedged+=b*x+cover*b*(max(kp-x,0)-max(x-kc,0))
        u.append(unhedged/1e6/budget-1);h.append(hedged/1e6/budget-1)
    u.sort();h.sort();i=int(.05*len(shocks))
    return [sum(u)/len(u),sum(h)/len(h),u[i],h[i]]

def mc_command(shocks,products,repeats):
    return f'mc {len(shocks)} {repeats} {A.COVERS[2]:.17g} {E.annual_budget_margin():.17g}\n'+'\n'.join(' '.join(format(v,'.17g') for v in a) for a in products+shocks)+'\n'

def benchmark(binary=None,repeats=7):
    shocks,products=inputs();py=python_kernel(shocks,products);times=[]
    for _ in range(repeats):
        start=time.perf_counter();python_kernel(shocks,products);times.append(time.perf_counter()-start)
    command=mc_command(shocks,products,repeats);start=time.perf_counter();cpp=run(command,binary)[0];wall=time.perf_counter()-start
    start=time.perf_counter();original=E.monte_carlo();original_seconds=time.perf_counter()-start
    expected=[original[k] for k in ['unhedged_mean','hedged_mean','unhedged_p05','hedged_p05']]
    return dict(paths=len(shocks),seed=A.MC_SEED,repeats=repeats,python_kernel_median_seconds=statistics.median(times),cpp_kernel_median_seconds=cpp[4],kernel_speedup=statistics.median(times)/cpp[4],cpp_cli_wall_seconds=wall,original_python_seconds=original_seconds,python_kernel_results=py,cpp_results=cpp[:4],original_python_results=expected,max_mc_difference=max(abs(a-b) for a,b in zip(cpp[:4],expected)),method='Same pre-generated Python Random.gauss shocks, correlation and inputs; medians include pricing, sorting and means, exclude RNG, I/O, strike solving. CLI wall covers all repeats plus parsing. Hardware-specific, not a production latency claim.')
