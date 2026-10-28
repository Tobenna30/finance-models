"""Download exact source archives into a caller-supplied cache; verify frozen hashes.
Usage: python fetch_data.py /tmp/rates-cache. Then extract_data.py --cache-dir ...
Changed archives fail validation: update and review a new dated snapshot explicitly.
"""
import sys,hashlib,json,urllib.request,zipfile
from pathlib import Path
root=Path(sys.argv[1]);root.mkdir(parents=True,exist_ok=True)
m=json.loads((Path(__file__).parent/'data/manifest.json').read_text())
for record in m['archives']+m['fred']:
    name=record.get('file',record.get('series','')+'.csv')
    b=urllib.request.urlopen(urllib.request.Request(record['url'],headers={'User-Agent':'Mozilla/5.0'}),timeout=90).read()
    if hashlib.sha256(b).hexdigest()!=record['sha256']:raise ValueError('Source changed: '+name+'; preserve committed snapshot and review new vintage')
    f=root/name;f.write_bytes(b)
    if f.suffix=='.zip':zipfile.ZipFile(f).extractall(root/f.stem)
