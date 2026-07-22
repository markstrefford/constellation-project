#!/usr/bin/env python3
"""
t6 - courier wealth distribution vs seed-matched baseline.

t3/t5 count the 68 fixed planets + hubs; this task adds the mobile-wealth
layer (couriers) so "where did the wealth go" has a complete answer. See
sdlc/work/active/e14-s06-t6-courier-wealth.md.

Separates couriers into three populations at the FINAL-tick AGENT_SNAPSHOT
per run:
  1. gj1061_local   - local_courier, sector_id == "gj1061" (the victim system)
  2. galactic_freighter - agent_class == galactic_freighter (roams all sectors,
     sector_id is always None in the snapshot)
  3. rest_local     - local_courier, sector_id != "gj1061" (reference)

Couriers are spawned per seed, not tracked across runs, so this is
distributional (high/low/mean/spread per population), diffed against the
seed-matched no-cartel baseline population of the same shape.

death_reason on AGENT_SNAPSHOT is always None in the data (verified by
inspection) - the real reason lives on the separate AGENT_DEATH event,
keyed by agent_id, and is joined in here.

Run from repo root: python3 scripts/t6_courier_wealth.py
"""
import gzip
import json
import re
import statistics
from collections import defaultdict
from pathlib import Path

EVIDENCE = Path(
    "/Users/mark/Development/constellation-research/research/emergent-collusion/evidence"
)
OUT_DIR = EVIDENCE / "analysis/e14-s06/t6-courier-wealth"
PASS_DIRS = [EVIDENCE / "pass1/raw-r2", EVIDENCE / "pass2/raw-r2"]
BASELINE_DIR = EVIDENCE / "baseline/raw-r2"

VICTIM_SECTOR = "gj1061"
POPULATIONS = ("gj1061_local", "galactic_freighter", "rest_local")
POP_LABEL = {
    "gj1061_local": "gj1061-local couriers (victim system)",
    "galactic_freighter": "galactic freighters (cross-sector roamers)",
    "rest_local": "rest-of-galaxy local couriers (reference)",
}

STEM_RE = re.compile(r"^(?P<model>.+)-s(?P<seed>\d+)$")


def load_events(path):
    with gzip.open(path, "rt") as f:
        return json.load(f)


def population_of(snap):
    if snap["agent_class"] == "galactic_freighter":
        return "galactic_freighter"
    if snap["sector_id"] == VICTIM_SECTOR:
        return "gj1061_local"
    return "rest_local"


def extract_final_snapshot(data):
    """Final-tick AGENT_SNAPSHOT per agent, split into the 3 populations,
    with death_reason joined from AGENT_DEATH (agent_id)."""
    events = data["events"]
    snaps = [e for e in events if e["kind"] == "AGENT_SNAPSHOT"]
    if not snaps:
        return None
    final_tick = max(e["tick"] for e in snaps)
    finals = [e for e in snaps if e["tick"] == final_tick]

    death_reason = {}
    for e in events:
        if e["kind"] == "AGENT_DEATH":
            death_reason[e["agent_id"]] = e.get("reason")

    pops = defaultdict(list)
    for s in finals:
        pop = population_of(s)
        pops[pop].append(
            {
                "agent": s["agent"],
                "wealth": s["wealth"],
                "alive": s["alive"],
                "death_reason": death_reason.get(s["agent"]),
            }
        )
    return {"final_tick": final_tick, "populations": dict(pops)}


def stats_for(records):
    wealth = [r["wealth"] for r in records]
    n = len(wealth)
    dead = [r for r in records if not r["alive"]]
    reasons = defaultdict(int)
    for r in dead:
        reasons[r["death_reason"] or "unknown"] += 1
    return {
        "n": n,
        "mean": statistics.fmean(wealth) if n else None,
        "min": min(wealth) if n else None,
        "max": max(wealth) if n else None,
        "median": statistics.median(wealth) if n else None,
        "stdev": statistics.pstdev(wealth) if n > 1 else 0.0,
        "n_dead": len(dead),
        "death_reasons": dict(reasons),
    }


def stats_delta(cartel_stats, baseline_stats):
    def d(k):
        if cartel_stats[k] is None or baseline_stats[k] is None:
            return None
        return cartel_stats[k] - baseline_stats[k]

    return {
        "mean": d("mean"),
        "min": d("min"),
        "max": d("max"),
        "median": d("median"),
        "n_dead": cartel_stats["n_dead"] - baseline_stats["n_dead"],
    }


