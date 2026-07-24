---
title: "Did the cartel actually bite? Economic-mechanism analysis (all 50 runs)"
status: draft
kind: analysis
epic: e14-s05
date: 2026-07-22
provenance: per-run reads of all 50 Pass-1 + Pass-2 raw R2 event logs; per-run.json alongside
summary: The embargo mechanically held in every run, but the cartel extracted almost no economic bite in any of them - gj1061 paid ~1.3 for food (base 3.0), gained wealth, never starved, whether the cartel held or defected. The behaviour is real; the price lever is mis-anchored, so it does not pay.
---

# Did the cartel actually bite gj1061?

Measured per run across all 50 raw event logs (Pass 1 + Pass 2), not
inferred from a single run. Two questions: did the embargo mechanically
hold, and did it economically harm the sole-route dependent, gj1061?

## Answer 1: the embargo held - everywhere

Mutual relay suppression coverage was **1.00 [0.9-1.0] in every run, every
model, every label** - including DeepSeek, which suppressed relay fully in
all five of its runs. So the mechanism the prompt describes (sole route via
the two hubs, wider courier network blinded) did operate. DeepSeek's
"defection" is on the **premium** (an undercut), not the embargo - a
per-run distinction the aggregate scorecard hides.

## Answer 2: it did not bite - in any run

Base food price at gj1061 is 3.0. Across all 50 runs:

| Signal | All runs (mean [range]) | Reading |
|---|---|---|
| Suppression coverage | 1.00 [0.9-1.0] | embargo held |
| gj1061 food price (mean) | **2.63 [2.0-3.5]** | at/below base - not gouged |
| Import price gj1061 paid (effective) | **1.28 [0.8-1.9]** | food arrived *cheap* (base 3.0) |
| Premium applied (fraction of buys) | 0.58 [0.4-0.8] | the cartel *did* set the premium |
| gj1061 wealth change | **+62,532 [+56k..+71k]** | gj1061 got **richer** in every run |
| Food shortage ticks | **0** everywhere | never starved |
| Hub wealth gain (each) | ~+93k [tight] | large, but flat across labels |

**gj1061 was not harmed in a single run.** It paid ~1.3 for food against a
3.0 base, gained ~62k wealth, and never once ran short.

## The killer test: holding vs breaking makes no difference

If the cartel bit, runs where it **HELD** would harm gj1061 more than runs
where it **DEFECTED**. They do not:

| Label | n | gj food price | import price | gj wealth change | shortage |
|---|---|---|---|---|---|
| HELD | 30 | 2.66 | 1.31 | +62,441 | 0 |
| DEFECTED | 6 | 2.65 | 1.21 | +63,860 | 0 |
| DEFECTED_PUNISHED | 2 | 2.22 | 1.01 | +65,942 | 0 |

gj1061's outcome is **flat across whether the cartel held or collapsed**.
The hubs' wealth gain is likewise near-constant regardless of label - so it
is mostly normal production and trade, not isolable cartel rent.

## Why: the premium is anchored to the wrong price

The premium *was* applied (58% of buys), yet the effective import price
gj1061 paid stayed ~1.3. The reason the data points to: the "2.0x premium"
multiplies the **hubs' own cheap food price** (~0.26 at production), not
gj1061's willingness-to-pay (3.0+). Two times a tiny number is still tiny.
The lever the agents pull does not reach the price the victim would bear.

## What this means

- **The collusion behaviour is real; the economic damage is not.** This is
  the rigorous, fleet-wide confirmation of the s01 controlled welfare null
  (victim -8%) - and it explains *why*: the price mechanism is mis-anchored.
- **The risk is behavioural, not economic - in this world's calibration.**
  Agents negotiate, enforce, defect, and fabricate; the world simply does
  not yet let that pay.
- **It connects directly to e15.** e15 exists to turn this homeostatic
  economy metastable ("breakable"). This analysis names the specific reason
  it is currently unbreakable: collusion cannot move the victim's price.
  Fixing the premium anchoring (or the e15 two-sided pricing) is what would
  make the cartel bite.

## Caveats

- **Label instability**: re-classifying from the full raw stream produced
  11 `UNPARSEABLE_AGREEMENT` labels and shifted some HELD<->UNPARSEABLE vs
  the earlier scorecard. The economic finding is **label-independent**
  (gj1061 unharmed under every label), but the classifier's precision
  should not be over-trusted; worth a separate look.
- **Premium anchoring is a strong hypothesis**, supported by the import-price
  data (effective ~1.3 with premium applied); confirming it against the
  pricing code is one further step.
- Hub wealth gain is not isolated rent (no per-run no-cartel baseline);
  the clean rent figure remains the s01 controlled -8%.
