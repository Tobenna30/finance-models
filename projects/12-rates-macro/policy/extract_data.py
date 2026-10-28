import pathlib,openpyxl,datetime,csv,hashlib,json
import argparse
parser=argparse.ArgumentParser();parser.add_argument('--cache-dir',type=pathlib.Path,required=True);args=parser.parse_args()
src=args.cache_dir;out=pathlib.Path(__file__).parent/'data'
series={};snapshot=[]
for group,kind in [('glcnominalddata','gilt'),('oisddata','ois'),('latest','both')]:
 for f in sorted((src/group).glob('*.xlsx')):
  if group!='latest' and not ('2016' in f.name or 'present' in f.name):continue
  k='ois' if f.name.startswith('OIS') else 'gilt'
  if group=='latest' and not (f.name.startswith('OIS') or f.name.startswith('GLC Nominal')):continue
  w=openpyxl.load_workbook(f,read_only=True,data_only=True)
  for sn,tag in [('1. fwds, short end','fwd'),('3. spot, short end','shortspot'),('4. spot curve','spot')]:
   rows=list(w[sn].values);tenors=rows[3]
   for row in rows[5:]:
    if not isinstance(row[0],datetime.datetime) or row[0]<datetime.datetime(2020,1,1) or row[0]>datetime.datetime(2026,10,27):continue
    date=row[0].date().isoformat()
    for i,(t,v) in enumerate(zip(tenors[1:],row[1:]),1):
     if not isinstance(t,(int,float)) or not isinstance(v,(int,float)):continue
     if date=='2026-10-27' and ((k=='ois' and tag=='shortspot') or (k=='gilt' and tag=='spot')):
      snapshot.append([k,tag,round(t,8),v])
     wanted=(k=='ois' and tag=='fwd' and abs(t-1)<1e-6) or (k=='gilt' and tag=='spot' and (abs(t-2)<1e-6 or abs(t-10)<1e-6))
     if wanted:series.setdefault(date,{})[f'{k}_{tag}_{round(t)}']=v
with (out/'daily_curves.csv').open('w') as f:
 w=csv.writer(f,lineterminator="\n");w.writerow(['date','ois_fwd_1','gilt_spot_2','gilt_spot_10'])
 for d,r in sorted(series.items()):
  if len(r)==3:w.writerow([d,r['ois_fwd_1'],r['gilt_spot_2'],r['gilt_spot_10']])
with (out/'snapshot.csv').open('w') as f:
 w=csv.writer(f,lineterminator="\n");w.writerow(['curve','type','years','rate_pct']);w.writerows(sorted(set(tuple(x) for x in snapshot)))
manifest=[{'file':f.name,'url':'https://www.bankofengland.co.uk/-/media/boe/files/statistics/yield-curves/'+('latest-yield-curve-data' if f.stem=='latest' else f.stem)+'.zip?download=1','sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in src.glob('*.zip')]
(out/'curve_manifest.json').write_text(json.dumps({'retrieved':'2026-10-28','archives':manifest,'extraction':'2016-24 and 2025-present archives, current-month overrides; date >=2020, <=2026-10-27; percent continuous rates; annual forward 1y and spot 2/10y; snapshot OIS monthly spots and gilt half-year spots'},indent=2))
print('extracted',len(series),len(snapshot))