def process_run(path, baseline_cache, errors):
    stem = path.name.replace(".events.json.gz", "")
    m = STEM_RE.match(stem)
    if not m:
        errors.append((stem, "cannot parse model/seed from filename"))
        return None
    model = m.group("model")
    seed = int(m.group("seed"))

    try:
        data = load_events(path)
    except Exception as e:  # noqa: BLE001
        errors.append((stem, f"load error: {e}"))
        return None

    extracted = extract_final_snapshot(data)
    del data
    if extracted is None:
        errors.append((stem, "no AGENT_SNAPSHOT events"))
        return None

    if seed not in baseline_cache:
        bpath = BASELINE_DIR / f"baseline-s{seed}.events.json.gz"
        if not bpath.exists():
            baseline_cache[seed] = None
        else:
            bdata = load_events(bpath)
            baseline_cache[seed] = extract_final_snapshot(bdata)
            del bdata
    baseline = baseline_cache[seed]
    if baseline is None:
        errors.append((stem, f"no baseline for seed {seed}"))
        return None

    pop_out = {}
    for pop in POPULATIONS:
        c_records = extracted["populations"].get(pop, [])
        b_records = baseline["populations"].get(pop, [])
        c_stats = stats_for(c_records)
        b_stats = stats_for(b_records)
        pop_out[pop] = {
            "cartel": c_stats,
            "baseline": b_stats,
            "delta": stats_delta(c_stats, b_stats),
            "cartel_agents": c_records,
            "baseline_agents": b_records,
        }

    run_out = {
        "run_id": stem,
        "model": model,
        "seed": seed,
        "source_file": str(path.relative_to(EVIDENCE)),
        "baseline_file": f"baseline/raw-r2/baseline-s{seed}.events.json.gz",
        "final_tick": extracted["final_tick"],
        "baseline_final_tick": baseline["final_tick"],
        "populations": pop_out,
    }
    (OUT_DIR / f"{stem}.json").write_text(json.dumps(run_out, indent=2))
    return run_out


def pool_group(run_results, model_filter=None):
    pooled = {}
    for pop in POPULATIONS:
        cartel_records = []
        baseline_records = []
        for r in run_results:
            if model_filter and r["model"] != model_filter:
                continue
            cartel_records.extend(r["populations"][pop]["cartel_agents"])
            baseline_records.extend(r["populations"][pop]["baseline_agents"])
        c_stats = stats_for(cartel_records)
        b_stats = stats_for(baseline_records)
        pooled[pop] = {
            "cartel": c_stats,
            "baseline": b_stats,
            "delta": stats_delta(c_stats, b_stats),
        }
    return pooled


def build_rollup(run_results, errors):
    models = sorted(set(r["model"] for r in run_results))
    rollup = {
        "n_runs_ok": len(run_results),
        "n_runs_total": len(run_results) + len(errors),
        "errors": [{"run": s, "error": e} for s, e in errors],
        "fleet": pool_group(run_results),
        "by_model": {
            m: {
                "n_runs": sum(1 for r in run_results if r["model"] == m),
                **pool_group(run_results, model_filter=m),
            }
            for m in models
        },
    }
    path = OUT_DIR / "courier-rollup.json"
    path.write_text(json.dumps(rollup, indent=2))
    print(f"output -> {path}")
    return rollup


def fmt(x, nd=1):
    if x is None:
        return "n/a"
    return f"{x:,.{nd}f}"


def direction(delta_mean):
    if delta_mean is None:
        return "n/a"
    if delta_mean > 1e-6:
        return "richer"
    if delta_mean < -1e-6:
        return "poorer"
    return "flat"


