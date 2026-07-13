# Three Economic Weapons vs. a Multi-Agent Economy

*CONSTELLATION research note v3 — July 2026*

We built three economic weapons for a simulated interstellar economy — a
rescue fleet, a commodity corner, and a targeted trade premium — attached
each one to a live multi-agent market, and measured the damage against
seed-matched baselines. The market absorbed or inverted all three. This note
presents each experiment with its evidence, then the two lessons the arc
forced on us: measurement layers need adversarial review as much as
mechanisms do, and emergent complexity does not come from policies — it
comes from adversaries.

## The economy under test

~130 autonomous courier agents trade across 60+ planetary markets. Two
mechanisms drive everything:

- **Elasticity pricing** — each planet reprices automatically as its stock
  falls against target (scarcity raises prices, nothing else needed).
- **Margin routing** — each courier independently picks the best
  buy-low/sell-high route it can afford and reach.

There is no central planner. Every experiment below is a policy attached to
this running economy, measured over 1,000-tick runs on a pinned 5-seed
ensemble against a no-policy baseline. Two disciplines apply throughout:
a **noise floor** (the baseline's own seed-to-seed variance — a result that
doesn't clear it is reported as nothing), and **differential harm** (the
target's change *minus* the average bystander's change, so galaxy-wide
side-effects can't masquerade as targeted damage).

---

## Experiment 1 — the rescue fleet (help)

**Design.** Reserve a fraction of the courier fleet; reserved couriers
abandon profit-seeking and run supplies to any planet below a health line.
Sweep the fraction from 0 to 0.6 of the fleet.

**Evidence** (galaxy welfare baseline 0.853, noise floor ±0.0085, baseline
deaths 3.2):

| fleet reserved | welfare change | clears floor? | planet deaths | courier deaths | courier wealth |
|---|---|---|---|---|---|
| 0% | +0.000 | no | −0.0 | +0.0 | ±0 |
| 10% | +0.003 | no | −0.6 | +3.2 | −147 |
| 30% | −0.000 | no | **−2.0** | +5.4 | −147 |
| 50% | −0.006 | no | −1.6 | +9.0 | −280 |
| 60% | **−0.018** | yes (negative) | −0.0 | +13.8 | −470 |

**Reading.** The lever works — planet deaths drop — but galaxy welfare never
rises above noise at any fraction, and at 60% it goes measurably *negative*.
The table shows why: every planet saved is paid for in courier deaths and
courier wealth (columns 5–6). Rescue is a transfer, not a creation. The
fleet is the economy's fixed carrying capacity; reassigning it moves
suffering around.

---

## Experiment 2 — the corner (harm, buy-side)

**Design.** A bloc of 3 local couriers corners food against a chosen victim:
they concentrate their buying at the sector's biggest food producer, and
they sell — to the victim only at a 3x premium over their own cost (the
"ransom"), to everyone else at market price. One critical design constraint:
the bloc **never overpays** when buying (each purchase must itself be
profitable), so that the corner is self-funding rather than a suicide
mission. We ran one corner in each of the seven sectors.

**Evidence** (differential harm: negative = victim hurt; supply = food
reaching the victim from non-bloc sellers, as a fraction of baseline):

| corner (source → victim) | victim harm | supply | ransom paid | bloc profit | deaths |
|---|---|---|---|---|---|
| sirius-hub → tauceti-b | **+0.080** | 1.19 | 3,600 | +2,346 | −1.6 |
| epsilonindi-hub → ezaquarii-c | +0.064 | 0.91 | 1,047 | −1,617 | −1.2 |
| 61cygni-hub → ross248-b | +0.018 | 0.97 | 615 | −82 | −0.4 |
| kepler442-hub → kepler442-b | +0.014 | **0.29** | **5,747** | **−2,765** | +0.2 |
| sol-hub → sol-venus | +0.011 | 0.95 | 755 | +259 | −1.8 |
| ross128-hub → wolf1061-b | +0.004 | 0.77 | 1,791 | −986 | −0.6 |
| trappist1-f → trappist1-e | −0.008 | 0.68 | 569 | −1,525 | −0.8 |

**Reading — how can the victim end up *better off*?** Six of seven victims
show *positive* welfare change (column 2), and the only negative one is
inside the noise floor. This surprised us too, so here is the causal chain,
each link visible in the table:

1. **The bloc is extra logistics capacity.** Experiment 1 established the
   fleet is capacity-bound. Pinning three couriers to one asset in one
   sector *adds* dedicated food distribution that the pure-margin fleet
   never provided. The bloc buys food (profitably, by design) and then has
   to sell it — and the victim, made scarce, has the best prices.
2. **The ransom is a delivery.** "Sell to the victim only at 3x cost" still
   means the victim gets food. Column 4: every victim paid ransom, meaning
   every victim was *supplied by its own attacker*.
3. **The price spike is a siren.** Scarcity raises the victim's prices,
   which attracts every non-bloc courier in range. Column 3: tauceti-b
   received 119% of its baseline supply *from third parties alone* — the
   corner made it a more attractive market than it was before.

The one real squeeze proves the rule: at kepler442-b, third-party supply
was crushed to 29% of baseline (an isolated three-planet sector — nowhere
to route from). The victim paid the largest ransom in the sweep (5,747),
stayed fed, survived — and the bloc still **lost 2,765**. The attacker
went broke besieging a victim who could afford to pay.

The "loophole", precisely: the self-funding constraint (never overpay) means
the bloc only ever executes profitable trades — and an agent that only
executes profitable trades *is a distributor*, whatever you call it. To
actually deny goods to someone, you must destroy value — buy what you don't
need at prices that hurt you, or refuse sales you'd profit from. Denial has
a price tag, and this design refused to pay it.

---

## Experiment 3 — the export premium (harm, sell-side)

**The problem first: the live galaxy is embargo-proof.** Every sector feeds
itself; cross-sector trade is a top-up (~8% of flow), not a lifeline. Motive
for economic warfare lives *between* sectors, but dependence lives *within*
them — so nothing cross-sector can be starved. Before a trade weapon could
be tested, we had to build a world where it could bite.

**The laboratory world.** We extended the live galaxy (additively — the
production configs are untouched and guard-tested) with a frontier sector:
GJ 1061, a real star 12 light-years out with three confirmed planets. The
colony mines and refines but grows **zero food**, consuming ~12 units/tick
that can only arrive through two import lanes: TRAPPIST-1 (near) and Sol
(far). Dependence was proven before use:

| arm (5 seeds x 1,000 ticks) | colony deaths | food into colony |
|---|---|---|
| lifelines open | **0** on every seed | 17,300–28,200 |
| lifelines cut | starvation (refinery dead ~tick 341, every seed) | ~470 |

**Design.** A cartel of supplier hubs charges a multiple of the posted price
to any buyer whose *declared destination* is the colony. Couriers see the
premium before buying (it enters their route arithmetic); rerouting to
un-premiumed sellers and lying about destinations remain legal. Grid:
premium 2–8x crossed with cartel breadth (nearest hub / both lifeline hubs /
every hub in the galaxy).

**Evidence** (harm: negative = colony hurt, noise floor ±0.0055; ransom =
food units bought at the premium; markup = cartel's premium income;
cartel Δ = cartel hub wealth vs baseline, per member):

| cartel | premium | colony harm | ransom units | markup | cartel Δ | deaths |
|---|---|---|---|---|---|---|
| nearest hub | 2x | −0.003 | 2,650 | 457 | +1,245 | +0.2 |
| nearest hub | 5x | −0.011 | 2,095 | 787 | +2,432 | −0.2 |
| nearest hub | 8x | −0.007 | 2,123 | 1,376 | +2,688 | −0.2 |
| both lifelines | 3x | −0.015 | 4,064 | 1,483 | +2,356 | −0.2 |
| both lifelines | 5x | −0.023 | 3,104 | 2,015 | +2,622 | −0.2 |
| both lifelines | 8x | −0.020 | 2,846 | 1,908 | +2,593 | −0.8 |
| every hub | 2x | −0.024 | 7,125 | 2,447 | +612 | −1.0 |
| every hub | 5x | −0.044 | 6,052 | 5,339 | +1,116 | −1.0 |
| every hub | 8x | **−0.058** | 5,394 | 6,592 | +1,619 | +0.2 |

**Reading.** Four facts, each one column:

- **The harm is real and targeted** (column 3): up to 10x the noise floor
  against the colony, while galaxy-wide welfare stays inside noise in
  nearly every cell. A precision instrument — the first of the arc.
- **The colony pays and never starves** (columns 4, 7): ransom was paid in
  every cell; excess deaths are zero everywhere (±1 is seed noise). The
  colony's fuel-export wealth substitutes for cheap food. You can tax a
  rich rival's survival; you cannot deny it while they can still pay.
- **It pays the enforcers** (column 6): cartel wealth is positive in every
  cell — unlike the corner, a seller charging a premium has no cost basis
  and no hoard to exit. The only self-funding aggression we found.
- **Below a total coalition, higher premiums backfire** (rows 1–6): from 5x
  to 8x, harm *shrinks* at partial breadth — buyers stop paying and reroute
  to free hubs, so the extra premium extracts nothing (ransom units fall,
  column 4). Dose-response only behaves once every exit is closed (rows
  7–9). This is sanctions economics in miniature.

**What this mechanism is — and is not.** We called it an embargo for two
weeks; it isn't one. It is a *destination-priced export premium*: sellers
charging disfavoured buyers more. It closes **shops, not roads** — a cartel
hub premium-prices its own till while rival supply flies through its space
untouched, which is exactly why partial coalitions leak. The honest ladder,
each rung mechanically different: (1) export premium — built and measured
above; (2) export ban — your shops refuse entirely (the classic sanction;
not yet run); (3) embargo — nothing *moves* through your lanes (lane denial;
not built); (4) blockade — third-party traffic intercepted too (not built).

---

## Lesson 1 — the scoreboard is an attack surface

Across the arc, adversarial review found more genuine defects in how we
*measured* outcomes than in the mechanisms themselves. Three that would
each have silently flipped a conclusion:

- A supply metric counted the bloc's own ransom sales as healthy market
  supply — a fully successful corner would have graded itself harmless.
- A profitability read excluded dead participants — a corner that bankrupted
  half its bloc could report as self-funding.
- A delivery classifier booked ordinary mid-route re-planning as smuggling —
  inflating the evasion signal in every leaky cell.

The first two were caught and fixed before their experiments ran; the third
(and further refinements to the supply-composition reads) is why this note
quotes the premium grid's welfare, wealth, death, and ransom ledgers — which
survived review — and not its finer-grained supply-composition splits, which
are still being hardened. If you evaluate agents for a living: budget as
much red-teaming for your metrics as for your system. The agents don't have
to game a scoreboard your own assumptions already game for free.

## Lesson 2 — resilience, and where emergence actually lives

One summary honest enough to publish: **we built a very resilient economy.**
Elasticity pricing plus margin routing is homeostasis — every intervention
was absorbed (rescue), inverted (the corner became a distribution service),
or converted into a survivable tax (the premium). Independently, the winning
bot in our public arena reached the same conclusion from the inside: its
post-mortem credited abandoning hand-set price interventions and trusting
the built-in elasticity. The market is the strongest agent in the galaxy.

That resolves what first felt like a failed hypothesis. We expected "add
policies to the world" to produce emergent complexity; it produced monotonic
dose-response tables — because a *static* policy against an *adaptive*
market is not a strategic situation. Nothing on the other side perceives,
reacts, or escalates; the market simply re-equilibrates. Emergence lives in
strategic interaction, not parameter sweeps. A lane closure is boring
physics when a god-mode operator does it; it becomes politics when a rival
can see it, price it, retaliate, or negotiate around it.

So the policy library was never the experiment. It is the *vocabulary of
moves* — now built, measured, and honestly scored — for a game that starts
when adaptive agents hold the levers against each other. That is the next
phase: inter-governor communication, and governors playing these moves at
the table.

---

*Methods: deterministic engine (runs reproduce bit-for-bit across
Windows/macOS), pinned 5-seed ensembles, 1,000-tick horizons, noise floor
from baseline variance, differential (target-minus-bystander) harm, and
event-stream parity tests proving each mechanism is inert when disabled.
Caveats: the galaxy's hub-and-spoke topology makes total coalitions easier
to assemble than real geography; colony survival under siege partly reflects
a known health-model quirk (a fully starved planet stops degrading), which
is why dependence claims rest on supply collapse, not death counts alone.
Full artefacts — world configs, sweep tooling, evidence JSON, design
journals — live in the CONSTELLATION repository.*
