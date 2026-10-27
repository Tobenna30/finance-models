"""Recalculate the raw openpyxl workbook in LibreOffice headless so every formula has a cached value.
Run from projects/14-derivatives-hedging: python -m refinery.recalc  ->  models/Refinery_Hedge.xlsx
Set SOFFICE to the LibreOffice binary if it is not on PATH."""
import os, shutil, subprocess, tempfile
from pathlib import Path
from .build_excel import RAW, OUT


def main():
    soffice = os.environ.get("SOFFICE", "soffice")
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run([soffice, "--headless", "--calc", "--convert-to", "xlsx:Calc MS Excel 2007 XML",
                        "--outdir", tmp, str(RAW)], check=True, capture_output=True, timeout=170)
        shutil.copy(Path(tmp) / RAW.name, OUT)
    RAW.unlink()
    print("recalculated", OUT)


if __name__ == "__main__":
    main()
