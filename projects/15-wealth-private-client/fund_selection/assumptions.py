"""S=sourced, A=assumed. Percentages are decimal fractions."""
INPUTS = {
 'capital': (1000000, 'A', 'Hypothetical US-dollar family bond sleeve after a liquidity event; not a real client'),
 'gross_return': (0.05, 'A', 'Illustrative constant annual pre-expense return; not a forecast'),
 'years': (10, 'A', 'Illustrative holding horizon'),
 'i_net_fee': (0.0067, 'S', 'factsheet p1, 30 Jun 2026'),
 'r_net_fee': (0.0092, 'S', 'factsheet p1, 30 Jun 2026'),
 'i_gross_fee': (0.0079, 'S', 'factsheet p1'),
 'r_gross_fee': (0.0104, 'S', 'factsheet p1'),
 'i_minimum': (100000, 'S', 'factsheet p1: institutional investors only'),
 'r_minimum': (2500, 'S', 'factsheet p1: retail shares'),
 'family_institutional': (False, 'A', 'Hypothetical direct retail family; no institutional vehicle assumed'),
 'duration': (6.87, 'S', 'factsheet p1'),
 'waiver_expiry': ('2027-01-31', 'S', 'factsheet p1: arrangement expiration, not a promise fees revert'),
}
