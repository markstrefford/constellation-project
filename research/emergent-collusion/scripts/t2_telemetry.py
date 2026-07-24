#!/usr/bin/env python3
"""
t2 - the telemetry window (what the hub actually saw).

For every decision tick in the t1 governor trace, reconstructs the telemetry
packet the hub's prompt was built from: its own market/stock/wealth, the
target's ground-truth state (gj1061-hub never appears in a hub's own prompt -
"Not visible from where you stand this tick" is the *permanent* string
regardless of embargo state, confirmed by grepping every run: the embargo
dial controls what COURIERS see, not what the governor's own dashboard
shows), courier flow through the hub and target, the peer hub's last-known
dials, and the recorded inbox (the exact `inbox` field from decisions.json -
already pinned, not reconstructed).

The observation->decision LAG is resolved per decision, not assumed: the
`user_prompt` embeds rounded treasury/stock/price numbers that pin an exact
PLANET_SNAPSHOT tick. For candidate lag in 0..4, score how many of the 7
parsed fields match snapshot[tick-lag] (rounded to display precision) and
take the best-scoring lag (ties -> smaller lag). Confirmed empirically before
writing this script:
  - dsv4pro and gemma431 (both passes): clean, consistent lag=1 (decision
    labeled tick N is built from the tick N-1 snapshot).
  - sonnet5: clean, consistent lag=0.
  - grok420 and kimi: mostly lag=0 but jitters to lag=1 on some ticks (real
    signal, not a parsing artifact - the alternate lag scores much lower,
    e.g. 2/7 vs 7/7).

Source: evidence/{pass1,pass2}/raw-r2/<run>.events.json.gz (telemetry) +
evidence/{pass1,pass2}/decisions/<run>.decisions.json (recorded prompt/inbox,
also the tick x hub spine from t1).

Output: evidence/analysis/e14-s06/t2-telemetry/<run>.json + <run>.md + INDEX.md

Run from repo root: python3 scripts/t2_telemetry.py
"""
import gzip
import json
import re
import time
from collections import defaultdict
from pathlib import Path

EVIDENCE = Path(
    "/Users/mark/Development/constellation-research/research/emergent-collusion/evidence"
)
OUT_DIR = EVIDENCE / "analysis/e14-s06/t2-telemetry"
OUT_DIR.mkdir(parents=True, exist_ok=True)
PASS_DIRS = {"pass1": EVIDENCE / "pass1", "pass2": EVIDENCE / "pass2"}

MEMBER_HUBS = ("sol-hub", "trappist1-hub")
VICTIM_HUB = "gj1061-hub"
WINDOW = 5  # ticks either side of the resolved observed_tick
MAX_LAG = 4


def peer_of(hub):
    return [h for h in MEMBER_HUBS if h != hub][0]


# ---------------------------------------------------------------- parsing --

PROMPT_RE = {
    "treasury": re.compile(r"Treasury:\s*([\d,]+)"),
    "stock": re.compile(
        r"Stock: food (\d+), fuel_raw (\d+), fuel_refined (\d+)"
    ),
    "prices": re.compile(
        r"Your posted prices: food: ([\d.]+), fuel_raw: ([\d.]+), "
        r"fuel_refined: ([\d.]+)"
    ),
}


def parse_prompt_fields(up):
    d = {}
    m = PROMPT_RE["treasury"].search(up)
    if m:
        d["treasury"] = float(m.group(1).replace(",", ""))
    m = PROMPT_RE["stock"].search(up)
    if m:
        d["food_stock"] = float(m.group(1))
        d["fuel_raw_stock"] = float(m.group(2))
        d["fuel_refined_stock"] = float(m.group(3))
    m = PROMPT_RE["prices"].search(up)
    if m:
        d["food_price"] = float(m.group(1))
        d["fuel_raw_price"] = float(m.group(2))
        d["fuel_refined_price"] = float(m.group(3))
    return d


def snap_fields(e):
    return {
        "treasury": e.get("wealth"),
        "food_stock": e["stock"].get("food"),
        "fuel_raw_stock": e["stock"].get("fuel_raw"),
        "fuel_refined_stock": e["stock"].get("fuel_refined"),
        "food_price": e["prices"].get("food"),
        "fuel_raw_price": e["prices"].get("fuel_raw"),
        "fuel_refined_price": e["prices"].get("fuel_refined"),
    }


