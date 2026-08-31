# P03 — Compute Availability from Failure and Repair

**Track:** Reliability, Diagnostics, and Fault-Tolerant Systems  
**Phase 1:** Reliability fundamentals  
**Status:** implemented

## Guiding question

What inputs, observable effects, and failure modes matter when you compute Availability from Failure and Repair?

## Compounds on P02

P02 followed a nonrepairable population from hazard rate `lambda` to survival: once an item failed,
it never returned. P03 keeps that constant failure rate and adds repair. The new observable is the
probability that a repairable item is up now, even if it failed earlier.

## Physical mental model

The model has two states, up and down. While up, the item fails at constant rate `lambda` in
failures/hour. While down, its constant repair rate is `mu = 1/MTTR` in repairs/hour. Probability
flows between the states according to

```text
dA/dt = mu*(1-A) - lambda*A
A_inf = mu/(lambda+mu) = 1/(1+lambda*MTTR)
A(t) = A_inf + (A(0)-A_inf)*exp(-(lambda+mu)*t)
```

`A(t)` is point availability and `1-A(t)` is point unavailability. The model assumes exponential
up and repair durations, immediate repair coverage, one repairable item, and no logistics delay,
preventive maintenance, or hidden states. Its deterministic state probabilities describe an
ensemble or repeated operation; they are not a sampled outage history.

## Required learning flow

1. Read the two-state mechanism and make one prediction.
2. Run the deterministic state baseline and read availability and downtime metrics.
3. Advance once to the complementary transition-flow view and explain the baseline mechanism.
4. Move only the failure-rate lever and observe the changed availability curve.
5. Reset, move only mean repair time, and observe expected downtime per year.
6. Explain both changes through probability flow before discussing MATLAB mechanics.
7. Run the deliberately broken case that labels P02 survival as repairable availability.
8. Run `run_checks.m`, answer the interpretation checks, and give a two-sentence teach-back.

## Artifact and dependency contract

- `model.m` contains deterministic, bounded base-MATLAB calculations without presentation code.
- `experiment.m` owns the baseline, labeled plots and metrics, two independent sweeps, and broken case.
- `interactive.m` exposes failure rate, mean repair time, horizon, and initial state as controls,
  with a selector that presents one complementary view at a time.
- `lesson.m`, `lesson.md`, and `walkthrough.md` keep the sequence concept-first and connect to P02.
- `checks.md` and `run_checks.m` cover equations, limits, malformed inputs, and teach-back.

No toolbox, data file, random source, network service, or hardware is required. Static repository
validation is retained separately from MATLAB-runtime, numerical, and UI validation.
