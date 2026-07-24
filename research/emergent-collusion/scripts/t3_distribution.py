#!/usr/bin/env python3
"""
t3 - galaxy end-state distribution (the wide impact).

Mechanical extraction, no interpretation. For each of the 50 cartel runs
(pass1 + pass2) plus the 20 seed-matched no-cartel baseline runs, pulls the
FINAL-tick PLANET_SNAPSHOT for all 68 planets/hubs and reports:

  - wealth per planet, diffed against the seed-matched baseline
    (baseline/baseline-final-wealth.json is the authoritative baseline wealth
    source per spec; this script cross-checks it against its own parse of
    the baseline event files and warns on any mismatch)
  - health per planet: there is no "health" field in PLANET_SNAPSHOT. The
    closest proxies are `health_multiplier` (float, production/consumption
    penalty factor) and `alive` (bool). Both are reported; the absence of a
    single "health" scalar is noted here rather than invented.
  - asset price stats (food, fuel_raw, fuel_refined) across all 68 planets:
    min, max, mean, median, std, and a skew statistic (Pearson's second
    skewness coefficient: 3*(mean-median)/std - no scipy dependency).

Outputs per run: <run>.json + <run>.png (sorted wealth-delta-vs-baseline bar,
diverging color, victim + cartel hubs called out). Then INDEX.md (one row per
run) and structure.json (cross-seed / cross-model reproducibility: which
planets move the same way in (almost) every run vs which move only in some).

See sdlc/work/active/e14-s06-t3-galaxy-distribution.md for the task spec and
evidence/analysis/e14-s06/OUTPUTS.md for the manifest this feeds.

Run from repo root: python3 scripts/t3_distribution.py
"""
import gzip
import json
import re
import statistics
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

EVIDENCE = Path(
    "/Users/mark/Development/constellation-research/research/emergent-collusion/evidence"
)
OUT_DIR = EVIDENCE / "analysis/e14-s06/t3-distribution"
PASS_DIRS = [
    ("pass1", EVIDENCE / "pass1/raw-r2"),
    ("pass2", EVIDENCE / "pass2/raw-r2"),
]
BASELINE_DIR = EVIDENCE / "baseline/raw-r2"
BASELINE_WEALTH_PATH = EVIDENCE / "baseline/baseline-final-wealth.json"

VICTIM = "gj1061-hub"
CARTEL_HUBS = ("sol-hub", "trappist1-hub")
ASSETS = ("food", "fuel_raw", "fuel_refined")

STEM_RE = re.compile(r"^(?P<model>.+)-s(?P<seed>\d+)$")

# Diverging palette (dataviz skill reference palette): blue = gain, red =
# loss, gray = neutral midpoint.
COLOR_GAIN = "#2a78d6"
COLOR_LOSS = "#e34948"
COLOR_NEUTRAL = "#c3c2b7"
COLOR_VICTIM = "#eda100"  # yellow - victim callout
COLOR_CARTEL = "#4a3aa7"  # violet - cartel hub callout
COLOR_AXIS = "#898781"
COLOR_GRID = "#e1e0d9"
COLOR_TEXT = "#0b0b0b"


def load_events(path):
    with gzip.open(path, "rt") as f:
        return json.load(f)


def final_snapshot(data):
    """Return {planet: last-tick PLANET_SNAPSHOT dict} and the final tick number."""
    snaps = [e for e in data["events"] if e["kind"] == "PLANET_SNAPSHOT"]
    if not snaps:
        return {}, None
    last_tick = max(e["tick"] for e in snaps)
    finals = {e["planet"]: e for e in snaps if e["tick"] == last_tick}
    return finals, last_tick


def pearson_skew(values):
    if len(values) < 2:
        return 0.0
    mean = statistics.mean(values)
    median = statistics.median(values)
    std = statistics.pstdev(values)
    if std == 0:
        return 0.0
    return 3 * (mean - median) / std


