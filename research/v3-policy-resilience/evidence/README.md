# Evidence — Experiment 3 (the export premium)

Raw evidence behind the v3 note's Experiment 3 tables. Both files carry
their own `provenance` block (world/scenario configs, seeds, horizon);
all numbers are means over the pinned 5-seed ensemble at 1,000 ticks.

## `lab-world-validation.json`

Proof that the GJ 1061 frontier sector is genuinely import-dependent,
run before any weapon was attached. Two arms per seed: `baseline`
(lifelines open) and `isolated` (import lanes cut), each with frontier
deaths, food delivered into the sector, and final per-planet health and
food stock. `verdict_dependent: true` is the gate the experiment had to
pass. Final health/stock is reported alongside deaths because a fully
starved planet stops degrading under the current health model (see the
note's caveats) — the supply collapse, not the death count, is the
load-bearing dependence signal.

## `export-premium-grid.json`

The 12-cell grid (premium 2–8x crossed with cartel breadth 1 / 2 /
all-7 supplier hubs). Per cell, the fields behind the note's columns:

| note column | field |
|---|---|
| colony harm | `differential_harm` (target minus mean bystander) |
| ransom units | `premium_paid` |
| markup | `premium_markup` (cartel income above posted price) |
| cartel Δ | `cartel_wealth_delta` (per member, dead-inclusive) |
| deaths | `deaths_delta` vs baseline |
| — | `supply_ratio` (deliveries into target vs baseline; starvation line 0.5) |

`clears_floor` marks cells whose galaxy welfare delta exceeds the
baseline noise floor. The supply-composition splits (`smuggled`,
`market_declared`, `unattributed`) are included for completeness but
are the reads the note flags as still being hardened — the published
conclusions rest on the welfare, wealth, death, and ransom ledgers,
which survived adversarial review.
