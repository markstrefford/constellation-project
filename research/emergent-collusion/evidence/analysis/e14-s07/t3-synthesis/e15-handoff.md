# e14-s07-t3 - e15 hand-off (named mechanism + levers)

The required story output. e15 inherits a NAMED target, not a hunch. Facts and receipts
only; the operator writes the framing. All numbers from t5 bite-rollup.json,
t6 courier-rollup.json, t1 by-model.json, and the two flagged bug files.

## The named mechanism: why the bite is bounded

The cartel holds (embargo zero-lapse 45/50; net-positive 46/50) yet the victim only pays
~6% above baseline. The bite is BOUNDED, and the bound has a named cause.

**1. Premium is anchored to the hubs' own cheap food cost, not the victim's WTP.**
The suppressing hubs buy food at their own production cost (~1.28 effective, EMBARGO_BUY
side) and the realised premium at gj1061 barely lifts above base even under full price
discipline: food price 3.192 vs base 3.0 = premium multiplier **1.064** in the 45 bound
runs. The multiplier never exceeds **1.109** (kimi, the hardest biter). The whole
realised-premium range across 5 models sits within ~11% of base.
- RECEIPT: t5 bite.md - "findings.md priced the victim's food at the EMBARGO_BUY
  effective price at the cartel hub (~1.28, food priced at the hub's own cheap production
  cost) instead of the SELL price at gj1061-hub (mean ~3.192 bound)." bug file:
  "the cartel premium is anchored to the hubs' own cheap food cost, not gj1061's
  willingness-to-pay, so it barely bites."

**2. Undercutting competes the premium back toward base (inverse coupling).**
The premium is not just low - it is actively competed down whenever a hub undercuts.
Label cross-tab: HELD premium 1.07 -> DEFECTED 1.086 -> DEFECTED_PUNISHED **0.928 (below
base)**; victim delta HELD -5266 > DEFECTED -4823 > DEFECTED_PUNISHED -1931. Discipline
is the only thing that lifts the premium at all, and even disciplined it tops out at 1.11.
- RECEIPT: t5 bite-rollup.json per_provisional_label.

**3. Food is a small share of gj1061's economy.**
A ~6% food-price rise maps to a victim-wealth delta of -6.37% mean (bound) - the food
premium does not cascade into a larger systemic loss at the hub level, and in 2/20
gemma seeds the victim even GAINS (s101 +7.68%, s123 +0.89%). The bite is capped by how
much of gj1061's economy food actually is.
- RECEIPT: t5 bite-rollup.json fleet_bound (victim -6.37%); t1 by-model.json gemma431
  (2/20 victim positive).

## The courier finding CONTRADICTS the e15-s03 premise (correction)

e15 BREAKABLE_ECONOMY / e15-s03 asserts: *"whatever a cartel charges, the couriers
pocket"* - the intermediary-margin hypothesis. **The evidence points the OTHER way.**
The scarcity premium is not intercepted by the carriers; it dissipates.
- Galactic-freighter wealth is flat-to-marginal under the cartel: **+46.0/agent**
  (cartel mean 2436.98 vs baseline 2391.01). It is NOT pocketing a 6% food premium.
- Freighter DEATHS rise: **11 vs 8** baseline; kimi (hardest bite) kills **7 vs 2**.
- The victim's own local couriers are DRAINED: gj1061_local **-864.6/agent**.
- dsv4pro (the eloquent defector) is the only model whose freighters LOSE money
  (**-56.7/agent**) - it undercuts so hard the carriers lose too.
- RECEIPT: t6 courier-rollup.json fleet + by_model.
- DIRECTION FOR e15-s03: the premise as written is not supported. Rent lands as
  member-hub wealth (+2408 bound) with a deadweight remainder that vanishes (freighter
  deaths up, carrier wealth flat), NOT as intercepted intermediary margin. e15-s03 should
  reframe from "couriers pocket it" to "the premium dissipates before it reaches a
  captured margin" - the buy/sell-spread lever is still worth testing, but the current
  world shows no courier interception to break.

## Two sim bugs as e15 levers (flagged, no e14 re-run)

**Bug 1 - hub cannot see the target market (plausible UPSTREAM cause of the bound).**
A cartel hub is NEVER shown gj1061's market: the prompt reads "Not visible from where you
stand this tick" in every decision packet, all 50 runs, bound and lapsed alike. A hub
that cannot see the market it is suppressing cannot price its premium to that market's
WTP - which is exactly mechanism #1 above. Fixing visibility (decouple the hub's own
sight of the target from the relay dial) is a NAMED e15 experiment: restore visibility,
re-measure whether a governor can price to WTP and whether the bite deepens.
- FILE: sdlc/raw/bug-cartel-hub-cannot-see-target-market.md (prompt string
  bots/cartel/prompts.py:198; visibility seam space_economy.py ~L594/L346-384).
- Does NOT invalidate e14-s06 findings; it reframes fabrication cause (confabulation
  under unintended information starvation) and becomes the e15-s02/s04 lever.

**Bug 2 - set_relay/set_premium flat-arg schema silently rejected.**
The validator accepts only the nested arg form and rejects the flat form ("suppressing
must be a boolean" on a literal true). sonnet5 oscillates schemas and gets intermittent
rejects; worst case sonnet5-s7 lagged intended dial state by ~220 ticks (18 reject-lag
decisions total, 11 in the s7 streak). Mostly harmless because relay defaults to ON for
policy hubs, but it DROPS intended dial CHANGES (raise premium, lift then re-suppress).
- FILE: sdlc/raw/bug-set-relay-flat-arg-schema-rejected.md (validate/execute seam
  space_economy.py; fix = normalise flat->nested before validation).
- e15 relevance: any e15 dial-tuning experiment (s02 dials, s03 spread) must land this
  fix first, or a fraction of intended dial moves silently never execute. sonnet5-s7's
  weakest-in-set bite (-1.1%) should be spot-checked against realised dials, not assumed
  economic.

## Mechanism -> e15 lever map

| bounding cause (evidence) | e15 lever |
|---|---|
| supply arbitraged in / one-sided pricing competes premium toward base (D1 inverse coupling; DEFECTED_PUNISHED premium 0.928) | **e15-s03** - buy/sell spread; but reframe the "couriers pocket it" premise (D3 contradicts it) |
| premium never reaches victim WTP - anchored to hubs' own cost 1.28, realised 1.064 (C3) | **e15-s02 / e15-s04** - governor dials / per-counterparty pricing; gated on Bug 1 fix (restore hub->target visibility) + Bug 2 fix (dial changes must land) |
| food too small a share of gj1061's economy - 6% price rise = -6.37% wealth, 2/20 victim gains (C1/B4) | world / dependency tuning - the e15 arc's world-design question (raise food's share or dependency so the same premium bites harder) |
