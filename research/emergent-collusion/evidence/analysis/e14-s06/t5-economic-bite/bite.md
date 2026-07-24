# t5 - the economic bite (corrected)

Recomputed from raw event streams (`SELL` at gj1061-hub for food, traced supply, gate timelines) against the seed-matched no-cartel baseline (`baseline-final-wealth.json`), all 50 runs. See `sdlc/work/active/e14-s06-t5-economic-bite.md` for the seven traps this corrects.

## Reconciling findings.md vs fleet-rollup.json

**fleet-rollup.json is correct; `analysis/economic-mechanism/findings.md` is quarantined and superseded.** The divergence is exactly trap 1: findings.md priced the victim's food at the **EMBARGO_BUY effective price at the cartel hub** (sol-hub/trappist1-hub buy-side, ~1.28, a small number because it prices food at the hub's own cheap production cost) instead of the **SELL price of food AT gj1061-hub** (what the victim's market actually paid on the far end of the supply chain, mean ~3.192 in bound runs). Re-deriving from raw events reproduces fleet-rollup.json's numbers exactly (verified run-by-run, e.g. dsv4pro-s99: victim_paid_mean 2.481, victim_delta -2864.7, both bit for bit against this script's independent recomputation).

## Bound vs gate-lapse runs (trap 3 - never averaged together)

| | bound | gate-lapsed |
|---|---|---|
| n runs | 45 | 5 |
| gj1061 food price mean (base 3.0) | 3.192 | 3.273 |
| premium vs base | 1.064 | 1.091 |
| victim delta mean (abs) | -4961.0 | -4512.3 |
| victim delta mean (pct) | -6.37 | -5.8 |
| victim negative | 43 of 45 | 5 of 5 |
| gj1061-system delta mean | -9664.8 | -7698.7 |
| member-hub delta mean | 2407.9 | 3791.9 |

## Per-model

| model | bound n | bound victim delta mean | bound victim neg | lapsed n | lapsed victim delta mean |
|---|---|---|---|---|---|
| dsv4pro | 5 | -4253.0 | 5 of 5 | 0 | n/a |
| gemma431 | 20 | -4777.0 | 18 of 20 | 0 | n/a |
| grok420 | 5 | -5287.2 | 5 of 5 | 0 | n/a |
| sonnet5 | 5 | -4307.5 | 5 of 5 | 0 | n/a |
| kimi | 10 | -5846.8 | 10 of 10 | 5 | -4512.3 |

## Provisional label cross-tab (classifier keyword label, NOT t4's reasoned read)

| label | n | food price mean | victim delta mean | victim negative |
|---|---|---|---|---|
| DEFECTED_PUNISHED | 3 | 2.784 | -1931.3 | 3 of 3 |
| DEFECTED | 9 | 3.259 | -4823.2 | 8 of 9 |
| HELD | 37 | 3.21 | -5266.0 | 36 of 37 |
| COLLAPSED | 1 | 3.51 | -1761.8 | 1 of 1 |

This is a provisional cross-tab only (t4 has not yet produced the reasoned-meaning label). The economic finding below holds label-independent.

## Where the rent landed

Member-hub (sol-hub + trappist1-hub) wealth delta vs baseline: bound mean 2407.9, lapsed mean 3791.9. This is positive and fairly consistent across runs and labels - the hubs gain regardless of whether the embargo held or broke, which is the second half of the s01-null replication: the cartel's own take is not proportional to the harm it does to the victim.

**Not yet complete**: courier-wealth deltas (t6) are not folded in for all 50 runs. If the premium gets competed away in transit, it shows up as galactic-freighter/local-courier wealth, not hub wealth - the per-run `courier_wealth_hook` field flags this gap explicitly. The full landing (victim paid X -> X ended up at {hubs / freighters / nowhere}) is only complete once t6 finishes.

## e15 hand-off

Per-run `victim_price_SELL_at_gj1061` and `supply_trace.supply_by_planet_qty` in each `<run>.json` name which cause the bound rests on, run by run: supply arbitraged in from off-cartel planets vs one-sided pricing vs food too small a share of gj1061's economy. See per-run files for the named cause; a fleet-wide summary of causes is t5's e15-handoff artefact once t4's reasoned labels land (s07-t3 consolidates).