def field_score(shown, snap):
    ok, tot = 0, 0
    for k, v in shown.items():
        sv = snap.get(k)
        if sv is None:
            continue
        tot += 1
        if k == "treasury" or k.endswith("_stock"):
            if round(sv) == round(v):
                ok += 1
        else:
            if abs(round(sv, 2) - round(v, 2)) < 0.005:
                ok += 1
    return ok, tot


def resolve_lag(shown, snaps_by_tick, tick):
    """Best-fit lag in 0..MAX_LAG for one decision. Returns
    (lag, ok, tot, runner_up_lag, runner_up_ok) - runner-up lets callers flag
    ambiguous fits (best and second-best scoring similarly)."""
    scored = []
    for lag in range(0, MAX_LAG + 1):
        snap = snaps_by_tick.get(tick - lag)
        if snap is None:
            continue
        ok, tot = field_score(shown, snap_fields(snap))
        scored.append((lag, ok, tot))
    if not scored:
        return None, 0, 0, None, 0
    scored.sort(key=lambda x: (-x[1], x[0]))
    best = scored[0]
    runner = scored[1] if len(scored) > 1 else None
    return best[0], best[1], best[2], (runner[0] if runner else None), (
        runner[1] if runner else 0
    )


# ------------------------------------------------------------- event index --

def load_run_index(events_path):
    with gzip.open(events_path) as f:
        data = json.load(f)
    evs = data["events"]

    planet_snap = defaultdict(dict)       # planet -> {tick: event}
    agents_by_tick = defaultdict(list)    # tick -> [agent snapshot events]
    relay_events = defaultdict(list)      # hub_id -> [RELAY_SUPPRESSION events]
    premium_events = defaultdict(list)    # member_id -> [EMBARGO_PREMIUM_SET events]

    for e in evs:
        k = e["kind"]
        if k == "PLANET_SNAPSHOT":
            planet_snap[e["planet"]][e["tick"]] = e
        elif k == "AGENT_SNAPSHOT":
            agents_by_tick[e["tick"]].append(e)
        elif k == "RELAY_SUPPRESSION":
            relay_events[e["hub_id"]].append(e)
        elif k == "EMBARGO_PREMIUM_SET":
            premium_events[e["member_id"]].append(e)

    for d in (relay_events, premium_events):
        for lst in d.values():
            lst.sort(key=lambda e: e["tick"])

    return {
        "planet_snap": planet_snap,
        "agents_by_tick": agents_by_tick,
        "relay_events": relay_events,
        "premium_events": premium_events,
    }


def last_before(events, tick):
    """Most recent event at or before `tick`."""
    out = None
    for e in events:
        if e["tick"] > tick:
            break
        out = e
    return out


def courier_flow_at(idx, tick, hub, target):
    agents = idx["agents_by_tick"].get(tick, [])
    at_hub = at_target = en_route_to_target = en_route_to_hub = 0
    cargo_to_target = 0.0
    for a in agents:
        if not a.get("alive", True):
            continue
        planet = a.get("planet")
        dest = a.get("dest")
        cargo_dest = a.get("cargo_dest")
        if planet == hub:
            at_hub += 1
        if planet == target:
            at_target += 1
        eff_dest = cargo_dest or dest
        if eff_dest == target and planet != target:
            en_route_to_target += 1
            cargo_to_target += sum((a.get("cargo") or {}).values())
        if eff_dest == hub and planet != hub:
            en_route_to_hub += 1
    return {
        "tick": tick,
        "at_hub": at_hub,
        "at_target": at_target,
        "en_route_to_target": en_route_to_target,
        "en_route_to_hub": en_route_to_hub,
        "cargo_units_en_route_to_target": round(cargo_to_target, 1),
    }


def own_window(idx, hub, center):
    snaps = idx["planet_snap"].get(hub, {})
    out = []
    for t in range(center - WINDOW, center + WINDOW + 1):
        e = snaps.get(t)
        if e is None:
            continue
        out.append({
            "tick": t,
            "wealth": round(e.get("wealth", 0), 2),
            "stock": {k: round(v, 1) for k, v in e.get("stock", {}).items()},
            "prices": {k: round(v, 4) for k, v in e.get("prices", {}).items()},
            "health_multiplier": e.get("health_multiplier"),
            "shortage_ticks": e.get("shortage_ticks"),
            "alive": e.get("alive"),
        })
    return out


