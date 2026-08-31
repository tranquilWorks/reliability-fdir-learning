# P04 — Expose Common-Cause Failure

**Track:** Reliability, Diagnostics, and Fault-Tolerant Systems  
**Phase 1:** Reliability fundamentals  
**Status:** implemented

## Guiding question

What inputs, observable effects, and failure modes matter when you expose Common-Cause Failure?

## Compounds on P03

P03 distinguished failure rate from repairable point availability. P04 keeps that rate discipline
but deliberately studies a nonrepairable mission so dependence is the only new mechanism. The
observable is mission reliability for a one-out-of-`n` redundant group, not P03 availability.

## Physical mental model

Each identical channel has constant marginal failure hazard `lambda` in failures/hour. A simple
beta-factor teaching model allocates a dimensionless fraction `beta` of that hazard to one shared
event that defeats every channel, leaving the rest as an independent failure mode on each channel:

```text
lambda_c = beta*lambda
lambda_i = (1-beta)*lambda

R_system(t) = exp(-lambda_c*t) *
              [1 - (1-exp(-lambda_i*t))^n]

Q_common(t)      = 1-exp(-lambda_c*t)
Q_independent(t) = exp(-lambda_c*t) * (1-exp(-lambda_i*t))^n
Q_system(t)      = Q_common(t) + Q_independent(t)
```

The failure terms are mutually exclusive mission states: either the shared event has occurred, or
no shared event occurred and all independent channel modes failed. At fixed mission time, extra
channels shrink only the second term. They cannot shrink the shared-event contribution.

## Required learning flow

1. Read the hazard split and make one prediction before plotting.
2. Run the deterministic reliability baseline and compare the correct and independent claims.
3. Advance once to the complementary failure-mode decomposition.
4. Move only `beta` and explain why joint reliability changes while marginal channel reliability
   does not.
5. Reset, move only channel count, and observe diminishing benefit toward the shared contribution.
6. Run the deliberately broken six-channel independence calculation and diagnose its optimism.
7. Run `run_checks.m`, answer the interpretation prompts, and give a two-sentence teach-back.

## Artifact, assumption, and dependency contract

- `model.m` contains deterministic bounded base-MATLAB arithmetic without presentation code.
- `experiment.m` owns five one-at-a-time plot transitions, metrics, two independent sweeps, and
  the broken case.
- `interactive.m` exposes bounded channel hazard, beta, channel count, and mission-duration controls
  with a selector that shows one complementary view at a time.
- `lesson.m`, `lesson.md`, and `walkthrough.md` connect explicitly to P03 before controls or syntax.
- `checks.md` and `run_checks.m` cover equations, limits, malformed inputs, recovery, and teach-back.

The model assumes identical constant channel hazards, one-out-of-`n` success, no repair, perfect
coverage, and one shared event that defeats all channels. It does not model partial-subset common
causes, repair, switching failure, uncertainty in beta, or observed field data. No toolbox, data
file, random source, network service, or hardware is required. Static repository validation is
retained separately from MATLAB-runtime, numerical, UI, bench, HIL, and field validation.
