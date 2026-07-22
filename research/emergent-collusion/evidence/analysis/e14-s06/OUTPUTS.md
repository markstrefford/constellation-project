# e14-s06 / e14-s07 outputs manifest

The single place that says where each task's data lands. Every task writes its
output to the directory below and nothing stays chat-only. Per-run file + an
INDEX/rollup per task. Two phases: **s06 = per-run** (analysis/e14-s06/),
**s07 = cross-run** (analysis/e14-s07/).

| Task | Script | Output dir | Files | Status |
|---|---|---|---|---|
| raw prompts (source) | pull_decisions.py | `evidence/{pass1,pass2}/decisions/` | `<model>-s<seed>.decisions.json` x50 | done |
| raw events (source) | (from R2) | `evidence/{pass1,pass2}/raw-r2/` | `<run>.events.json.gz` x50 | done |
| baseline (source) | run_baseline.py | `evidence/baseline/raw-r2/` | `baseline-s<seed>...` x20 | done |
| **s06-t1** governor trace | t1_governor_trace.py | `e14-s06/t1-governor-trace/` | `<run>.json`, `<run>.md`, `INDEX.md` | done (50) |
| **s06-t2** telemetry window | t2_telemetry.py | `e14-s06/t2-telemetry/` | `<run>.json`, `<run>.md`, `INDEX.md` | done (50) |
| **s06-t3** galaxy distribution | t3_distribution.py | `e14-s06/t3-distribution/` | `<run>.json`, `<run>.png`, `INDEX.md`, `structure.json` | done (50) |
| **s06-t4** consistency | t4_consistency.py | `e14-s06/t4-consistency/` | `<run>.json`, `<run>.md`, `INDEX.md` | done (50) |
| **s06-t5** economic bite | t5_economic_bite.py (extract) + reasoned labels | `e14-s06/t5-economic-bite/` | `<run>.json`, `bite-rollup.json`, `bite.md`, `INDEX.md` | done (50) |
| **s06-t6** courier wealth | t6_courier_wealth.py | `e14-s06/t6-courier-wealth/` | `<run>.json`, `courier-rollup.json`, `courier.md`, `INDEX.md` | done (50) |
| **s06-t7** dossier assembly | t7_dossier.py (stitch) | `e14-s06/t7-dossiers/` | `<run>.md`, `INDEX.md` | done (50) |
| **s07-t1** per-model rollup | s07_t1_rollup.py | `e14-s07/t1-rollup/` | `by-model.json`, `by-model.md`, `chattiness.json` | pending |
| **s07-t2** cross-run patterns | s07_t2_cross_run.py | `e14-s07/t2-cross-run/` | `patterns.md`, `patterns.json` | pending |
| **s07-t3** synthesis | (assembly, receipted) | `e14-s07/t3-synthesis/` | `synthesis.md`, `e15-handoff.md` | pending |

Superseded / to fold in:
- `per-run/*.json` + `fleet-rollup.json` - the first quantitative harness. Its
  food-price / gate / supply-trace columns are valid and get folded into t2/t3;
  its total-wealth-vs-baseline column is the noisy one t3 handles properly (only
  the victim + cartel-hub deltas reproduce across seeds).
- `t1-timelines/dsv4pro-s99.md` - a one-off demo; superseded by t1-governor-trace.

Convention: each script prints `output -> <path>` on completion. The .md files
are the human-readable distillation; the .json files are the machine spine the
next task consumes.