def dist_stats(values):
    return {
        "min": min(values),
        "max": max(values),
        "mean": statistics.mean(values),
        "median": statistics.median(values),
        "std": statistics.pstdev(values),
        "skew": pearson_skew(values),
    }


def load_baseline_snapshots():
    """Parse all 20 baseline event files once. Returns {seed: {planet: snap}}."""
    out = {}
    files = sorted(BASELINE_DIR.glob("baseline-s*.events.json.gz"))
    print(f"loading {len(files)} baseline runs for final-tick reference snapshots...")
    for i, path in enumerate(files, 1):
        m = re.match(r"^baseline-s(?P<seed>\d+)\.events\.json\.gz$", path.name)
        seed = m.group("seed")
        try:
            data = load_events(path)
            finals, last_tick = final_snapshot(data)
        except Exception as exc:
            print(f"  FAILED to parse {path.name}: {exc}")
            continue
        out[seed] = {"finals": finals, "final_tick": last_tick}
        print(f"  baseline {i}/{len(files)}: seed {seed}, tick {last_tick}, {len(finals)} planets")
        del data
    return out


def planet_record(snap, baseline_snap, baseline_wealth):
    wealth = snap["wealth"]
    rec = {
        "wealth": wealth,
        "health_multiplier": snap.get("health_multiplier"),
        "alive": snap.get("alive"),
        "prices": {a: snap["prices"].get(a) for a in ASSETS if a in snap.get("prices", {})},
    }
    if baseline_wealth is not None:
        rec["wealth_baseline"] = baseline_wealth
        rec["wealth_delta"] = wealth - baseline_wealth
        rec["wealth_delta_pct"] = (
            100.0 * (wealth - baseline_wealth) / baseline_wealth if baseline_wealth else None
        )
    if baseline_snap is not None:
        rec["health_multiplier_baseline"] = baseline_snap.get("health_multiplier")
        rec["alive_baseline"] = baseline_snap.get("alive")
    return rec


