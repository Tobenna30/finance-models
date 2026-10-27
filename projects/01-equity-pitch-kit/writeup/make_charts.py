"""Charts for the LSEG pitch. Run from projects/01-equity-pitch-kit: python3 writeup/make_charts.py"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from lseg.engine import pe_history, stub, solve
from lseg import assumptions as A

OUT = Path(__file__).resolve().parent / "charts"; OUT.mkdir(exist_ok=True)
NAVY, GREY, RED = "#1F3864", "#9AA5B1", "#C0392B"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "axes.spines.top": False, "axes.spines.right": False})

# 1. Trailing P/E history
ph = pe_history()
x = [r[0] for r in ph["rows"]]; y = [r[3] for r in ph["rows"]]
fig, ax = plt.subplots(figsize=(3.6, 2.2), dpi=200)
ax.plot(range(len(x)), y, color=NAVY, lw=1.4)
ax.axhline(ph["avg"], color=GREY, ls="--", lw=1); ax.text(len(x) * 0.80, ph["avg"] + 0.6, f"5y avg {ph['avg']:.1f}x", color="#555", fontsize=7)
ax.scatter([len(x) - 1], [y[-1]], color=RED, s=12, zorder=3); ax.annotate(f"now {y[-1]:.1f}x", (len(x) - 1, y[-1]), xytext=(len(x) - 14, y[-1] + 4.5), color=RED, fontsize=7, arrowprops=dict(arrowstyle="-", color=RED, lw=0.6))
ax.set_xticks([i for i, m in enumerate(x) if m.endswith("-01")]); ax.set_xticklabels([m[:4] for m in x if m.endswith("-01")])
ax.set_title("LSEG trailing P/E (adjusted EPS)", fontsize=8, loc="left", color=NAVY, fontweight="bold")
fig.tight_layout(); fig.savefig(OUT / "pe_history.png"); plt.close(fig)

# 2. Forward P/E: peers vs LSEG and LSEG ex-Tradeweb
st = stub()
data = sorted([(row[0].replace("Intercontinental Exchange", "ICE").replace("Deutsche Börse", "Deutsche B."), row[6]) for row in A.COMPS], key=lambda t: t[1])
data += [("LSEG", st["group_pe"]), ("LSEG ex-Tradeweb", st["stub_pe"])]
data = sorted(data, key=lambda t: t[1])
fig, ax = plt.subplots(figsize=(3.6, 2.2), dpi=200)
cols = [RED if "LSEG" in n else GREY for n, _ in data]
ax.barh([n for n, _ in data], [v for _, v in data], color=cols, height=0.65)
for i, (_, v) in enumerate(data): ax.text(v + 0.2, i, f"{v:.1f}x", va="center", fontsize=6)
ax.tick_params(axis="y", labelsize=6); ax.set_xlim(0, 32)
ax.set_title("Forward P/E, 20–23 Oct 2026", fontsize=8, loc="left", color=NAVY, fontweight="bold")
fig.tight_layout(); fig.savefig(OUT / "fwd_pe.png"); plt.close(fig)

# 3. Retention reported vs implied by the share price
implied = A.RETENTION[1] + solve("retention_adj", -0.06, 0.03)
labs = list(A.RETENTION_HISTORY) + ["Implied by\nshare price"]
vals = [v * 100 for v in A.RETENTION_HISTORY.values()] + [implied * 100]
fig, ax = plt.subplots(figsize=(3.6, 2.2), dpi=200)
ax.bar(labs, vals, color=[NAVY] * 3 + [RED], width=0.6)
for i, v in enumerate(vals): ax.text(i, v + 0.05, f"{v:.1f}%", ha="center", fontsize=7)
ax.set_ylim(89, 94.2); ax.set_title("Revenue retention: reported vs priced in", fontsize=8, loc="left", color=NAVY, fontweight="bold")
fig.tight_layout(); fig.savefig(OUT / "retention.png"); plt.close(fig)
print("charts written", sorted(p.name for p in OUT.iterdir()))

# 4. Tradeweb stake as % of LSEG market cap (weekly)
from lseg.trackers import weekly
w = weekly()
fig, ax = plt.subplots(figsize=(3.6, 2.2), dpi=200)
ax.plot(range(len(w)), [x["stake_pct"] * 100 for x in w], color=NAVY, lw=1.4)
ticks = [i for i, x in enumerate(w) if x["date"][5:7] == "01" and int(x["date"][8:10]) <= 7]
ax.set_xticks(ticks); ax.set_xticklabels([w[i]["date"][:4] for i in ticks])
ax.set_ylabel("%"); ax.set_title("Tradeweb stake as % of LSEG market cap", fontsize=8, loc="left", color=NAVY, fontweight="bold")
fig.tight_layout(); fig.savefig(OUT / "stake_share.png"); plt.close(fig)
print("stake chart written")
