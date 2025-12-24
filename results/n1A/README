# CONSTELLATION: Three-Way Comparison

## Summary Table

| Metric | Mechanical (0 LLM) | Partial LLM (4/15) | Full LLM (15/15) |
|--------|-------------------|-------------------|------------------|
| **Agent Survival** | 100% | 100% | 100% |
| **Agent Total Wealth** | $248,873 | $337,946 | **$351,894** |
| **Agent Mean Wealth** | $12,444 | $16,897 | **$17,595** |
| **Planet Mortality** | 53% (8/15) | 33% (5/15) | **47% (7/15)** |
| **Healthy Planets** | 4/15 | 6/15 | 5/15 |
| **Trade Volume** | 1,103 | 1,262 | 597 |
| **Max Price Spike** | $80 | $223 | **$392** |

## Key Findings

### 1. WEALTH: Full LLM Wins
- $351K total wealth vs $338K (partial) vs $249K (mechanical)
- **41% improvement** over mechanical baseline
- Agents consistently profitable despite planet struggles

### 2. PLANET MORTALITY: Partial LLM Wins
- Mechanical: 8 planets critical (53%)
- **Partial LLM: 5 planets critical (33%)** ← Best outcome
- Full LLM: 7 planets critical (47%)

### 3. THE PARADOX: More Intelligence ≠ Better Outcomes
Full LLM performed WORSE than partial LLM for planet survival. Why?

**Hypothesis: Competition vs Coordination**
- Partial LLM: 4 smart planets + 11 mechanical = hybrid stability
- Full LLM: 15 smart planets all competing = destructive competition

### 4. TRADE COLLAPSE
- Mechanical: 1,103 trades
- Partial LLM: 1,262 trades
- Full LLM: **597 trades** (53% drop!)

Fewer trades despite more "intelligent" pricing. The LLM planets may have been pricing each other out of the market.

**Critical Finding: Trade Efficiency Collapsed**
```
Full LLM Run:
- Total departures: 3,628
- Total trades: 597
- Trade efficiency: 16% (only 16 trades per 100 trips!)
- Continuing deliveries: 1,211
- Refuel events: 436
```

Agents were traveling constantly but only trading 16% of the time. The rest were:
- Repositioning (chasing better opportunities)
- Refueling
- Carrying cargo long distances

**Jupiter's Fuel Mountain:**
Jupiter accumulated **69,956 fuel_raw** (1000 ticks × 100/tick - pickups)
Only 245 fuel_raw buys in 1000 ticks!
The supply chain was massively undersupplied.

### 5. PRICE VOLATILITY EXPLOSION
- Mechanical max: $80
- Partial LLM max: $223
- Full LLM max: **$392**

More LLM = more price signals = more volatility = market confusion?

## Planet-by-Planet Comparison (Final Refined Fuel Stock)

| Planet | Mechanical | Partial LLM | Full LLM |
|--------|------------|-------------|----------|
| Jupiter | **67.2** | 66.5 | 42.5 |
| Earth | 152.9 | **156.1** | 51.3 |
| Venus | 29.5 | **43.7** | 37.9 |
| Mercury | 15.5 | 13.9 | **27.2** |
| Moon | 4.2 | **16.5** | 5.1 |
| Mars | 0.9 | **145.3** | 1.0 |
| Ceres | 0.8 | 0.8 | 0.8 |
| Vesta | **48.4** | 3.7 | 10.0 |
| Pallas | **51.4** | 51.4 | 10.9 |
| Hygiea | 2.0 | **47.0** | 1.1 |
| Psyche | 2.6 | 3.3 | **69.7** |
| Eros | 1.9 | **15.1** | 1.2 |
| Saturn | 1.0 | **2.7** | 1.0 |
| Uranus | 0.8 | 0.8 | 0.7 |
| Neptune | **64.2** | 48.7 | 3.4 |

**Bold = best outcome for that planet.** Ceres and Uranus critical in all three experiments.

### The Mars Miracle REVERSED
- Partial LLM: Mars 0.9 → 145.3 (saved!)
- Full LLM: Mars 145.3 → 1.0 (crashed!)

With 4 LLM planets, Mars (as transit) was a beneficiary.
With 15 LLM planets, Mars became a competitor and lost.

## What Happened?

### The Food Rush (Tick 550 Snapshot)
At tick 550, we observed:
- 9/20 agents hauling food to Saturn ($67 price)
- Jupiter sitting on 40,000 fuel_raw (nobody picking up)
- Earth, Mars, Ceres all at ~1.0 refined fuel

**The LLM planets accidentally created a "gold rush"** for food that starved the fuel supply chain.

### Wild Oscillations (Stock Timeline)
```
Planet  | T100  | T200  | T400  | T600  | T800  | T1000
--------|-------|-------|-------|-------|-------|-------
Mars    |  83.9 |   1.0 |   2.1 | 233.4 |   1.0 |   1.0
Saturn  |   1.0 |  33.2 |   1.0 |   1.9 |   1.0 |   1.0
Earth   |  83.2 |   4.4 |   1.1 | 326.7 |   4.1 |  51.3
```

Planets swung wildly between healthy (200+) and critical (1.0).
The system never stabilized into a sustainable equilibrium.

### Delivery Distribution
| Planet | Partial LLM | Full LLM |
|--------|-------------|----------|
| Mars | 64 | 44 |
| Saturn | ~80 | 74 |
| Ceres | ~15 | 10 |

Fewer deliveries to transit nodes in full LLM run.

## Research Implications

### 1. Optimal LLM Ratio
- 0% LLM (mechanical): Poor outcomes
- 27% LLM (4/15): **Best planet outcomes**
- 100% LLM (15/15): Better wealth, worse planets

There may be an **optimal ratio** of intelligent to mechanical agents in a system.

### 2. Emergent Competition
When all agents are "intelligent," they may:
- All pursue the same high-margin opportunities (food rush)
- Create price wars that destabilize markets
- Fail to coordinate on system-level needs (fuel distribution)

### 3. The Value of "Dumb" Actors
Mechanical planets provided stable, predictable behavior.
This stability may be necessary for intelligent actors to optimize against.
Remove the stability → system chaos.

### 4. Coordination Failure
Despite 15 LLM planets with the ability to reason about the system:
- None coordinated fuel deliveries to critical nodes
- None sacrificed local optimization for global stability
- The "tragedy of the commons" played out

## Questions for Future Research

1. **Would explicit coordination mechanisms help?**
   - Planets sharing information
   - Collective pricing agreements
   - Central planning vs market

2. **What's the optimal LLM ratio?**
   - 27% was better than 100%
   - Is there a sweet spot? 40%? 50%?

3. **Can LLMs learn to coordinate?**
   - Current: Each LLM optimizes locally
   - Future: LLMs with system-level awareness?

4. **Role of archetype diversity**
   - Producer/Consumer/Transit/Outpost
   - Does the mix matter more than the intelligence?

## Conclusion

**Full LLM control produced the wealthiest agents but the most unstable economy.**

The system traded stability for profitability. Agents made more money, but the underlying infrastructure (transit nodes, fuel distribution) suffered.

This may mirror real-world observations about markets:
- Too much optimization → instability
- Diversity of strategies → resilience
- "Dumb money" may serve a systemic function

**Headline:** *"100% AI control increased agent wealth by 41% while simultaneously destabilizing 47% of the planetary economy."*
