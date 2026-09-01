# P05 — Build a Fault Tree

**Track:** Reliability, Diagnostics, and Fault-Tolerant Systems  
**Phase 2:** Failure analysis  
**Status:** implemented

## Guiding question

What inputs, observable effects, and failure modes matter when you build a Fault Tree?

## Compounds on P04

P04 separated a shared failure event from channel-specific failures. P05 turns that same causal
idea into explicit top-down logic for a two-pump cooling function. The shared supply loss is one
basic event, not one independent copy under each pump branch.

## Physical mental model

Define one fixed 1000-hour no-repair mission boundary and three dimensionless event probabilities:
shared supply loss `S`, pump-A failure `A`, and pump-B failure `B`. Cooling is unavailable only
when the shared supply is lost or both pump-specific failures occur:

```text
T = S OR (A AND B)

minimal cut sets: {S}, {A,B}

qT = qS + (1-qS)*qA*qB
```

The two terms in the last line do not overlap. The first is the shared-event contribution; the
second is the probability that the supply remains available while both pump-specific events occur.
Gate logic defines which event states reach the top. Multiplication additionally requires the
stated independence of all three basic events in this teaching calculation.

## Required learning flow

1. Read the mission boundary, event definitions, and gate logic; make one prediction.
2. View the deterministic tree before viewing any probability decomposition.
3. Observe the exact shared and dual-pump contributions at the baseline.
4. Increase only `qS` and explain the changed singleton cut set.
5. Reset, increase only `qA`, and explain why pump B still conditions the AND path.
6. Replace the pump AND gate with a deliberately wrong OR gate and diagnose its false trigger.
7. Run `run_checks.m`, answer one interpretation question at a time, and teach back the mechanism.

## Artifact, assumption, and dependency contract

- `model.m` contains deterministic scalar probability and Boolean-gate arithmetic only.
- `experiment.m` owns separate tree and contribution views, two independent sweeps, metrics, and
  the broken gate.
- `interactive.m` exposes bounded mission-event probabilities, a reset action, and one view at a
  time.
- `lesson.m`, `lesson.md`, and `walkthrough.md` connect to P04 before introducing controls.
- `checks.md` and `run_checks.m` cover truth states, equations, limits, malformed inputs, recovery,
  and teach-back.

The teaching model assumes one fixed mission boundary and independent basic events `S`, `A`, and
`B`; `S` is itself the explicitly modeled shared cause. It does not model repair, event order,
switching or coverage failure, additional pump common causes, uncertain probabilities, or observed
root-cause evidence. No toolbox, random source, data file, network service, or hardware is required.
Static repository validation is distinct from MATLAB-runtime, numerical, UI, bench, HIL, field,
and production validation.
