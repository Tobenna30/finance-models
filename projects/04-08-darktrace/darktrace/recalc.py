"""Recalculate the raw openpyxl workbook in LibreOffice headless so every formula has a cached value.
Run from projects/04-08-darktrace: python -m darktrace.recalc  ->  models/Darktrace_04_08.xlsx"""
import shutil, subprocess, tempfile
from pathlib import Path
from .build_excel import RAW, OUT


def main():
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["soffice", "--headless", "--calc", "--convert-to", "xlsx:Calc MS Excel 2007 XML",
                        "--outdir", tmp, str(RAW)], check=True, capture_output=True, timeout=170)
        shutil.copy(Path(tmp) / RAW.name, OUT)
    RAW.unlink()
    print("recalculated", OUT)


if __name__ == "__main__":
    main()
