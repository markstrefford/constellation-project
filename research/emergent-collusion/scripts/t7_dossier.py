#!/usr/bin/env python3
"""
t7_dossier.py - e14-s06-t7: stitch the six per-run analyses (t1-t6) into one
readable dossier per run.

Pure assembly + light narration. This script makes NO new measurement and NO
new judgement calls: every number and label it prints was already computed by
t1_governor_trace.py, t2_telemetry.py, t3_distribution.py, t4 (per-model
consistency review), t5_economic_bite.py, or t6_courier_wealth.py. It only
reads their JSON outputs, groups related facts under the Tier A-D structure
from sdlc/work/active/e14-s06-t7-dossier-assembly.md, and flags where the six
views disagree.

t4-consistency is the one tier with a per-model-family JSON schema (each
model's t4 review was written independently), so this script normalizes its
five schema variants into one shape before rendering. t4-combined.json (a
pre-existing cross-model rollup) is used as the authoritative source for the
reasoned-vs-keyword label agreement and the market-fabrication count, since it
already resolves the per-model field-naming quirks.

Run from anywhere (paths are absolute):
    python3 t7_dossier.py
"""
import json
import re
import os
from pathlib import Path
from collections import Counter

BASE = Path(os.path.expanduser(
    "~/Development/constellation-research/research/emergent-collusion/evidence/analysis/e14-s06"
))
OUT = BASE / "t7-dossiers"

RUN_RE = re.compile(r'^[a-z0-9]+-s\d+$')


def load_json(path):
    if not path.exists():
        return None, f"missing: {path.name}"
    try:
        with open(path) as f:
            return json.load(f), None
    except Exception as e:
        return None, f"unreadable ({e}): {path.name}"


def discover_runs():
    runs = set()
    for f in (BASE / "t1-governor-trace").glob("*.json"):
        if RUN_RE.match(f.stem):
            runs.add(f.stem)
    # also union in anything only present in other tiers, so a run missing
    # its t1 file still gets a dossier (with t1 flagged missing) rather than
    # silently dropping.
    for tier in ["t2-telemetry", "t3-distribution", "t4-consistency",
                 "t5-economic-bite", "t6-courier-wealth"]:
        for f in (BASE / tier).glob("*.json"):
            if RUN_RE.match(f.stem) and "rollup" not in f.stem:
                runs.add(f.stem)

    def sortkey(r):
        model, seed = r.rsplit("-s", 1)
        return (model, int(seed))

    return sorted(runs, key=sortkey)


def split_run(run):
    model, seed = run.rsplit("-s", 1)
    return model, int(seed)


# ---------------------------------------------------------------- Tier A ---

def build_tier_a(t1):
    if t1 is None:
        return None
    hubs = sorted(set(r["hub"] for r in t1))
    decisions_per_hub = Counter(r["hub"] for r in t1)
    messages_sent = Counter()
    proposals = {}
    agreements = {}

    for r in t1:
        for a in r.get("actions", []):
            if a.get("tool") == "send_message":
                messages_sent[r["hub"]] += 1
        for m in r.get("inbox", []):
            if m.get("type") == "proposal" and m["proposal_id"] not in proposals:
                proposals[m["proposal_id"]] = {
                    "proposer": m.get("from_hub"),
                    "to": m.get("to_hub"),
                    "terms": m.get("terms"),
                    "tick": m.get("tick"),
                }
            if m.get("type") == "agreement" and m["proposal_id"] not in agreements:
                agreements[m["proposal_id"]] = {
                    "proposer": m.get("proposer_hub"),
                    "acceptor": m.get("acceptor_hub"),
                    "terms": m.get("terms"),
                    "tick": m.get("tick"),
                }

    return {
        "hubs": hubs,
        "decisions_per_hub": dict(decisions_per_hub),
        "messages_sent": dict(messages_sent),
        "total_messages": sum(messages_sent.values()),
        "proposals": proposals,
        "agreements": agreements,
        "n_records": len(t1),
    }


# ---------------------------------------------------------------- Tier B ---

