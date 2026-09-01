# P07 — Construct a Reliability Block Diagram

**Track:** Reliability, Diagnostics, and Fault-Tolerant Systems  
**Phase 2:** Failure analysis  
**Status:** implemented

## Guiding question

What inputs, observable effects, and failure modes matter when you construct a Reliability Block Diagram?

## Compounds on P06

P06 described a fixed 1000-hour, no-repair cooling mission bottom-up. Its three FMEA rows are shared
supply output absent (`S`), Pump A no flow (`A`), and Pump B no flow (`B`). P07 turns each failure
statement around into a success block and asks which functions the mission requires:

```text
source → [shared supply works] → ┬→ [Pump A works] →┬→ cooling succeeds
                                 └→ [Pump B works] →┘
```

The functional rule is `S works AND (A works OR B works)`. The one shared supply is in series because
every success path needs it. The pumps are parallel because either pump can carry the cooling load
when its companion fails. P06's observable effects and detection coverage can help locate evidence,
but observation does not change physical success unless a detection-and-recovery action is modeled.

## Physical mental model

An RBD is a map of required success, not a drawing of wires, fluid lines, or component proximity.
First define the mission boundary and success criterion. Next give each distinct required function one
block, connect blocks in series for `AND`, and branch in parallel for genuine alternatives. Only then
attach block reliabilities measured over the same mission and state the dependency assumptions used
to combine them.

For the synthetic P06 inputs, `q=[0.005,0.10,0.10]` and `R=1-q` give
`R_S=0.995`, `R_A=0.90`, and `R_B=0.90`. Assuming the three block-success events are independent:

```text
R_pumps  = R_A + (1-R_A)R_B
R_system = R_S R_pumps                  = 0.98505
Q_system = (1-R_S) + R_S(1-R_A)(1-R_B) = 0.01495
```

The failure result is exactly P05's top-event probability; the success and failure models are
complements under the same boundary and assumptions. The two minimal success paths, `S-A` and `S-B`,
share `S` and overlap when all three blocks work. Their probabilities cannot be blindly added or
combined as independent path events.

## Required learning flow

1. Translate P06's failure modes into required-function success statements and make one prediction.
2. Construct the deterministic baseline topology before reading any aggregate metric.
3. Inspect the disjoint outcome ledger and verify success plus failure closes to one.
4. Sweep shared-supply reliability while both pump blocks remain fixed.
5. Reset, then sweep Pump-A reliability while the supply and Pump B remain fixed.
6. Duplicate the one physical supply inside both branches and diagnose the optimistic symptom.
7. Run `run_checks.m`, answer one interpretation question at a time, and teach back the mechanism.

## Artifact, assumption, and dependency contract

- `model.m` contains fixed-size, deterministic success, failure, path-overlap, and outcome arithmetic.
- `experiment.m` owns the correct topology, outcome ledger, two independent sweeps, metrics, and the
  deliberately duplicated-supply case.
- `interactive.m` exposes bounded block-reliability controls, reset, and one visible view at a time.
- `lesson.m`, `lesson.md`, and `walkthrough.md` connect P06's bottom-up rows to functional topology
  before introducing controls.
- `checks.md` and `run_checks.m` cover topology identity, equations, limits, malformed inputs,
  recovery, interpretation, and teach-back.

The block probabilities are synthetic fixed-mission inputs, not field estimates. The model excludes
repair, standby switching, load sharing, capacity margins, time-varying hazards, uncertain estimates,
and dependencies beyond the named shared topology. Quantification assumes independent `S`, `A`, and
`B` events; P04 explains why an unmodeled common cause can invalidate that assumption. No toolbox,
random source, data file, network service, or hardware is required. Static repository validation is
distinct from MATLAB-runtime, numerical, rendered-UI, bench, HIL, field, and production validation.
