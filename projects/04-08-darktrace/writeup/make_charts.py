"""Charts for the Darktrace write-ups. Run from projects/04-08-darktrace: python3 writeup/make_charts.py"""
import sys
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from darktrace import engine as E, assumptions as A  # noqa: E402

OUT = Path(__file__).resolve().parent / "charts"; OUT.mkdir(exist_ok=True)
NAVY, GREY, RED = "#1F3864", "#8C8C8C", "#C00000"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "axes.spines.top": False, "axes.spines.right": False})

# football field
ff = E.football()[::-1]
fig, ax = plt.subplots(figsize=(6.6, 3.0))
for i, (lab, lo, hi) in enumerate(ff):
    ax.barh(i, hi - lo, left=lo, color=NAVY, height=0.55)
    ax.text(lo - 8, i, f"{lo:,.0f}", va="center", ha="right", fontsize=7); ax.text(hi + 8, i, f"{hi:,.0f}", va="center", fontsize=7)
ax.axvline(A.DEAL["offer_p"], color=RED, lw=1.2); ax.text(A.DEAL["offer_p"] + 6, len(ff) - 0.35, "Offer 620p", color=RED, fontsize=7)
ax.axvline(A.DEAL["undisturbed_p"], color=GREY, lw=1, ls="--"); ax.text(A.DEAL["undisturbed_p"] - 6, len(ff) - 0.35, "Undisturbed 517p", color=GREY, fontsize=7, ha="right")
ax.set_yticks(range(len(ff))); ax.set_yticklabels([f[0] for f in ff]); ax.set_xlabel("pence per share"); ax.set_xlim(300, 1250)
fig.tight_layout(); fig.savefig(OUT / "football_field.png", dpi=200); plt.close(fig)

# deleveraging, base vs downside
fig, ax = plt.subplots(figsize=(3.3, 2.4))
for case, col in (("Base", NAVY), ("Downside", GREY)):
    r = E.lbo(case)["rows"]; ax.plot([f"FY{x['year'] % 100}" for x in r], [x["lev"] for x in r], marker="o", color=col, label=case)
ax.set_title("Total debt / EBITDA", fontsize=8); ax.legend(frameon=False); ax.set_ylim(0, 13)
fig.tight_layout(); fig.savefig(OUT / "leverage.png", dpi=200); plt.close(fig)

# IRR grid heatmap
g = E.lbo_grid()
fig, ax = plt.subplots(figsize=(3.3, 2.4))
ax.imshow(g, cmap="Blues", aspect="auto", vmin=0.10, vmax=0.34)
for i, row in enumerate(g):
    for j, v in enumerate(row): ax.text(j, i, f"{v:.0%}", ha="center", va="center", fontsize=7, color="white" if v > 0.24 else "black")
ax.set_xticks(range(len(A.GRID_DEBT))); ax.set_xticklabels([f"{d / 1000:.2f}bn" for d in A.GRID_DEBT], fontsize=6.5)
ax.set_yticks(range(len(A.GRID_EXIT))); ax.set_yticklabels([f"{x:.0f}x" for x in A.GRID_EXIT])
ax.set_xlabel("Debt at close ($)"); ax.set_ylabel("Exit EV / EBITDA"); ax.set_title("Base-case IRR", fontsize=8)
for s in ax.spines.values(): s.set_visible(False)
fig.tight_layout(); fig.savefig(OUT / "irr_grid.png", dpi=200); plt.close(fig)
print("charts in", OUT)