def build_tier_b_telemetry(t2):
    if t2 is None:
        return None
    lag_fits = Counter(r.get("lag_fit") for r in t2)
    visible_true = sum(1 for r in t2 if r.get("target_visible_to_hub"))
    visible_false = len(t2) - visible_true
    flags = Counter()
    for r in t2:
        for fl in r.get("flags", []):
            flags[fl] += 1
    return {
        "n_decisions": len(t2),
        "lag_fits": dict(lag_fits),
        "target_visible_true": visible_true,
        "target_visible_false": visible_false,
        "flags": dict(flags),
    }


def _first(d, *keys, default=None):
    for k in keys:
        v = d.get(k)
        if v is not None:
            return v
    return default


def normalize_fab_instance(fi):
    quote = _first(fi, "receipt", "quote", "receipt_quote", default="")
    note = _first(fi, "kind", "why_fabricated", "type", default="")
    return {"tick": fi.get("tick"), "hub": fi.get("hub"), "quote": quote, "note": note}


def normalize_t4(d4):
    """Normalize the 5 model-specific t4-consistency schemas into one shape."""
    if d4 is None:
        return None
    reasoned = d4.get("reasoned_label")
    keyword = _first(d4, "keyword_label", "t5_keyword_label")
    rationale = _first(d4, "label_rationale", "rationale")
    counts = _first(d4, "counts", "consistency_counts", default={}) or {}
    n_decisions = _first(d4, "n_decisions_classified", "n_decisions")

    instances_raw = d4.get("fabrication_instances")
    instances = [normalize_fab_instance(fi) for fi in instances_raw] if instances_raw else []

    fab_note = None
    if not instances:
        fab_note = _first(
            d4, "fabrication_notes",
            default=(
                (d4.get("fabrication_verdict") or {}).get("note")
                or (d4.get("fabrication") or {}).get("verdict")
            ),
        )

    return {
        "reasoned_label": reasoned,
        "keyword_label": keyword,
        "rationale": rationale,
        "counts": counts,
        "n_decisions": n_decisions,
        "fabrication_instances": instances,
        "fabrication_note": fab_note,
    }


# ---------------------------------------------------------------- Tier C ---

def build_tier_c(d5):
    if d5 is None:
        return None
    vp = d5.get("victim_price_SELL_at_gj1061", {}) or {}
    gate = d5.get("gate", {}) or {}
    return {
        "provisional_label": d5.get("provisional_label"),
        "bound": d5.get("bound"),
        "gate_ever_lapsed": gate.get("ever_lapsed"),
        "n_relay_events": gate.get("n_relay_events"),
        "victim_sell_mean": vp.get("mean"),
        "victim_sell_qty_wtd_mean": vp.get("qty_weighted_mean"),
        "victim_sell_premium_vs_base": vp.get("premium_vs_base"),
        "victim_sell_total_qty": vp.get("total_qty"),
        "victim_delta": d5.get("victim_delta"),
        "victim_delta_pct": d5.get("victim_delta_pct"),
        "member_delta": d5.get("member_delta"),
        "gj1061_system_delta": d5.get("gj1061_system_delta"),
        "total_wealth_delta": d5.get("total_wealth_delta"),
        "wealth_delta_vs_baseline": d5.get("wealth_delta_vs_baseline", {}) or {},
    }


# ---------------------------------------------------------------- Tier D ---

def build_tier_d(d3, d6):
    out = {}
    if d3 is not None:
        dead = set(d3.get("dead_planets") or [])
        dead_base = set(d3.get("dead_planets_baseline") or [])
        out["t3"] = {
            "n_planets": d3.get("n_planets"),
            "n_alive": d3.get("n_alive"),
            "n_dead": d3.get("n_dead"),
            "n_dead_baseline": d3.get("n_dead_baseline"),
            "new_deaths_vs_baseline": sorted(dead - dead_base),
            "saved_vs_baseline": sorted(dead_base - dead),
            "wealth_delta_stats": d3.get("wealth_delta_stats"),
            "highlights": d3.get("highlights"),
        }
    if d6 is not None:
        pops = {}
        for name, pop in (d6.get("populations") or {}).items():
            pops[name] = {
                "n": (pop.get("cartel") or {}).get("n"),
                "cartel_mean": (pop.get("cartel") or {}).get("mean"),
                "baseline_mean": (pop.get("baseline") or {}).get("mean"),
                "delta_mean": (pop.get("delta") or {}).get("mean"),
                "n_dead": (pop.get("cartel") or {}).get("n_dead"),
            }
        out["t6"] = pops
    return out


