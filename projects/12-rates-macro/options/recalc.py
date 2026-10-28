"""Native recalculation without overwriting the input file in place."""
import os,subprocess,tempfile,shutil
from pathlib import Path
book=Path(__file__).resolve().parent.parent/'models/Sterling_Receiver_Options.xlsx'
soffice=os.environ.get('SOFFICE','soffice')
with tempfile.TemporaryDirectory(prefix='receiver-recalc-') as temp:
 out=Path(temp);profile=out/'profile'
 subprocess.run([soffice,f'-env:UserInstallation={profile.as_uri()}','--headless','--convert-to','xlsx','--outdir',str(out),str(book)],check=True)
 result=out/book.name
 if not result.exists():raise RuntimeError('LibreOffice did not export a workbook')
 shutil.copy2(result,book)
