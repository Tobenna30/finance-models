# C++17 refinery pricer

A small library reproduces the unchanged Python refinery engine. The CLI is an auditable interface, not a production service. No original refinery assumptions, engine, workbook or risk memo are rebuilt.

## Results

The 28 October 2026 run checked all **48 collar rows**: two models, two products, twelve months. Maximum absolute difference across solved call strikes and both premiums was **2.1316282072803006e-14**, below 1e-8. Currency is USD per barrel; Black-76 volatility is dimensionless and normal volatility is USD/bbl per square-root year.

At **20,000 paths**, seed **20261027**, seven measured repetitions, median Python stress-kernel time was **0.011707666009897366s** and C++ was **0.000603709s**: **19.39289626276462x**. C++ CLI wall time for all seven repetitions and parsing was **0.08019550000608433s**. The original unmodified Python function took **0.2432691250141943s** once; that is a different workload, not the denominator of the kernel speed-up. Maximum Monte Carlo summary difference against the original was **1.454286960766906e-15**.

Machine: Apple arm64, Apple clang 21.0.0, Python 3.12.14, `-O3`. Timings vary by hardware/load/compiler. No speed threshold in CI. Exact inputs, summary outputs, source hashes and methodology: [benchmark.json](benchmark.json); all collar comparisons: [parity.csv](parity.csv).

Validation: **57 pytest cases**, plus **one CTest case containing eight native assertions**. These are counted separately. Greeks are checked against central finite differences for both put/call and both pricing models. Source-of-truth cover 80%, crack-fall loss 10%, Bachelier outage cost 2.3013698630136973%, Black-76 outage cost 1.5473073710677457% are unchanged.

## Build and run

```sh
cmake -S projects/14-derivatives-hedging/cpp-pricer -B /tmp/cpp-pricer -DCMAKE_BUILD_TYPE=Release
cmake --build /tmp/cpp-pricer --parallel 2
ctest --test-dir /tmp/cpp-pricer --output-on-failure
REFINERY_PRICER=/tmp/cpp-pricer/refinery_pricer python -m pytest tests/test_cpp_pricer.py tests/test_refinery_hedge.py
REFINERY_PRICER=/tmp/cpp-pricer/refinery_pricer python projects/14-derivatives-hedging/cpp-pricer/benchmark.py
```

A compiler-only fallback is `c++ -O3 -std=c++17 pricer.cpp main.cpp -o /tmp/refinery_pricer` from this folder. CMake is the CI path.

Example CLI input: `price B 40 38 0.4 1 0.04 1`. `N` selects Bachelier, `B` Black-76; the last field is one for call or zero for put. Output columns: price, delta, gamma, vega, remaining-time derivative, rho. `strike N 40 38 12 1 0.04 1` solves the sold-call strike against the put premium using the Python bracket and 200 bisections.

## Interview walkthrough

1. Discount a forward option by `exp(-rT)`. Bachelier integrates a normal forward, which can be negative. Black-76 integrates a positive lognormal forward; its forward and strike must be positive.
2. `quote` calculates the normal CDF/PDF once per required argument. Put-call parity is checked. Delta and gamma differentiate in the forward, not spot. Vega is per full volatility unit; divide Black-76 vega by 100 for one volatility point. Normal vega has different units.
3. `dprice_dt` differentiates in remaining maturity; calendar theta is its negative. Rho holds the forward fixed, so it is `-T*price`. Spot-rate coupling would need a different convention.
4. `zero_cost_call` bisects a monotonic call premium. Reject a bracket that cannot finance the put. Each comparison row checks the actual Python monthly expiry, normal/Black volatility and funding rate.
5. The existing Monte Carlo uses the first month's strikes against stylised annual average cracks. Preserve that approximation rather than silently improving it. Generate exactly the original correlated Python `Random.gauss` shocks once and pass the identical pairs to both kernels. The native loop accumulates product margins, applies the collar payoff, sorts returns and takes the same 5% order statistic.

## Limits

Kernel timings exclude RNG, strike solving, process start and text parsing for both versions. CLI timing includes startup/parsing and seven stress runs. This is not a production latency claim. Common random numbers come from Python; native RNG is deliberately not substituted because different normal transforms would invalidate pathwise parity. No implied-vol solver, calibration, American exercise, market data service or exchange conventions. At zero expiry/volatility, the API returns discounted intrinsic and a half-delta at the strike; gamma/vega use zero by convention, not a claim that kink derivatives exist. C++ uses standard-library `erf`; last-bit differences across platforms are expected.

This is a code extension of the existing financial model. The live-formula refinery workbook remains the financial output and is byte-for-byte unchanged; parity and timing outputs are CSV/JSON rather than a second financial model.
