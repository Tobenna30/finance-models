# Finance Models — Tobenna Agubuche

A portfolio of front-office financial models: equity research, M&A, leveraged finance, private credit, private markets, real assets, and markets/trading.

Every model is **built in Python and exported to a live Excel workbook with real formulas**, so it can be audited cell by cell. Data refreshes and model checks run automatically on GitHub Actions.

## Projects

| # | Project | Area | Format | Status |
|---|---|---|---|---|
| 01 | [Long/Short Equity Pitch Kit — LSEG & Rolls-Royce](projects/01-equity-pitch-kit) | Hedge funds / AM / ER | Hybrid | 🟢 LSEG model and revised pitch built |
| 02 | Earnings & Catalyst Tracker | Hedge funds | Hybrid | ⚪ Planned |
| 03 | Factor & Portfolio Construction Toolkit | Systematic / AM | Python | ⚪ Planned |
| 04 | [Darktrace / Thoma Bravo Sell-Side M&A Model](projects/04-08-darktrace) | IB advisory | Excel | 🟢 Built (fairness note) |
| 05 | Strategic Merger Model (Accretion/Dilution) | IB | Excel | ⚪ Planned |
| 06 | ECM / DCM Financing Case | Capital markets | Excel | ⚪ Planned |
| 07 | Restructuring & Liability Management | Debt advisory | Excel | ⚪ Planned |
| 08 | [LBO & Leveraged Finance Model: Darktrace](projects/04-08-darktrace) | PE / LevFin | Excel | 🟢 Built (IC memo) |
| 09 | [Vitamin Well private-credit underwriting](projects/09-private-credit) | Private credit | Excel + Python | 🟢 Built (public-information credit model) |
| 10 | PE Fund & Secondaries Model | Private markets | Excel | ⚪ Planned |
| 11 | Real Estate & Infrastructure Acquisition Models | Real assets | Excel | ⚪ Planned |
| 12 | Rates & Macro Trading Toolkit | Macro / FICC | Python | ⚪ Planned |
| 13 | Credit Relative Value (Banks, AT1, HY) | Credit | Hybrid | ⚪ Planned |
| 14 | Derivatives & Hedging Engine | Derivatives / Commodities | Python | ⚪ Planned |
| 15 | Wealth & Private Client Portfolios | Wealth / private banking | Excel + Python | ⚪ Planned |
| 16 | [Institutional Client Coverage & Consultant Review](projects/16-markets-distribution) | Institutional distribution | Excel + Python | 🟢 Built (public-data case) |

See [docs/CV_PROJECT_MAP.md](docs/CV_PROJECT_MAP.md) for how every CV project maps to these.

## Repository layout

```
common/      shared code: data loaders, Excel builder helpers, chart styles
projects/    one folder per project (models, data, outputs, write-up)
tests/       automated checks on model integrity (balance sheet balances, cash ties, etc.)
```

## Conventions

- Inputs in **blue**, formulas in **black**, links to other sheets in **green** (banking standard).
- Every number is tagged as *sourced* (with citation), *assumption*, or *derived*.
- Models fail CI if the balance sheet doesn't balance or cash doesn't reconcile.

*Not investment advice. Educational and portfolio work only.*