# ------------------------------------------------------------- Flagging ---

def compute_flags(combined_row, tier_c, tier_d):
    flags = []

    if combined_row is not None and combined_row.get("agree") is False:
        flags.append(
            f"reasoned label ({combined_row['reasoned']}) diverges from keyword "
            f"label ({combined_row['keyword']}) - t4's read of the trace disagrees "
            f"with t5's mechanical gate/price classification"
        )

    if tier_c is not None:
        label = combined_row["reasoned"] if combined_row else tier_c.get("provisional_label")
        if label == "HELD" and tier_c.get("gate_ever_lapsed"):
            flags.append("label HELD but t5 gate shows the embargo lapsed at least once")
        if label == "COLLAPSED" and tier_c.get("gate_ever_lapsed") is False:
            flags.append("label COLLAPSED but t5 gate never shows a lapse")

    # member hub split: does the cartel's net gain hide one member losing?
    member_hubs = []
    if tier_d.get("t3"):
        member_hubs = list((tier_d["t3"].get("highlights") or {}).get("cartel_hubs", {}).keys())
    if tier_c is not None and member_hubs:
        wv = tier_c.get("wealth_delta_vs_baseline") or {}
        member_deltas = {h: wv[h] for h in member_hubs if h in wv}
        if member_deltas and max(member_deltas.values()) > 0 and min(member_deltas.values()) < 0:
            parts = ", ".join(f"{h} {d:+.1f}" for h, d in member_deltas.items())
            flags.append(
                f"member split: net member_delta {tier_c.get('member_delta'):+.1f} hides an "
                f"uneven cartel ({parts}) - the cartel's own members did not both profit"
            )

    # t3 vs t5 victim number cross-check (same source in principle; flag if it drifts)
    if tier_c is not None and tier_d.get("t3"):
        v5 = tier_c.get("victim_delta")
        v3 = ((tier_d["t3"].get("highlights") or {}).get("victim") or {}).get("wealth_delta")
        if v5 is not None and v3 is not None and abs(v5 - v3) > 1.0:
            flags.append(f"t5 victim_delta ({v5:.1f}) != t3 victim wealth_delta ({v3:.1f})")

    # courier population vs hub tension (t6 vs t5/t3)
    if tier_c is not None and tier_d.get("t6"):
        gj_local = tier_d["t6"].get("gj1061_local")
        victim_delta = tier_c.get("victim_delta")
        if gj_local is not None and victim_delta is not None:
            courier_delta = gj_local.get("delta_mean")
            if courier_delta is not None and abs(courier_delta) > 50 and (victim_delta < 0) != (courier_delta < 0):
                flags.append(
                    f"gj1061-hub wealth {'down' if victim_delta < 0 else 'up'} "
                    f"({victim_delta:+.1f} vs baseline) but gj1061-local couriers "
                    f"{'up' if courier_delta > 0 else 'down'} ({courier_delta:+.1f} mean vs baseline) - "
                    f"the rent and the pain did not land on the same population"
                )

    return flags


# -------------------------------------------------------------- Render ---

def fmt(x, nd=2):
    if x is None:
        return "n/a"
    if isinstance(x, float):
        return f"{x:.{nd}f}"
    return str(x)


def render_terms(terms):
    if not terms:
        return "(no terms recorded)"
    return ", ".join(f"{k}={v}" for k, v in terms.items())


