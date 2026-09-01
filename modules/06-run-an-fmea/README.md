# P06 — Run an FMEA

**Track:** Reliability, Diagnostics, and Fault-Tolerant Systems  
**Phase 2:** Failure analysis  
**Status:** implemented

## Guiding question

What inputs, observable effects, and failure modes matter when you run an FMEA?

## Compounds on P05

P05 built a fault tree top-down from loss of cooling: `T = S OR (A AND B)`. P06 keeps the same
fixed 1000-hour, no-repair two-pump boundary and turns the analysis around. It follows the shared
supply mode `S`, Pump-A mode `A`, and Pump-B mode `B` bottom-up from item function through local,
next-higher, and end effects. Each effect column uses the row-under-analysis premise: only that mode
is present and companion items are available. Under that premise, a single pump mode degrades
redundancy; it does not by itself become P05's cooling-loss top event.

## Physical mental model

An FMEA row is a causal sentence, not just a score:

```text
item / required function
    → failure mode (how the function fails)
    → local effect → next-higher effect → end effect
    → observable effect and current controls
```

For each row, `q` is a synthetic dimensionless occurrence probability over the fixed mission and
`c` is conditional detection coverage:

```text
c = P(indicator annunciates | mode occurs)
detected occurrence = q*c
latent occurrence   = q*(1-c)
detected + latent   = q
```

This multiplication is the conditional-probability chain rule, not an independence assumption.
Failure-mode rows can co-occur, so sums across rows are expected mode-occurrence counts per mission,
not union probabilities. Row co-occurrence does not change a row's single-mode effect text; return to
P05's combination logic to determine a combined event's end effect. Consequence classes remain
categorical in P06; multiplying ordinal labels into a risk-priority number would displace the P08
quantitative-prioritization lesson.

## Required learning flow

1. Read how the bottom-up FMEA complements P05's top-down fault tree and make one prediction.
2. Inspect the deterministic worksheet before viewing its occurrence partition.
3. Observe the baseline detected and latent values for all three rows.
4. Increase only Pump-A occurrence probability and explain why both partitions scale.
5. Reset, increase only Pump-A detection coverage, and explain why occurrence does not move.
6. Break the analysis by treating even oracle-filtered true-positive detector records as a complete
   failure-mode inventory.
7. Run `run_checks.m`, answer one interpretation question at a time, and teach back the mechanism.

## Artifact, assumption, and dependency contract

- `model.m` contains fixed-size row metadata and transparent conditional-probability arithmetic.
- `experiment.m` owns the worksheet, occurrence view, two independent sweeps, metrics, and broken
  detected-only inventory.
- `interactive.m` exposes bounded occurrence and coverage controls, reset, row selection, and one
  view at a time.
- `lesson.m`, `lesson.md`, and `walkthrough.md` connect to P05 before introducing controls.
- `checks.md` and `run_checks.m` cover row completeness, equations, limits, malformed inputs,
  recovery, and teach-back.

The three-row worksheet is a deliberately bounded teaching slice, not an exhaustive design FMEA.
Its probabilities and coverages are synthetic reference inputs, not measured rates or qualified
detector performance. It does not model repair, event order, uncertain estimates, combined top-event
logic, priority scoring, false alarms, ambiguous indicator attribution, or observed root-cause proof.
The broken comparison grants each detected occurrence one uniquely attributed true-positive record
with perfect specificity; raw logs can also overcount or misattribute modes. No toolbox, random
source, data file, network service, or hardware is required. Static repository validation is
distinct from MATLAB-runtime, numerical, UI, bench, HIL, field, and production validation.
