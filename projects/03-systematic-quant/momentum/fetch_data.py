"""Frozen French monthly decile/factor extraction. No individual-security data.
python fetch_data.py [--download]: optionally fetch, then parse first monthly table.
Downloads must match frozen SHA256; changed releases require explicit review.
"""
from pathlib import Path
import csv,hashlib,io,json,re,sys,urllib.request,zipfile
DATA=Path(__file__).parent/'data'
FILES=['10_Portfolios_Prior_12_2','F-F_Momentum_Factor']

def extract():
    manifest=[];tables=[]
    for name in FILES:
        url='https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/'+name+'_CSV.zip';p=DATA/(name+'.zip')
        if '--download' in sys.argv:
            b=urllib.request.urlopen(url,timeout=60).read()
            old=json.loads((DATA/'manifest.json').read_text()) if (DATA/'manifest.json').exists() else []
            target=next((x['sha256'] for x in old if x['name']==name),None)
            if target and hashlib.sha256(b).hexdigest()!=target:raise ValueError('New source vintage: review before replacing frozen data')
            p.write_bytes(b)
        b=p.read_bytes();z=zipfile.ZipFile(io.BytesIO(b));text=z.read(z.namelist()[0]).decode('utf-8-sig');rows=[];started=False
        for line in text.splitlines():
            if re.match(r'^\d{6},',line):
                started=True;r=next(csv.reader([line]));v=[float(x) for x in r[1:]]
                if any(x in [-99.99,-999] for x in v):raise ValueError('Missing monthly return')
                if r[0]<='202609':rows.append([r[0][:4]+'-'+r[0][4:6]]+[x/100 for x in v])
            elif started:break
        tables.append(rows);manifest.append({'name':name,'url':url,'sha256':hashlib.sha256(b).hexdigest(),'vintage':'202609 CRSP','retrieved':'2026-10-28','rows':len(rows),'first':rows[0][0],'last':rows[-1][0]})
    factor={row[0]:row[1] for row in tables[1]}
    with (DATA/'monthly.csv').open('w') as f:
        w=csv.writer(f,lineterminator='\n');w.writerow(['month']+['decile'+str(i) for i in range(1,11)]+['mom'])
        for row in tables[0]:
            if row[0] in factor:w.writerow(row+[factor[row[0]]])
    (DATA/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
if __name__=='__main__':extract()