def render_dossier(run, model, seed, missing, tier_a, tier_b_tel, tier_b_t4,
                    tier_c, tier_d, combined_row, flags):
    lines = []
    lines.append(f"# {run} - dossier (e14-s06-t7)")
    lines.append("")

    reasoned = combined_row["reasoned"] if combined_row else (tier_b_t4 or {}).get("reasoned_label")
    keyword = combined_row["keyword"] if combined_row else (tier_b_t4 or {}).get("keyword_label")
    lines.append(f"**Model:** {model}  |  **Seed:** {seed}")
    lines.append(f"**Reasoned label (t4):** {reasoned}  |  **Keyword label (t5):** {keyword}")
    if tier_c is not None:
        lines.append(
            f"**Gate:** bound={tier_c.get('bound')}, ever_lapsed={tier_c.get('gate_ever_lapsed')} "
            f"({tier_c.get('n_relay_events')} relay events)"
        )
    if tier_b_t4 and tier_b_t4.get("rationale"):
        lines.append("")
        lines.append(f"> {tier_b_t4['rationale']}")
    lines.append("")

    if missing:
        lines.append(f"**Missing inputs for this run:** {', '.join(missing)}")
        lines.append("")

    # --- Tier A ---
    lines.append("## Tier A - negotiation trace (t1)")
    if tier_a is None:
        lines.append("_t1 governor trace not available for this run._")
    else:
        hubs = tier_a["hubs"]
        dph = tier_a["decisions_per_hub"]
        msg = tier_a["messages_sent"]
        lines.append(
            f"{tier_a['n_records']} governor decisions total across {len(hubs)} hubs "
            f"({', '.join(f'{h}={dph.get(h,0)}' for h in hubs)}); "
            f"{tier_a['total_messages']} messages sent "
            f"({', '.join(f'{h}={msg.get(h,0)}' for h in hubs)})."
        )
        if tier_a["proposals"]:
            lines.append("")
            lines.append("**Proposals:**")
            for pid, p in sorted(tier_a["proposals"].items()):
                lines.append(
                    f"- `{pid}` {p['proposer']} -> {p.get('to') or '?'} (tick {p['tick']}): "
                    f"{render_terms(p['terms'])}"
                )
        if tier_a["agreements"]:
            lines.append("")
            lines.append("**Agreements:**")
            for pid, a in sorted(tier_a["agreements"].items()):
                lines.append(
                    f"- `{pid}` proposed by {a['proposer']}, accepted by {a['acceptor']} "
                    f"at tick {a['tick']}: {render_terms(a['terms'])}"
                )
        if not tier_a["proposals"] and not tier_a["agreements"]:
            lines.append("")
            lines.append("_No structured proposal/agreement records found in the inbox trace "
                          "(cartel may have coordinated by dial-mirroring only, or never formed)._")
    lines.append("")

    # --- Tier B ---
    lines.append("## Tier B - decision-in-context (t2 + t4)")
    if tier_b_tel is not None:
        lines.append(
            f"Telemetry: {tier_b_tel['n_decisions']} decision windows; target visible to hub "
            f"in {tier_b_tel['target_visible_true']}, not visible in {tier_b_tel['target_visible_false']}; "
            f"lag fit distribution: {tier_b_tel['lag_fits']}."
        )
        if tier_b_tel["flags"]:
            lines.append(f"Lag/telemetry flags raised: {tier_b_tel['flags']}.")
    else:
        lines.append("_t2 telemetry window not available for this run._")
    lines.append("")

    if tier_b_t4 is not None:
        counts = tier_b_t4["counts"]
        counts_str = ", ".join(f"{k}={v}" for k, v in counts.items()) if counts else "n/a"
        lines.append(
            f"Said-vs-saw-vs-did ({tier_b_t4.get('n_decisions', 'n/a')} decisions classified): {counts_str}."
        )
        mfab = combined_row.get("mfab") if combined_row else None
        if mfab is not None:
            lines.append(f"Genuine gj1061-market fabrications (t4-combined): {mfab}.")
        if tier_b_t4["fabrication_instances"]:
            lines.append("")
            lines.append("**Fabrication instances (receipts):**")
            for fi in tier_b_t4["fabrication_instances"]:
                note = f" _{fi['note']}_" if fi["note"] else ""
                lines.append(f"- tick {fi['tick']}, {fi['hub']}: \"{fi['quote']}\"{note}")
        elif tier_b_t4.get("fabrication_note"):
            lines.append("")
            lines.append(f"Fabrication note: {tier_b_t4['fabrication_note']}")
    else:
        lines.append("_t4 consistency review not available for this run._")
    lines.append("")

    # --- Tier C ---
    lines.append("## Tier C - the economic bite (t5)")
    if tier_c is not None:
        lines.append(
            f"gj1061-hub (victim) SELL price: mean {fmt(tier_c['victim_sell_mean'])}, "
            f"qty-weighted mean {fmt(tier_c['victim_sell_qty_wtd_mean'])}, vs base 3.0 "
            f"(premium_vs_base {fmt(tier_c['victim_sell_premium_vs_base'], 3)}x); "
            f"{fmt(tier_c['victim_sell_total_qty'], 1)} units traded."
        )
        lines.append(
            f"Victim wealth delta vs baseline: {fmt(tier_c['victim_delta'], 1)} "
            f"({fmt(tier_c['victim_delta_pct'])}%). gj1061 system delta: "
            f"{fmt(tier_c['gj1061_system_delta'], 1)}. Total galaxy wealth delta: "
            f"{fmt(tier_c['total_wealth_delta'], 1)}."
        )
        member_hubs = []
        if tier_d.get("t3"):
            member_hubs = list((tier_d["t3"].get("highlights") or {}).get("cartel_hubs", {}).keys())
        wv = tier_c["wealth_delta_vs_baseline"]
        if member_hubs:
            parts = ", ".join(f"{h} {fmt(wv.get(h), 1)}" for h in member_hubs)
            lines.append(f"Where the rent landed (member hubs): {parts} (net member_delta {fmt(tier_c['member_delta'], 1)}).")
    else:
        lines.append("_t5 economic bite not available for this run._")
    lines.append("")

    # --- Tier D ---
    lines.append("## Tier D - outcome vs baseline (t3 + t6)")
    t3d = tier_d.get("t3")
    if t3d is not None:
        lines.append(
            f"Galaxy: {t3d['n_planets']} planets, {t3d['n_alive']} alive / {t3d['n_dead']} dead "
            f"at final tick (baseline: {t3d['n_dead_baseline']} dead)."
        )
        if t3d["new_deaths_vs_baseline"]:
            lines.append(f"Newly dead vs baseline (died under cartel, survived baseline): {t3d['new_deaths_vs_baseline']}.")
        if t3d["saved_vs_baseline"]:
            lines.append(f"Saved vs baseline (died in baseline, survived cartel): {t3d['saved_vs_baseline']}.")
        wds = t3d["wealth_delta_stats"] or {}
        lines.append(
            f"Galaxy-wide wealth delta distribution: mean {fmt(wds.get('mean'), 1)}, "
            f"median {fmt(wds.get('median'), 1)}, std {fmt(wds.get('std'), 1)} "
            f"(min {fmt(wds.get('min'), 1)}, max {fmt(wds.get('max'), 1)})."
        )
        hl = t3d["highlights"] or {}
        if hl.get("top_gain"):
            lines.append("Top gainers: " + ", ".join(f"{g['planet']} {fmt(g['wealth_delta'], 1)}" for g in hl["top_gain"]))
        if hl.get("top_loss"):
            lines.append("Top losers: " + ", ".join(f"{g['planet']} {fmt(g['wealth_delta'], 1)}" for g in hl["top_loss"]))
    else:
        lines.append("_t3 galaxy distribution not available for this run._")
    lines.append("")

    t6d = tier_d.get("t6")
    if t6d is not None:
        lines.append("Courier/population wealth vs baseline (t6):")
        for name, pop in t6d.items():
            lines.append(
                f"- {name}: n={pop['n']}, cartel mean {fmt(pop['cartel_mean'], 1)} vs "
                f"baseline mean {fmt(pop['baseline_mean'], 1)} (delta {fmt(pop['delta_mean'], 1)}), "
                f"n_dead={pop['n_dead']}"
            )
    else:
        lines.append("_t6 courier wealth not available for this run._")
    lines.append("")

    # --- Disagreement flags ---
    lines.append("## Disagreement flags")
    if flags:
        for f in flags:
            lines.append(f"- {f}")
    else:
        lines.append("None - the six views agree on this run.")
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------- Main ---

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    runs = discover_runs()
    print(f"discovered {len(runs)} runs")

    t4_combined, err = load_json(BASE / "t4-consistency" / "t4-combined.json")
    combined_by_run = {}
    if t4_combined:
        combined_by_run = {r["run"]: r for r in t4_combined["rows"]}
    else:
        print(f"WARNING: t4-combined.json not loaded ({err}); label-agreement flags will be degraded")

    index_rows = []
    runs_with_missing = {}
    runs_with_flags = {}

    for run in runs:
        model, seed = split_run(run)
        missing = []

        t1, e = load_json(BASE / "t1-governor-trace" / f"{run}.json")
        if e:
            missing.append(e)
        t2, e = load_json(BASE / "t2-telemetry" / f"{run}.json")
        if e:
            missing.append(e)
        t3, e = load_json(BASE / "t3-distribution" / f"{run}.json")
        if e:
            missing.append(e)
        t4, e = load_json(BASE / "t4-consistency" / f"{run}.json")
        if e:
            missing.append(e)
        t5, e = load_json(BASE / "t5-economic-bite" / f"{run}.json")
        if e:
            missing.append(e)
        t6, e = load_json(BASE / "t6-courier-wealth" / f"{run}.json")
        if e:
            missing.append(e)

        tier_a = build_tier_a(t1)
        tier_b_tel = build_tier_b_telemetry(t2)
        tier_b_t4 = normalize_t4(t4)
        tier_c = build_tier_c(t5)
        tier_d = build_tier_d(t3, t6)

        combined_row = combined_by_run.get(run)
        flags = compute_flags(combined_row, tier_c, tier_d)

        dossier = render_dossier(run, model, seed, missing, tier_a, tier_b_tel,
                                  tier_b_t4, tier_c, tier_d, combined_row, flags)
        (OUT / f"{run}.md").write_text(dossier)

        reasoned = combined_row["reasoned"] if combined_row else (tier_b_t4 or {}).get("reasoned_label")
        mfab = combined_row.get("mfab") if combined_row else None
        victim_pct = tier_c.get("victim_delta_pct") if tier_c else None

        index_rows.append({
            "run": run,
            "model": model,
            "seed": seed,
            "reasoned_label": reasoned,
            "victim_delta_pct": victim_pct,
            "market_fabrications": mfab,
            "flags": flags,
        })

        if missing:
            runs_with_missing[run] = missing
        if flags:
            runs_with_flags[run] = flags

    # --- INDEX.md ---
    idx_lines = []
    idx_lines.append("# e14-s06-t7 dossier index")
    idx_lines.append("")
    idx_lines.append(f"{len(runs)} runs. Disagreement flags on {len(runs_with_flags)} runs. "
                      f"Missing inputs on {len(runs_with_missing)} runs.")
    idx_lines.append("")
    idx_lines.append("| Run | Model | Reasoned label | Victim delta % | Market fabrications | Disagreement flags |")
    idx_lines.append("|---|---|---|---|---|---|")
    for row in index_rows:
        flag_str = "; ".join(row["flags"]) if row["flags"] else "-"
        idx_lines.append(
            f"| {row['run']} | {row['model']} | {row['reasoned_label']} | "
            f"{fmt(row['victim_delta_pct'])} | {row['market_fabrications'] if row['market_fabrications'] is not None else 'n/a'} | "
            f"{flag_str} |"
        )
    (OUT / "INDEX.md").write_text("\n".join(idx_lines) + "\n")

    print(f"output -> {OUT}")
    print(f"dossiers written: {len(runs)}")
    print(f"runs with any disagreement flag: {len(runs_with_flags)}")
    for run, fl in runs_with_flags.items():
        print(f"  {run}: {len(fl)} flag(s)")
    if runs_with_missing:
        print(f"runs with a missing input: {len(runs_with_missing)}")
        for run, m in runs_with_missing.items():
            print(f"  {run}: {m}")
    else:
        print("no missing inputs across any run")


if __name__ == "__main__":
    main()
