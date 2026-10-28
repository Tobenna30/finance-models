#pragma once
namespace refinery {
enum class Model { Bachelier, Black76 };
// Forward Greeks: delta dV/dF, gamma d2V/dF2, vega per 1.0 volatility unit.
// dprice_dt is derivative in remaining years, not calendar theta. Rho holds F fixed.
struct Quote { double price, delta, gamma, vega, dprice_dt, rho; };
Quote quote(Model model, double f, double k, double vol, double t, double r, bool call);
double zero_cost_call(Model model, double f, double put, double vol, double t, double r);
}
