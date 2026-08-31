# P02 — Relate Hazard Rate to Survival

**Track:** Reliability, Diagnostics, and Fault-Tolerant Systems  
**Phase 1:** Reliability fundamentals  
**Status:** implemented

## Guiding question

What inputs, observable effects, and failure modes matter when you relate Hazard Rate to Survival?

## Compounds on P01

P01 used component reliability `exp(-lambda*t)` while comparing series and redundant structures. P02
opens that expression: constant `lambda` was a hazard rate, `lambda*t` was cumulative hazard, and
the exponential converted accumulated exposure into survival.

## Physical mental model

Hazard rate `lambda(t)` is the conditional failure rate among items that have survived to time `t`;
its units are failures per hour. Accumulating that rate gives dimensionless cumulative hazard
`H(t)`. Survival follows

```text
H(t) = integral from 0 to t of lambda(u) du
S(t) = exp(-H(t))
```

The model uses a transparent piecewise-constant hazard history for a nonrepairable population whose
members share a known deterministic exposure. It does not model repair or hidden population
heterogeneity. One control sets the baseline rate. A second multiplies the rate after a named
operating-condition change. This makes both the input history and the resulting survival curve
visible without a toolbox. Hazard can jump at the change, but cumulative hazard and survival remain
continuous; only their slopes change.

## Required learning flow

1. Read the mechanism and make one prediction.
2. Run the deterministic constant-hazard baseline and read its labeled metrics.
3. Move only the baseline hazard-rate lever and observe the changed survival curve.
4. Reset, move only the post-change multiplier, and locate where the curves first diverge.
5. Explain the change through cumulative hazard before discussing MATLAB mechanics.
6. Run the deliberately broken `S = 1-H` approximation and diagnose its negative probability.
7. Run `run_checks.m`, answer the interpretation checks, and give a two-sentence teach-back.

## Artifact and dependency contract

- `model.m` contains deterministic base-MATLAB calculations and bounded input validation.
- `experiment.m` owns the baseline, labeled plots and metrics, two independent sweeps, and broken case.
- `interactive.m` exposes hazard rate, multiplier, change time, and mission duration as meaningful controls.
- `lesson.m`, `lesson.md`, and `walkthrough.md` keep the sequence concept-first.
- `checks.md` and `run_checks.m` cover numerical invariants, limiting cases, malformed inputs, and teach-back.

No toolbox, data file, random source, network service, or hardware is required. Static repository
validation is retained separately from MATLAB-runtime and UI validation.
