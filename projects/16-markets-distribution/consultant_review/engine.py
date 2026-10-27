from .assumptions import FUND,BENCHMARK,SECTORS,REQUESTS

def calculate():
    return dict(excess_bp=[round((f-b)*100,8) for f,b in zip(FUND,BENCHMARK)],
       sector_active_pp={n:round(f-b,8) for n,f,b in SECTORS},
       fund_sector_total=sum(x[1] for x in SECTORS),benchmark_sector_total=sum(x[2] for x in SECTORS),
       open_requests=sum(x[2]=='Open' for x in REQUESTS),total_requests=len(REQUESTS),
       call='ESCALATE: quarterly outperformance is not evidence of persistent net outperformance; do not approve a mandate from this snapshot')