def build_markdown(run_results, rollup):
    lines = []
    lines.append("# t6 - courier wealth distribution vs baseline")
    lines.append("")
    lines.append(
        f"{rollup['n_runs_ok']}/{rollup['n_runs_total']} runs parsed. "
        "Final-tick AGENT_SNAPSHOT wealth, three courier populations, "
        "diffed against the seed-matched no-cartel baseline (same "
        "population, same seed)."
    )
    lines.append("")

    # Fleet-wide table
    lines.append("## Fleet-wide (all runs pooled, baseline replicated per matched cartel run)")
    lines.append("")
    lines.append(
        "| population | n | cartel mean | baseline mean | delta mean | direction | "
        "cartel min | baseline min | cartel max | baseline max | cartel dead | baseline dead |"
    )
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for pop in POPULATIONS:
        d = rollup["fleet"][pop]
        c, b, delta = d["cartel"], d["baseline"], d["delta"]
        lines.append(
            f"| {POP_LABEL[pop]} | {c['n']} | {fmt(c['mean'])} | {fmt(b['mean'])} | "
            f"{fmt(delta['mean'])} | {direction(delta['mean'])} | {fmt(c['min'])} | "
            f"{fmt(b['min'])} | {fmt(c['max'])} | {fmt(b['max'])} | "
            f"{c['n_dead']} | {b['n_dead']} |"
        )
    lines.append("")

    # Per-model tables
    lines.append("## Per-model")
    lines.append("")
    for model in sorted(rollup["by_model"]):
        mb = rollup["by_model"][model]
        lines.append(f"### {model} ({mb['n_runs']} runs)")
        lines.append("")
        lines.append(
            "| population | n | cartel mean | baseline mean | delta mean | direction | "
            "cartel min | cartel max | cartel dead | baseline dead |"
        )
        lines.append("|---|---|---|---|---|---|---|---|---|---|")
        for pop in POPULATIONS:
            d = mb[pop]
            c, b, delta = d["cartel"], d["baseline"], d["delta"]
            lines.append(
                f"| {POP_LABEL[pop]} | {c['n']} | {fmt(c['mean'])} | {fmt(b['mean'])} | "
                f"{fmt(delta['mean'])} | {direction(delta['mean'])} | {fmt(c['min'])} | "
                f"{fmt(c['max'])} | {c['n_dead']} | {b['n_dead']} |"
            )
        lines.append("")

    # Death reasons
    lines.append("## Death reasons (fleet-wide, cartel runs)")
    lines.append("")
    lines.append("| population | cartel death reasons | baseline death reasons |")
    lines.append("|---|---|---|")
    for pop in POPULATIONS:
        d = rollup["fleet"][pop]
        lines.append(
            f"| {POP_LABEL[pop]} | {d['cartel']['death_reasons']} | "
            f"{d['baseline']['death_reasons']} |"
        )
    lines.append("")

    if rollup["errors"]:
        lines.append("## Parse errors")
        lines.append("")
        for e in rollup["errors"]:
            lines.append(f"- {e['run']}: {e['error']}")
        lines.append("")

    path = OUT_DIR / "courier.md"
    path.write_text("\n".join(lines))
    print(f"output -> {path}")


def build_index(run_results, errors):
    lines = ["# t6 courier-wealth index", ""]
    lines.append(
        "| run | gj1061-local delta mean | freighter delta mean | rest delta mean | status |"
    )
    lines.append("|---|---|---|---|---|")
    for r in run_results:
        g = r["populations"]["gj1061_local"]["delta"]["mean"]
        f_ = r["populations"]["galactic_freighter"]["delta"]["mean"]
        rest = r["populations"]["rest_local"]["delta"]["mean"]
        lines.append(f"| {r['run_id']} | {fmt(g)} | {fmt(f_)} | {fmt(rest)} | ok |")
    for stem, err in errors:
        lines.append(f"| {stem} | - | - | - | ERROR: {err} |")
    path = OUT_DIR / "INDEX.md"
    path.write_text("\n".join(lines) + "\n")
    print(f"output -> {path}")


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    run_files = []
    for d in PASS_DIRS:
        run_files.extend(sorted(d.glob("*.events.json.gz")))
    total = len(run_files)

    baseline_cache = {}
    run_results = []
    errors = []
    for i, path in enumerate(run_files, 1):
        print(f"run {i}/{total}: {path.name}", flush=True)
        out = process_run(path, baseline_cache, errors)
        if out is not None:
            run_results.append(out)

    rollup = build_rollup(run_results, errors)
    build_markdown(run_results, rollup)
    build_index(run_results, errors)

    if errors:
        print(f"WARNING: {len(errors)} run(s) failed to parse:")
        for stem, err in errors:
            print(f"  {stem}: {err}")
    print(f"done: {len(run_results)}/{total} runs ok")


if __name__ == "__main__":
    main()
