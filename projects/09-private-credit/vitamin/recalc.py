"""LibreOffice recalculation with cached results for parity tests."""
import os
import shutil
import subprocess
import tempfile
from .build_excel import RAW, OUT

def main():
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run([os.environ.get('SOFFICE','soffice'),'--headless','--calc','--convert-to',
                        'xlsx:Calc MS Excel 2007 XML','--outdir',tmp,str(RAW)],check=True,capture_output=True,timeout=170)
        shutil.copy(__import__('pathlib').Path(tmp)/RAW.name,OUT)
    RAW.unlink();print('recalculated',OUT)

if __name__=='__main__':main()
