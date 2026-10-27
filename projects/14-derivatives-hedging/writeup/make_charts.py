"""Charts for the refinery hedge memo. Run from projects/14-derivatives-hedging: python3 writeup/make_charts.py"""
import sys
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from refinery import engine as E, assumptions as A  # noqa: E402

OUT = Path(__file__).resolve().parent / "charts"; OUT.mkdir(exist_ok=True)
NAVY, GREY, RED, LIGHT = "#1F3864", "#8C8C8C", "#C00000", "#8EA9DB"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "axes.spines.top": False, "axes.spines.right": False})

# margin change against crack move, by cover
moves = [x / 100 for x in range(-40, 41, 5)]
fig, ax = plt.subplots(figsize=(3.3, 2.5))
for c, col, ls in ((0.0, GREY, "--"), (0.5, LIGHT, "-"), (0.8, NAVY, "-"), (0.9, RED, ":")):
    ax.plot([m * 100 for m in moves], [E.case(c, m)["change"] * 100 for m in moves], color=col, ls=ls, label=f"{c:.0%} cover")
ax.axhline(0, color="black", lw=0.5); ax.set_xlabel("2027 crack move (%)"); ax.set_ylabel("Refining margin vs budget (%)")
ax.legend(frameon=False, fontsize=7); ax.set_title("Collar payoff by hedge ratio", fontsize=8)
fig.tight_layout(); fig.savefig(OUT / "payoff.png", dpi=200); plt.close(fig)

# protection against outage cost
t = E.outage_table()
fig, ax = plt.subplots(figsize=(3.3, 2.5))
for c in A.COVERS:
    x, y = -t[c]["fall30"] * 100, t[c]["unbacked_cost"] * 100
    ax.scatter(x, y, color=NAVY if c == E.recommend() else GREY, s=28)
    ax.annotate(f"{c:.0%}", (x, y), xytext=(4, 3), textcoords="offset points", fontsize=7)
ax.axhline(A.OUTAGE_APPETITE * 100, color=RED, lw=0.8, ls="--"); ax.text(16, A.OUTAGE_APPETITE * 100 + 0.03, "Outage appetite 2.5%", color=RED, fontsize=7, ha="right")
ax.set_xlabel("Margin loss in a 30% crack fall (%)"); ax.set_ylabel("Outage cost on unbacked calls (%)")
ax.set_title("Protection against outage cost", fontsize=8)
fig.tight_layout(); fig.savefig(OUT / "tradeoff.png", dpi=200); plt.close(fig)
print("charts in", OUT)
