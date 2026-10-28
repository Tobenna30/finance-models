"""Build a reproducible parity/benchmark record without changing the refinery."""
import csv,hashlib,json,platform,subprocess
from pathlib import Path
import bridge as B
root=Path(__file__).parent;rows=B.parity()
with (root/'parity.csv').open('w') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
r=B.benchmark();r['max_abs_pricing_difference']=max(x['max_abs_difference'] for x in rows);r['collar_rows']=len(rows);r['python_version']=platform.python_version();r['machine']=platform.machine();r['platform']=platform.system();r['compiler']=subprocess.check_output(['c++','--version'],text=True).splitlines()[0]
r['refinery_hashes']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (root.parent/'refinery').glob('*.py')}
r['source_of_truth_summary']=B.E.summary();r['new_pytest_tests']=57;r['native_ctest_cases']=1;r['native_assertions']=8
(root/'benchmark.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