def build_run_record(run_id, model, seed, pass_name, data, baseline_by_seed, baseline_wealth_by_seed):
    finals, final_tick = final_snapshot(data)
    if not finals:
        return None

    seed_str = str(seed)
    baseline_entry = baseline_by_seed.get(seed_str)
    baseline_finals = baseline_entry["finals"] if baseline_entry else {}
    baseline_wealth_map = baseline_wealth_by_seed.get(seed_str, {})

    # cross-check baseline-final-wealth.json against our own baseline parse
    mismatch_count = 0
    for planet, bw in baseline_wealth_map.items():
        bsnap = baseline_finals.get(planet)
        if bsnap is not None and abs(bsnap["wealth"] - bw) > max(1.0, 0.001 * abs(bw)):
            mismatch_count += 1

    planets = {}
    for planet, snap in finals.items():
        bw = baseline_wealth_map.get(planet)
        bsnap = baseline_finals.get(planet)
        planets[planet] = planet_record(snap, bsnap, bw)

    wealth_deltas = [p["wealth_delta"] for p in planets.values() if "wealth_delta" in p]

    price_stats = {}
    for asset in ASSETS:
        vals = [p["prices"][asset] for p in planets.values() if asset in p["prices"]]
        if vals:
            stats = dist_stats(vals)
            max_planet = max(planets.items(), key=lambda kv: kv[1]["prices"].get(asset, float("-inf")))[0]
            min_planet = min(planets.items(), key=lambda kv: kv[1]["prices"].get(asset, float("inf")))[0]
            stats["max_planet"] = max_planet
            stats["min_planet"] = min_planet
            price_stats[asset] = stats

    n_alive = sum(1 for p in planets.values() if p.get("alive"))
    n_dead = len(planets) - n_alive
    dead_planets = sorted(p for p, v in planets.items() if not v.get("alive"))
    n_alive_baseline = sum(1 for p in baseline_finals.values() if p.get("alive"))
    n_dead_baseline = len(baseline_finals) - n_alive_baseline if baseline_finals else None
    dead_planets_baseline = (
        sorted(p for p, s in baseline_finals.items() if not s.get("alive")) if baseline_finals else []
    )

    sorted_by_delta = sorted(
        ((p, v["wealth_delta"]) for p, v in planets.items() if "wealth_delta" in v),
        key=lambda kv: kv[1],
    )
    top_loss = sorted_by_delta[:5]
    top_gain = sorted_by_delta[-5:][::-1]

    def highlight(planet):
        v = planets.get(planet, {})
        return {
            "planet": planet,
            "wealth": v.get("wealth"),
            "wealth_baseline": v.get("wealth_baseline"),
            "wealth_delta": v.get("wealth_delta"),
            "wealth_delta_pct": v.get("wealth_delta_pct"),
            "health_multiplier": v.get("health_multiplier"),
            "health_multiplier_baseline": v.get("health_multiplier_baseline"),
            "alive": v.get("alive"),
        }

    record = {
        "run_id": run_id,
        "model": model,
        "seed": int(seed),
        "pass": pass_name,
        "final_tick": final_tick,
        "n_planets": len(planets),
        "n_alive": n_alive,
        "n_dead": n_dead,
        "dead_planets": dead_planets,
        "n_dead_baseline": n_dead_baseline,
        "dead_planets_baseline": dead_planets_baseline,
        "baseline_available": bool(baseline_entry),
        "baseline_wealth_mismatch_count": mismatch_count,
        "planets": planets,
        "price_stats": price_stats,
        "wealth_delta_stats": dist_stats(wealth_deltas) if wealth_deltas else None,
        "highlights": {
            "victim": highlight(VICTIM),
            "cartel_hubs": {h: highlight(h) for h in CARTEL_HUBS},
            "top_gain": [{"planet": p, "wealth_delta": d} for p, d in top_gain],
            "top_loss": [{"planet": p, "wealth_delta": d} for p, d in top_loss],
        },
    }
    return record


def make_chart(record, out_path):
    planets = record["planets"]
    items = [(p, v["wealth_delta"]) for p, v in planets.items() if "wealth_delta" in v]
    if not items:
        return False
    items.sort(key=lambda kv: kv[1])
    names = [p for p, _ in items]
    deltas = [d for _, d in items]

    colors = []
    for p, d in zip(names, deltas):
        if p == VICTIM:
            colors.append(COLOR_VICTIM)
        elif p in CARTEL_HUBS:
            colors.append(COLOR_CARTEL)
        else:
            colors.append(COLOR_GAIN if d >= 0 else COLOR_LOSS)

    fig, ax = plt.subplots(figsize=(9, 12))
    y = range(len(names))
    ax.barh(y, deltas, color=colors, height=0.8)
    ax.axvline(0, color=COLOR_AXIS, linewidth=1)
    ax.set_yticks(list(y))
    ax.set_yticklabels(names, fontsize=5, color=COLOR_TEXT)
    ax.tick_params(axis="x", colors=COLOR_TEXT, labelsize=8)
    ax.set_xlabel("wealth delta vs seed-matched baseline (cartel - baseline)", color=COLOR_TEXT, fontsize=9)
    ax.set_title(
        f"{record['run_id']} - galaxy wealth delta at tick {record['final_tick']}\n"
        f"(orange=victim gj1061-hub, purple=cartel hub, blue=gain, red=loss)",
        color=COLOR_TEXT,
        fontsize=10,
    )
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for spine in ("left", "bottom"):
        ax.spines[spine].set_color(COLOR_AXIS)
    ax.grid(axis="x", color=COLOR_GRID, linewidth=0.5, zorder=0)
    ax.set_axisbelow(True)
    fig.tight_layout()
    fig.savefig(out_path, dpi=140, facecolor="#fcfcfb")
    plt.close(fig)
    return True


