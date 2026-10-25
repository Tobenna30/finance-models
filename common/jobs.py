"""Weekly hiring tracker: open roles at LSEG and FactSet by function, from their Workday career sites.

Run: python -m common.jobs  -> appends data/jobs_history.csv and writes data/jobs_latest.csv
Only public job listings are read; requests are paced politely.
"""
import csv, json, re, sys, time, urllib.request
from datetime import date
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data"
UA = "Mozilla/5.0 (research project; contact agubuchetobe@gmail.com)"
COMPANIES = {   # name: list of candidate Workday (host, tenant, site); first that answers wins
    "LSEG": [("lseg.wd3.myworkdayjobs.com", "lseg", "Careers")],
    "FactSet": [("factset.wd1.myworkdayjobs.com", "factset", "FactSetCareers"),
                ("factset.wd1.myworkdayjobs.com", "factset", "External"),
                ("factset.wd108.myworkdayjobs.com", "factset", "FactSetCareers")],
}
CATEGORIES = [   # first match wins, so order matters
    ("AI & data science", r"\bai\b|artificial intelligence|machine learning|\bml\b|genai|\bllm|data scien|\bnlp\b|prompt"),
    ("Sales & client", r"sales|account (manager|executive|director)|client|business development|relationship|customer s|go-to-market|\bgtm\b|business director"),
    ("Engineering", r"engineer|developer|software|devops|\bsre\b|architect|cloud|platform|technolog|security|\bqa\b|test|c\+\+|servicenow|oracle|development manager"),
    ("Content & data ops", r"content|data analyst|data operations|research|editor|journalist|reporter|data steward|pricing|valuation|quantitative"),
    ("Product", r"product"),
    ("Operations", r"operations|clearing|onboarding|service|support|billing|kyc|supervision|resilience|live service|delivery|pmo|project|migration|integration"),
    ("Corporate", r"financ|accounting|controller|legal|\bhr\b|human resources|people|recruit|compliance|risk|audit|tax|treasury|procurement|marketing|communications|secretariat|reporting|vendor|records"),
]


def post(url, payload):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), method="POST",
                                 headers={"User-Agent": UA, "Content-Type": "application/json", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def classify(title: str) -> str:
    t = title.lower()
    for name, pat in CATEGORIES:
        if re.search(pat, t): return name
    return "Other"


def fetch(host, tenant, site):
    url = f"https://{host}/wday/cxs/{tenant}/{site}/jobs"
    first = post(url, {"appliedFacets": {}, "limit": 20, "offset": 0, "searchText": ""})
    total, jobs, off = first.get("total", 0), first.get("jobPostings", []), 20
    while off < total and off < 2000:
        time.sleep(0.5)
        jobs += post(url, {"appliedFacets": {}, "limit": 20, "offset": off, "searchText": ""}).get("jobPostings", [])
        off += 20
    return total, jobs, url


def main():
    DATA.mkdir(exist_ok=True)
    today = date.today().isoformat()
    latest, summary = [], []
    for co, cands in COMPANIES.items():
        for host, tenant, site in cands:
            try:
                total, jobs, url = fetch(host, tenant, site)
                break
            except Exception as e:  # try the next candidate
                print(co, host, site, "failed:", e, file=sys.stderr); total, jobs, url = None, [], None
        if total is None:
            summary.append({"date": today, "company": co, "total": "", "source": "unavailable"}); continue
        counts = {}
        for j in jobs:
            cat = classify(j.get("title", ""))
            counts[cat] = counts.get(cat, 0) + 1
            latest.append({"date": today, "company": co, "title": j.get("title"), "location": j.get("locationsText"),
                           "posted": j.get("postedOn"), "category": cat})
        row = {"date": today, "company": co, "total": total, "source": url}
        row.update({name: counts.get(name, 0) for name, _ in CATEGORIES + [("Other", "")]})
        summary.append(row); print(co, total, counts, file=sys.stderr)
    fields = ["date", "company", "total", "source"] + [n for n, _ in CATEGORIES] + ["Other"]
    hist = DATA / "jobs_history.csv"
    rows = list(csv.DictReader(hist.open())) if hist.exists() else []
    rows = [r for r in rows if r["date"] != today] + summary
    with hist.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore"); w.writeheader(); w.writerows(rows)
    if latest:
        with (DATA / "jobs_latest.csv").open("w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(latest[0].keys())); w.writeheader(); w.writerows(latest)


if __name__ == "__main__":
    main()
