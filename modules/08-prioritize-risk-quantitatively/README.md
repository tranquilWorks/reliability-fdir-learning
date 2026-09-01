# P08 — Prioritize Risk Quantitatively

**Track:** Reliability, Diagnostics, and Fault-Tolerant Systems  
**Phase 2:** Failure analysis  
**Status:** implemented

## Guiding question

What inputs, observable effects, and failure modes matter when you prioritize Risk Quantitatively?

## Compounds on P07

P06 named the shared-supply (`S`), Pump-A (`A`), and Pump-B (`B`) modes, traced their effects, and
kept occurrence separate from detection coverage. P07 turned those modes into the fixed
1000-hour, no-repair success rule `S works AND (A works OR B works)`. Under its explicit
independent-basic-event assumption, P07's disjoint outcome ledger is the success-side complement of
P05's fault-tree logic:

| P07 outcome | Mission disposition | Probability |
| --- | --- | ---: |
| shared supply fails | failure | `0.00500` |
| supply works; both pumps fail | failure | `0.00995` |
| supply and Pump A work; Pump B fails | degraded success | `0.08955` |
| supply and Pump B work; Pump A fails | degraded success | `0.08955` |
| supply and both pumps work | full success | `0.80595` |

P08 keeps those probabilities instead of inventing a separate scoring model. It assigns the first
four loss-bearing scenarios synthetic consequences in one comparable unit and asks which scenario
makes the largest expected contribution. Only the first two are mission failures; the two
single-pump outcomes retain P07 mission success while carrying repair and degraded-operation cost.

## Quantitative mental model

For mutually exclusive scenario `i`, use a ratio-scale occurrence probability and a consequence in
kUSD per occurrence:

```text
risk contribution_i = P(scenario_i) × consequence_i
                    = expected kUSD per fixed mission.
```

The baseline consequences `[120,100,8,12]` kUSD per occurrence correspond to P07 order
`[S, A&B, B only, A only]`. Expected losses are `[0.6000,0.9950,0.7164,1.0746]` kUSD per mission,
so the priority order is A-only, A&B, B-only, then S. The result illustrates why occurrence alone
and consequence alone are both incomplete.

The four scenarios are disjoint, so their contributions add to `3.3860` kUSD per mission without
double counting. That economic total is conditional on the boundary, probabilities, consequence
estimates, and independence assumption. It does not make a safety requirement tradeable, prove
input quality, or represent field evidence.

## Required learning flow

1. Recall P06's mode/effect distinction and P07's disjoint outcome ledger.
2. Make one prediction, then inspect the deterministic probability baseline.
3. View probability and consequence separately before viewing their expected-loss product.
4. Sweep only shared-supply failure probability and observe the outcome reallocation.
5. Reset, then sweep only dual-pump consequence and verify all probabilities stay fixed.
6. Multiply ordinal occurrence and severity categories, observe the false four-way tie, and name
   why category products have no ratio-scale unit.
7. Run `run_checks.m`, answer one interpretation question at a time, and teach back the mechanism.

## Artifact, assumption, and dependency contract

- `model.m` owns fixed-size outcome, mission-success/failure, expected-loss, share, sensitivity,
  deterministic-rank, and broken ordinal-product arithmetic.
- `experiment.m` owns the probability ledger, probability-consequence plane, expected-loss view,
  two independent sweeps, metrics, and deliberately broken case.
- `interactive.m` exposes bounded `q_S`, `q_A`, and `q_B` controls, four common-unit consequences,
  reset, and one visible view at a time.
- `lesson.m`, `lesson.md`, and `walkthrough.md` connect P06 and P07 before introducing a score or
  MATLAB control.
- `checks.md` and `run_checks.m` cover equations, scenario isolation, ranks, limits, malformed
  inputs, recovery, applicability, and teach-back.

The inputs are synthetic teaching values, not estimates from field data, a hazard analysis, or a
financial forecast. The model excludes uncertainty distributions, correlated basic events beyond
the named assumption, repair, event order, risk appetite, safety constraints, detection-triggered
recovery, and mitigation cost/benefit. P06 detection coverage remains evidence about occurrence
unless an explicit response mechanism is modeled. No toolbox, random source, data file, network
service, or hardware is required. Static repository validation is distinct from MATLAB-runtime,
numerical-fidelity, rendered-UI, bench, HIL, field, and production validation.