def target_window(idx, center):
    snaps = idx["planet_snap"].get(VICTIM_HUB, {})
    out = []
    for t in range(center - WINDOW, center + WINDOW + 1):
        e = snaps.get(t)
        if e is None:
            continue
        out.append({
            "tick": t,
            "wealth": round(e.get("wealth", 0), 2),
            "stock": {k: round(v, 1) for k, v in e.get("stock", {}).items()},
            "prices": {k: round(v, 4) for k, v in e.get("prices", {}).items()},
            "health_multiplier": e.get("health_multiplier"),
            "shortage_ticks": e.get("shortage_ticks"),
            "alive": e.get("alive"),
        })
    return out


def peer_dial_state(idx, peer, at_tick):
    r = last_before(idx["relay_events"].get(peer, []), at_tick)
    p = last_before(idx["premium_events"].get(peer, []), at_tick)
    return {
        "suppressing": r.get("suppressing") if r else None,
        "suppressing_as_of_tick": r.get("tick") if r else None,
        "premium": p.get("premium") if p else None,
        "premium_as_of_tick": p.get("tick") if p else None,
    }


# -------------------------------------------------------------- per-record --

def build_packet(idx, rec):
    hub = rec["hub"]
    tick = rec["tick"]
    target = VICTIM_HUB
    peer = peer_of(hub) if hub in MEMBER_HUBS else None

    shown = parse_prompt_fields(rec.get("user_prompt", ""))
    snaps_by_tick = idx["planet_snap"].get(hub, {})
    lag, ok, tot, runner_lag, runner_ok = resolve_lag(shown, snaps_by_tick, tick)

    flags = []
    if lag is None:
        flags.append("no_snapshot_in_lag_window")
        observed_tick = None
    else:
        observed_tick = tick - lag
        if tot == 0:
            flags.append("no_parsed_fields")
        elif ok < tot:
            flags.append(f"partial_field_match_{ok}_of_{tot}")
        if runner_lag is not None and runner_ok >= ok - 1 and runner_lag != lag:
            flags.append(f"ambiguous_lag_runner_up={runner_lag}({runner_ok}/{tot})")
        if lag >= 2:
            flags.append("stale_observation_lag_ge_2")

    center = observed_tick if observed_tick is not None else tick

    packet = {
        "tick": tick,
        "hub": hub,
        "resolved_lag": lag,
        "observed_tick": observed_tick,
        "lag_fit": f"{ok}/{tot}" if tot else None,
        "own_window": own_window(idx, hub, center),
        "target_window": target_window(idx, center),
        "target_visible_to_hub": False,  # structural: never shown in user_prompt
        "courier_flow": courier_flow_at(idx, center, hub, target) if center is not None else None,
        "peer_hub": peer,
        "peer_dials_as_of_decision": peer_dial_state(idx, peer, tick) if peer else None,
        "inbox": rec.get("inbox", []),
        "flags": flags,
    }
    return packet


# ------------------------------------------------------------------- runs --

def list_runs():
    runs = []  # (phase, run_id, decisions_path, events_path)
    for phase, pdir in PASS_DIRS.items():
        for dp in sorted((pdir / "decisions").glob("*.decisions.json")):
            run_id = dp.name.replace(".decisions.json", "")
            ep = pdir / "raw-r2" / f"{run_id}.events.json.gz"
            runs.append((phase, run_id, dp, ep))
    return runs


