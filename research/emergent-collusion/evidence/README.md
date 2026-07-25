# Evidence - Holding the Line

The evidence behind the paper. Every headline claim traces to a receipt here.
All runs use the same prompt (`prompt-cartel-v2.md`) and the same scenario: two
lifeline hubs (Sol, TRAPPIST-1) embargo the food supply to a sole-route
dependent hub (GJ 1061), with autonomous couriers routing by profit. Runs are
deterministic given a seed and compared against a seed-matched no-cartel
baseline.

| Folder / file | What it is |
|---|---|
| `prompt-cartel-v2.md` | The cartel prompt, identical across the origin experiment and both passes. |
| `origin/` | The founding experiment: the first live LLM cartel - Kimi K2.5, two governors, 2000 ticks, seeds 42/7/99/123/2024. Negotiation, self-authored enforcement, defection, and the seed-42 fabrication case. |
| `scorecards/` | Per-model results. `pass1-*`: the five-model matrix (Grok, Sonnet, Gemma, DeepSeek + Kimi as control), 5 seeds each, 1000 ticks. `pass2-labels`: Gemma and Kimi extended to 15 fresh seeds (100-114). |
| `transcripts/` | The full derived message + reasoning log for every run, by pass and model. The primary receipts. |
| `rollups/` | Cross-run analysis: `by-model` (per-model scorecard), `patterns` (cross-run patterns), `claims-ledger` (every headline claim with its receipt), `economic-mechanism-*` (why the economic bite is bounded). |
| `baseline/` | The seed-matched no-cartel reference: per-planet final wealth for all 20 seeds. Every economic figure is a delta against this. |

## Provenance

- **Prompt**: cartel-v2 (`prompt-cartel-v2.md`), identical across the origin, Pass 1, and Pass 2.
- **Scenario**: Sol + TRAPPIST-1 embargo GJ 1061 over a constrained lane network. 1000 ticks (2000 for the origin).
- **Models**: DeepSeek V4 Pro, Grok 4.2, Sonnet 5, Gemma 4.3.1, Kimi K2.5. Origin and control: Kimi K2.5.
- **Labelling**: each run labelled HELD / DEFECTED / COLLAPSED by a reasoned reading of its full decision trace (Claude Opus), not a keyword classifier.
- **Baseline**: the same world and seeds with the cartel policies and governors removed, parity-verified against the runs' T0 state.

Bulk R2 event logs are retained locally for deep reanalysis and are not part of
this published pack.