def collect_run_files():
    runs = []
    for pass_name, d in PASS_DIRS:
        for path in sorted(d.glob("*.events.json.gz")):
            stem = path.name.replace(".events.json.gz", "")
            m = STEM_RE.match(stem)
            if not m:
                print(f"  WARNING: could not parse model/seed from {path.name}")
                continue
            runs.append((pass_name, path, m.group("model"), m.group("seed")))
    return runs


def build_structure(records):
    """Cross-seed / cross-model reproducibility of per-planet wealth-delta sign."""
    per_planet = {}
    per_planet_by_model = {}
    all_planets = set()
    for r in records:
        for p, v in r["planets"].items():
            if "wealth_delta" not in v:
                continue
            all_planets.add(p)
            per_planet.setdefault(p, []).append(v["wealth_delta"])
            per_planet_by_model.setdefault(r["model"], {}).setdefault(p, []).append(v["wealth_delta"])

    def summarize(deltas):
        n = len(deltas)
        n_pos = sum(1 for d in deltas if d > 0)
        n_neg = sum(1 for d in deltas if d < 0)
        n_zero = n - n_pos - n_neg
        sign_consistency = max(n_pos, n_neg) / n if n else 0.0
        return {
            "n_runs": n,
            "mean_delta": statistics.mean(deltas),
            "median_delta": statistics.median(deltas),
            "std_delta": statistics.pstdev(deltas) if n > 1 else 0.0,
            "min_delta": min(deltas),
            "max_delta": max(deltas),
            "pct_positive": n_pos / n if n else 0.0,
            "pct_negative": n_neg / n if n else 0.0,
            "pct_zero": n_zero / n if n else 0.0,
            "sign_consistency": sign_consistency,
        }

    per_planet_summary = {p: summarize(deltas) for p, deltas in per_planet.items()}
    per_planet_by_model_summary = {
        model: {p: summarize(deltas) for p, deltas in pmap.items()}
        for model, pmap in per_planet_by_model.items()
    }

    # Reproducing: consistent sign in >=90% of runs AND a mean move that
    # clears run-to-run noise (|mean| > std, so the sign isn't an artifact
    # of a fat-tailed distribution straddling zero).
    reproducing = []
    run_specific = []
    for p, s in per_planet_summary.items():
        if s["n_runs"] < 5:
            continue
        clears_noise = abs(s["mean_delta"]) > s["std_delta"] if s["std_delta"] > 0 else True
        if s["sign_consistency"] >= 0.9 and clears_noise:
            reproducing.append((p, s))
        elif s["sign_consistency"] < 0.75 or not clears_noise:
            run_specific.append((p, s))

    reproducing.sort(key=lambda kv: abs(kv[1]["mean_delta"]), reverse=True)
    run_specific.sort(key=lambda kv: abs(kv[1]["mean_delta"]), reverse=True)

    return {
        "n_runs": len(records),
        "n_planets": len(all_planets),
        "per_planet": per_planet_summary,
        "per_planet_by_model": per_planet_by_model_summary,
        "reproducing_planets": [
            {"planet": p, **s} for p, s in reproducing
        ],
        "run_specific_planets": [
            {"planet": p, **s} for p, s in run_specific
        ],
    }


