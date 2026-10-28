"""Build with the documented artifact-tool runtime; recalc in LibreOffice afterwards."""
import os,subprocess,json
from pathlib import Path
from assumptions import CURVES,ASOF,INPUTS,SOURCES
from engine import calculate
HERE=Path(__file__).parent
node=os.environ.get('NODE',str(Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node'))
(HERE/'data/build_inputs.json').write_text(json.dumps({'curve':CURVES['curves'][ASOF],'asof':ASOF,'inputs':INPUTS,'sources':SOURCES,'expected':calculate()},indent=2))
subprocess.run([node,str(HERE/'build_excel.mjs')],cwd=HERE,check=True)
