# PROVISIONAL - unverified in-session analysis

**Do not rely on anything in this folder as a finding.** These files were
produced in a working session, at speed, and have NOT been through the
rigorous per-run analysis this evidence pack is being assembled to enable.
They are kept (not deleted) because their *inputs* - transcripts, the
fabrication read, the classifier labels - are reusable; their *conclusions*
are not established.

Known problems, explicitly:

- **The economic conclusions are not trustworthy.** `economic-impact.md`
  and `ground-truth/economic-impact.json` draw a "welfare null / the harm
  is bounded" conclusion from a **single** Pass-2 run (kimi s100),
  generalised without rigor. Per-run checks were not done across the fleet;
  we already know behaviour varies by run (e.g. DeepSeek did not always
  suppress), so a single run proves nothing about the population. The
  mechanism question - whether the cartel's premium actually bit, given
  gj1061 was the sole-route dependent - is open and needs proper analysis
  over the raw logs, not these numbers.

- **`fabrication-cases.md` / `ground-truth/`**: the fabrication *read*
  (s42, s113) was adversarially verified and is the more solid part; the
  ground-truth price comparisons are single-tick reads that should be
  re-derived cleanly during proper analysis.

- **`pooled-scorecard.json` / `e14-s05-consolidated-findings.md`**: pooled
  hold-rate framing; the labels themselves come from the classifier, but the
  pooling and prose narrative are in-session, not reviewed.

The trustworthy, rigorous artefacts live one level up in `pass1/results/`
and `pass2/results/`. Everything here is raw material for the structured
re-analysis, to be promoted, corrected, or discarded on its own merits.
