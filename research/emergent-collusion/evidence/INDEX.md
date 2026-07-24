# Evidence index - emergent collusion

Manifest of the evidence pack, organised by experimental pass. Status is
authoritative in each folder's `META.yaml`. Publication is status-gated
(see repo `CLAUDE.md`); `raw-r2/` is gitignored (bulk event logs, local
analysis only).

| Folder | Status | What it is |
|---|---|---|
| `origin-s01/` | draft | The founding experiment: the first live LLM cartel (Kimi k2.5) - negotiation, self-authored enforcement, defection, the seed-42 fabrication. Kept distinct (2000-tick, kimi-only). |
| `pass1/` | draft | The rigorous five-model matrix: grok, sonnet, gemma, deepseek x 5 seeds, kimi as the s01 control. `results/` (scorecard + findings), `raw-r2/` (20 full event logs), `transcripts/`. |
| `pass2/` | draft | gemma + kimi extended to 15 new seeds (100-114). `results/` (labels), `raw-r2/` (30 full event logs), `transcripts/`, and `provisional/` (unverified in-session analysis - see its README). |
| `shared/` | - | `prompt-cartel-v2.md` - the prompt, identical across both passes and the origin. |

## What is rigorous vs provisional

- **Rigorous / committed evidence**: `pass1/results/`, `pass2/results/`,
  the transcripts, and the raw logs. These are the trustworthy inputs.
- **Provisional / not established**: everything under
  `pass2/provisional/` - ad-hoc in-session analysis (including the economic
  "welfare null" conclusion, which was drawn from a single run and is NOT
  reliable). Read `pass2/provisional/README.md` first.

## Provenance at a glance

- **Scenario**: s01 live cartel (`cartel-run.yaml`) - Sol + TRAPPIST-1 hubs
  embargo the sole-route dependent gj1061 hub. 1000 ticks (2000 for origin).
- **Prompt**: cartel-v2, identical across passes (`shared/prompt-cartel-v2.md`;
  also embedded verbatim in every run's decisions.json).
- **Manifests** (in the sim repo): `e14-s05-manifest.json` (Pass 1),
  `e14-s05-pass2-manifest.json` (Pass 2).
- **raw-r2/**: `<model>-s<seed>.events.json.gz` - the complete R2 event
  stream per run (events + final snapshot).

## Status legend

- **draft** - work in progress; not committed.
- **approved** - cleared to publish; commit this folder, push, then set published.
- **published** - live on the public repo.
