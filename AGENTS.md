# AGENTS.md

Instructions for any coding agent (Codex, Claude or other) working in this repo. Read this before every task.

## What this repo is

A portfolio of front-office finance models (IB, private markets, asset management, hedge funds, wealth, sales) built by Tobenna Agubuche (MSc Finance, QMUL). The models are sent to portfolio managers and interviewers, so they must hold up to a professional's review.

Each project has **one anchor company or market**. Analyst tasks are added to it as modules. Every project cited on a CV must point to a module here. When a job description needs a task no module covers, build that module on the closest project before the CV goes out. Do not invent new projects outside the 16 in `docs/CV_PROJECT_MAP.md` (added in PR #7).

## CV Autopilot handoffs

Before running CV Autopilot handoffs, read `~/Documents/CV Autopilot/handoffs/CODEX.md` for the build, PR and results-handoff workflow. Follow its restrictions on the shared CV Autopilot folder.

## Workflow

- Branch from `main`, one branch and PR per project or module. Tobenna reviews and merges. Never push to `main`.
- CI: `.github/workflows/checks.yml` runs `pytest` on push and PR. All tests must pass.
- `.github/workflows/refresh-data.yml` runs every Monday (EDGAR, hiring tracker, prices) and opens a PR with refreshed `data/`.
- Never print, commit or log tokens or credentials.

## House standard for every model

Copy the structure of `projects/01-equity-pitch-kit/lseg/`:

1. `assumptions.py`: the single source of inputs. Tag every value **S** (sourced, with URL or document and page), **A** (assumption, with one line of reasoning) or **D** (derived).
2. `engine.py`: pure Python calculation of the full model. No Excel logic here.
3. `build_excel.py`: openpyxl workbook. Every forecast cell is a live formula pointing at the Inputs sheet, never a pasted number. Include a Cover, Inputs, the model sheets, scenarios/sensitivities and a Sources sheet.
4. Recalculate with LibreOffice headless (`soffice --headless --convert-to xlsx`) and commit the recalculated file to `models/`.
5. Tests in `tests/test_<project>.py`: the Excel values tie to the engine, the balance sheet balances, cash ties, history ties to reported figures, forecasts are formulas, scenarios are ordered bear < base < bull.
6. Write-ups in `writeup/` as markdown, built to PDF with `writeup/build_pdf.py` (markdown to python-docx to LibreOffice). Charts from `writeup/make_charts.py`.

Sources: prefer primary documents (annual reports, scheme documents, prospectuses, SEC EDGAR, company IR). Secondary data (stockanalysis.com, Yahoo) only as a cross-check, labelled as such. Shared data pullers live in `common/` (`edgar.py`, `jobs.py`, `prices.py`).

## Modelling rules

- Acquisitions and deal payments are cash outflows in the DCF. (An LSEG bug once left the Octus purchase out and overstated value by 5%.)
- Do not tune assumptions to rescue a conclusion. If a change moves the answer, show it as its own documented line with a source, so a reader can switch it off.
- State the call plainly (long, short, fair, accept, reject). Avoid "neutral".
- Show what the market implies (reverse DCF or implied multiple) next to your own view.

## Writing rules

- No AI tells: no em dashes, no filler ("delve", "robust", "leverage", "it is worth noting", "in today's landscape"), no stacked adjectives, no rhetorical questions.
- Plain analyst prose: short sentences, numbers first, one idea per paragraph.
- British spelling. Pence as `p`, pounds as `£m` / `£bn`.

## Project status

| # | Project | Anchor | Status |
|---|---|---|---|
| 01 | Equity research | LSEG | Built. Post-Octus pitch revised: long, 10,414p target; reverse DCF implies 93.45% retention. PR #8 merged. |
| 02 | Earnings & catalyst tracking | LSEG + coverage | Hiring and Tradeweb-stake trackers built |
| 04 + 08 | Sell-side M&A + LBO | Darktrace (Thoma Bravo take-private) | Built. Review adds liquidity shortfalls and conditional IC decision; final debt terms need verification. |
| 06 | ECM / DCM Financing Case | Meta AI infrastructure financing | Built: USD37.5bn priced package, USD12.475bn assumed net cash at close, USD24.907bn deferred; matched debt/equity alternatives and initial preferred mechanics. Class C dilution and final terms require review. |
| 09 | Private credit underwriting | Vitamin Well / Vital Bidco | Built: 2026 public-information capacity, cash/debt, policy headroom and recovery. Final terms and audited accounts unverified. |
| 14 | Derivatives, hedging & commodities | Illustrative South African refinery | Built: Bachelier collars, Black-76 check, outage stress and USD/ZAR overlay. 80% cover; 10% crack-fall loss; 2.3% outage cost. |
| 03, 05, 07, 10–13, 15–16 | See `docs/CV_PROJECT_MAP.md` | | Not started |

## Darktrace follow-up (projects 04 and 08)

Built in `projects/04-08-darktrace/`. Follow the review record before extending the model. Primary confirmation of final syndicated debt terms, consistent precedent EV bridges and intra-year liquidity/covenant analysis remain open. Do not describe the model as an April 2024 information set or the debt as safe because year-end cash stays positive.

## LSEG items parked (do not act without being asked)

- Feeding the edge items into valuation: evidence-based scenario weights 20/50/30, price/other 4.5%, and a stub-based valuation (stub earnings x peer P/E plus the Tradeweb stake) as a third method.
- Remaining LSEG modules: earnings quality, Octus deal value, buyback execution, bear case, FTSE Russell IPO, capital allocation, Dutch Bros short.