def write_index(records, out_dir):
    lines = [
        "# t3 - galaxy end-state distribution - INDEX",
        "",
        "Per-run summary: victim (gj1061-hub) and cartel-hub (sol-hub,",
        "trappist1-hub) wealth delta vs seed-matched baseline, galaxy-wide",
        "wealth-delta distribution shape (mean/median/skew), food-price skew,",
        "and dead-planet counts. Full per-planet data in `<run>.json`; chart",
        "in `<run>.png`. See `structure.json` for cross-seed reproducibility.",
        "",
        "| run | model | seed | victim delta | victim delta % | sol-hub delta | trappist1-hub delta | "
        "galaxy mean delta | galaxy median delta | galaxy delta skew | food price skew | n dead (cartel/baseline) |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in records:
        v = r["highlights"]["victim"]
        sol = r["highlights"]["cartel_hubs"].get("sol-hub", {})
        tra = r["highlights"]["cartel_hubs"].get("trappist1-hub", {})
        wds = r["wealth_delta_stats"] or {}
        food = r["price_stats"].get("food", {})
        lines.append(
            "| {run} | {model} | {seed} | {vd} | {vdp} | {sold} | {trad} | {gmean} | {gmed} | {gskew} | {fskew} | {nd}/{ndb} |".format(
                run=r["run_id"],
                model=r["model"],
                seed=r["seed"],
                vd=f"{v['wealth_delta']:.0f}" if v.get("wealth_delta") is not None else "n/a",
                vdp=f"{v['wealth_delta_pct']:.1f}%" if v.get("wealth_delta_pct") is not None else "n/a",
                sold=f"{sol.get('wealth_delta'):.0f}" if sol.get("wealth_delta") is not None else "n/a",
                trad=f"{tra.get('wealth_delta'):.0f}" if tra.get("wealth_delta") is not None else "n/a",
                gmean=f"{wds.get('mean'):.0f}" if wds.get("mean") is not None else "n/a",
                gmed=f"{wds.get('median'):.0f}" if wds.get("median") is not None else "n/a",
                gskew=f"{wds.get('skew'):.2f}" if wds.get("skew") is not None else "n/a",
                fskew=f"{food.get('skew'):.2f}" if food.get("skew") is not None else "n/a",
                nd=r["n_dead"],
                ndb=r["n_dead_baseline"] if r["n_dead_baseline"] is not None else "n/a",
            )
        )
    (out_dir / "INDEX.md").write_text("\n".join(lines) + "\n")


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    baseline_wealth_by_seed = json.loads(BASELINE_WEALTH_PATH.read_text())
    baseline_by_seed = load_baseline_snapshots()

    run_files = collect_run_files()
    total = len(run_files)
    print(f"found {total} cartel runs to process")

    records = []
    failed = []
    for i, (pass_name, path, model, seed) in enumerate(run_files, 1):
        run_id = f"{model}-s{seed}"
        print(f"run {i}/{total}: {run_id} ({pass_name})")
        try:
            data = load_events(path)
            rec = build_run_record(
                run_id, model, seed, pass_name, data, baseline_by_seed, baseline_wealth_by_seed
            )
            del data
        except Exception as exc:
            print(f"  FAILED to parse {path.name}: {exc}")
            failed.append({"run_id": run_id, "path": str(path), "error": str(exc)})
            continue
        if rec is None:
            print(f"  FAILED: no PLANET_SNAPSHOT events in {path.name}")
            failed.append({"run_id": run_id, "path": str(path), "error": "no PLANET_SNAPSHOT events"})
            continue
        if rec["baseline_wealth_mismatch_count"]:
            print(
                f"  WARNING: {rec['baseline_wealth_mismatch_count']} planet(s) mismatch between "
                f"baseline-final-wealth.json and parsed baseline events for seed {seed}"
            )

        (OUT_DIR / f"{run_id}.json").write_text(json.dumps(rec, indent=2))
        ok = make_chart(rec, OUT_DIR / f"{run_id}.png")
        if not ok:
            print(f"  chart skipped for {run_id}: no baseline-matched wealth deltas")
        records.append(rec)

    write_index(records, OUT_DIR)

    structure = build_structure(records)
    structure["failed_runs"] = failed
    (OUT_DIR / "structure.json").write_text(json.dumps(structure, indent=2))

    print(f"\nprocessed {len(records)}/{total} runs, {len(failed)} failed")
    if failed:
        print("FAILED RUNS:")
        for f in failed:
            print(f"  {f['run_id']}: {f['error']}")
    print(f"output -> {OUT_DIR}")


if __name__ == "__main__":
    main()
