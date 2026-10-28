import os,subprocess,tempfile,shutil
from pathlib import Path
from build_excel import RAW,OUT
with tempfile.TemporaryDirectory() as d:
 p=Path(d);subprocess.run([os.environ.get('SOFFICE','soffice'),'-env:UserInstallation='+(p/'profile').as_uri(),'--headless','--convert-to','xlsx','--outdir',str(p),str(RAW)],check=True,capture_output=True)
 shutil.copy(p/RAW.name,OUT)
RAW.unlink();print(OUT)