def build_run(phase, run_id, dp, ep):
    recs = json.loads(dp.read_text())
    recs.sort(key=lambda r: (r["tick"], r["hub"]))
    idx = load_run_index(ep)

    packets = [build_packet(idx, r) for r in recs]

    (OUT_DIR / f"{run_id}.json").write_text(json.dumps(packets, indent=1))

    hubs = sorted(set(p["hub"] for p in packets))
    lag_by_hub = {}
    for h in hubs:
        lags = [p["resolved_lag"] for p in packets if p["hub"] == h and p["resolved_lag"] is not None]
        dist = defaultdict(int)
        for l in lags:
            dist[l] += 1
        lag_by_hub[h] = dict(sorted(dist.items()))

    gaps = sum(1 for p in packets if p["flags"] and any(
        f.startswith("no_snapshot") or f.startswith("no_parsed") for f in p["flags"]
    ))
    ambiguous = sum(1 for p in packets if any(f.startswith("ambiguous_lag") for f in p["flags"]))
    clean = len(packets) - gaps - ambiguous

    hdr = [
        f"# t2 telemetry window - {run_id}",
        "",
        f"decisions: {len(packets)} | clean_windows: {clean} | "
        f"ambiguous_lag: {ambiguous} | gaps: {gaps}",
        f"lag distribution per hub: {lag_by_hub}",
        "",
        "| tick | hub | lag | observed_tick | fit | own(treasury/food) | "
        "target(wealth/food_stock/food_price) | courier(hub/target/->target) | "
        "peer dials | flags |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    rows = []
    for p in packets:
        own = next((w for w in p["own_window"] if w["tick"] == p["observed_tick"]), None)
        own_s = f"{own['wealth']:.0f}/{own['stock'].get('food','-')}" if own else "-"
        tgt = next((w for w in p["target_window"] if w["tick"] == p["observed_tick"]), None)
        tgt_s = (
            f"{tgt['wealth']:.0f}/{tgt['stock'].get('food','-')}/"
            f"{tgt['prices'].get('food','-')}"
        ) if tgt else "-"
        cf = p["courier_flow"] or {}
        cf_s = f"{cf.get('at_hub','-')}/{cf.get('at_target','-')}/{cf.get('en_route_to_target','-')}"
        pd = p["peer_dials_as_of_decision"] or {}
        pd_s = f"s={pd.get('suppressing')},p={pd.get('premium')}"
        flags_s = ";".join(p["flags"]) or "-"
        rows.append(
            f"| {p['tick']} | {p['hub']} | {p['resolved_lag']} | "
            f"{p['observed_tick']} | {p['lag_fit']} | {own_s} | {tgt_s} | "
            f"{cf_s} | {pd_s} | {flags_s} |"
        )
    (OUT_DIR / f"{run_id}.md").write_text("\n".join(hdr + rows))

    return {
        "run_id": run_id,
        "phase": phase,
        "n_decisions": len(packets),
        "clean": clean,
        "ambiguous": ambiguous,
        "gaps": gaps,
        "lag_by_hub": lag_by_hub,
    }


def main():
    runs = list_runs()
    idx_rows = [
        "# t2 telemetry-window index",
        "",
        "| run | phase | decisions | clean | ambiguous_lag | gaps | lag/hub |",
        "|---|---|---|---|---|---|---|",
    ]
    t0 = time.time()
    failed = []
    for i, (phase, run_id, dp, ep) in enumerate(runs, 1):
        if not ep.exists():
            print(f"[t2] {i:2}/{len(runs)} {run_id:16} SKIP (no events file: {ep})", flush=True)
            failed.append((run_id, "missing events file"))
            continue
        try:
            summary = build_run(phase, run_id, dp, ep)
        except Exception as exc:  # noqa: BLE001 - report and continue over 50 runs
            print(f"[t2] {i:2}/{len(runs)} {run_id:16} FAILED: {exc}", flush=True)
            failed.append((run_id, str(exc)))
            continue
        idx_rows.append(
            f"| {summary['run_id']} | {summary['phase']} | {summary['n_decisions']} | "
            f"{summary['clean']} | {summary['ambiguous']} | {summary['gaps']} | "
            f"{summary['lag_by_hub']} |"
        )
        print(
            f"[t2] {i:2}/{len(runs)} {run_id:16} decisions={summary['n_decisions']:3} "
            f"clean={summary['clean']:3} ambiguous={summary['ambiguous']:2} "
            f"gaps={summary['gaps']:2} ({time.time()-t0:.0f}s)",
            flush=True,
        )
    if failed:
        idx_rows += ["", "## failed / skipped", ""]
        idx_rows += [f"- {run}: {msg}" for run, msg in failed]
    (OUT_DIR / "INDEX.md").write_text("\n".join(idx_rows))
    print(f"[t2] done -> {OUT_DIR} ({len(runs)} runs, {len(failed)} failed)", flush=True)


if __name__ == "__main__":
    main()
