import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "projects" / "01-equity-pitch-kit"))

from lseg.engine import run, sotp, solve, KEYS  # noqa: E402
from lseg import assumptions as A  # noqa: E402


def test_balance_sheet_balances_every_year_every_scenario():
    for s in (1, 2, 3):
        r = run(s)["r"]
        for y in A.YEARS_FCST:
            assert abs(r["check"][y]) < 1e-6, (s, y)


def test_cash_flow_ties_to_balance_sheet():
    r = run(2)["r"]; cash = A.OPENING_BS["Cash"]
    for y in A.YEARS_FCST:
        cash += r["eqfcf"][y] - r["div_cash"][y] - r["nci_div"][y] - r["bb"][y]
        assert abs(cash - r["cash"][y]) < 1e-6


def test_history_ties_to_reported_totals():
    assert sum(A.HIST_LINES[k][2025] for k in KEYS) == A.HIST["Total income"][2025]
    assert sum(A.HIST_LINES[k][2024] for k in KEYS) == A.HIST["Total income"][2024]
    assert sum(v[2025] for v in A.DIV_EBITDA_HIST.values()) == A.HIST["Adj EBITDA"][2025]


def test_2026_is_nine_months_actual_plus_q4():
    r = run(2)["r"]
    for k in KEYS:
        assert abs(r[k][2026] - (sum(A.Q[k][4:7]) + A.Q[k][3] * (1 + A.Q4_GROWTH[k]))) < 1e-9


def test_scenarios_are_ordered():
    fv = [run(s)["fair_value"] for s in (1, 2, 3)]
    assert fv[0] < fv[1] < fv[2]


def test_2026_inside_company_guidance():
    r = run(2)["r"]
    assert r["eqfcf"][2026] >= 2795                                   # >= £2.8bn
    dm = r["ebitda"][2026] / r["tot"][2026] - A.HIST["Adj EBITDA"][2025] / A.HIST["Total income"][2025]
    assert 0.008 <= dm <= 0.016                                       # +100-120bp cc guide
    assert 1.5 <= r["lev"][2027] <= 2.5                               # pro forma 2027 upper end of range


def test_model_close_to_consensus():
    r = run(2)["r"]
    for y in (2026, 2027, 2028):
        assert abs(r["ebitda"][y] / A.CONSENSUS["Adjusted EBITDA"][y] - 1) < 0.05
        assert abs(r["eps"][y] / A.CONSENSUS["Adjusted EPS (p)"][y] - 1) < 0.05


def test_sotp_and_reverse_dcf_sane():
    s = sotp()
    assert 15 < s["blended_pe"] < 30 and abs(sum(p["weight"] for p in s["parts"].values()) - 1) < 1e-9
    implied = A.RETENTION[1] + solve("retention_adj", -0.06, 0.03)
    assert 0.80 < implied < A.RETENTION[1]


def test_excel_forecasts_are_formulas():
    from openpyxl import load_workbook
    import lseg.build_excel as b
    wb = load_workbook(b.OUT)
    for name in ("Model", "Divisions"):
        vals = [c.value for row in wb[name].iter_rows(min_row=6, min_col=6, max_col=10) for c in row if c.value is not None]
        assert vals and all(isinstance(v, str) and v.startswith("=") for v in vals), name


def test_stub_and_history():
    from lseg.engine import stub, pe_history
    st = stub()
    assert 0.15 < st["stake_pct"] < 0.35 and st["stub_pe"] < st["group_pe"]
    ph = pe_history()
    assert len(ph["rows"]) == len(A.MONTHLY_CLOSE) and ph["lo"] <= ph["now"] <= ph["hi"]


def test_trackers_and_evidence():
    from lseg.trackers import hiring, weekly
    import sys as _s; _s.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from common.jobs import classify
    assert classify("Senior AI Engineer") == "AI & data science" and classify("Account Executive") == "Sales & client"
    w = weekly()
    if w:  # data present once the weekly refresh has run
        assert all(0.05 < x["stake_pct"] < 0.6 for x in w)
    assert all(len(e) == 6 and e[-1].startswith("https://") for e in A.EVIDENCE)
