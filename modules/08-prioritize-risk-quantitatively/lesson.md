# P08 lesson: Prioritize Risk Quantitatively

## Guiding question

What inputs, observable effects, and failure modes matter when you prioritize Risk Quantitatively?

## Start from P07's outcomes, not from a priority formula

P06 separated item function, failure mode, effect, observable evidence, occurrence, and conditional
detection coverage. P07 then asked which combinations actually change the cooling mission. With one
shared supply and two alternative pumps, success is `S works AND (A works OR B works)` over the
fixed 1000-hour, no-repair mission; its failure complement is P05's `S OR (A AND B)` fault tree.

P08 does not rank the three basic events directly. A Pump-A failure has a different consequence
when Pump B works than when Pump B also fails. Instead, preserve P07's five mutually exclusive
outcomes:

```text
S fails                                      0.00500
S works; A and B fail                        0.00995
S and A work; B fails                        0.08955
S and B work; A fails                        0.08955
S, A, and B work                             0.80595
```

The first four are loss-bearing scenarios, not four mission failures. Shared-supply failure and
supply-up dual-pump failure are the two P07 mission-failure outcomes, totaling `0.01495`. Either
single-pump failure is degraded mission success because the companion pump still carries the load;
those two outcomes plus all-parts-working total the P07 system reliability `0.98505`. The fifth
outcome closes the probability ledger to one. This boundary prevents double counting: supply
failure and any supply-up pump outcome cannot happen in the same mission state.

## Put consequence in a common ratio-scale unit

A prioritization input needs more than an ordered label. This lesson uses synthetic economic
consequences `[120,100,8,12]` kUSD per scenario occurrence in P07 order
`[S, A&B, B only, A only]`. The large-event values include recovery and mission impact; the
single-pump values represent repair and degraded-operation cost while the companion pump carries
the load. These are teaching estimates, not observed costs.

For disjoint scenario `i`:

```text
E[loss_i] = P(scenario_i) × C_i
```

The units remain visible:

```text
(occurrences/mission) × (kUSD/occurrence) = kUSD/mission.
```

At baseline:

| Scenario | Probability/mission | Consequence (kUSD/occurrence) | Expected loss (kUSD/mission) | Rank |
| --- | ---: | ---: | ---: | ---: |
| S | `0.00500` | `120` | `0.6000` | 4 |
| A&B | `0.00995` | `100` | `0.9950` | 2 |
| B only | `0.08955` | `8` | `0.7164` | 3 |
| A only | `0.08955` | `12` | `1.0746` | 1 |

The total is `3.3860` kUSD per mission. A-only ranks first: its per-occurrence consequence is much
smaller than shared-supply loss, but its occurrence probability is sufficiently larger. That does
not turn A-only into a mission failure; it is a frequent degraded-success cost. “Most frequent” and
“most severe” are observations; neither is the complete priority.

## Observe one probability lever at a time

Make one prediction before the baseline: must the rarest, most expensive scenario rank first?
Inspect the probability ledger, then the probability-consequence plane, then the expected-loss
bars.

Sweep only shared-supply failure probability through `[0,0.005,0.01,0.02,0.05]`; keep
`q_A=q_B=0.10` and all consequences fixed. Total expected loss becomes
`[2.800,3.386,3.972,5.144,8.660]` kUSD per mission.

The S contribution rises with slope `120`. The A&B, B-only, and A-only contributions fall slightly
because all three require the supply to work. This is not a beneficial effect of supply failure;
it is probability moving between mutually exclusive outcome states. S and A-only tie at
`q_S=1.08/(120+1.08)=0.0089197`; `q_S=0.01` is the first sampled point after that crossover, where
S becomes first priority even though its consequence did not change.

## Reset, then observe one consequence lever

Reset `q=[0.005,0.10,0.10]`. Sweep only A&B consequence through `[0,25,50,100,200]` kUSD per
occurrence. The A&B probability remains exactly `0.00995`, so its expected loss becomes
`[0,0.24875,0.49750,0.99500,1.99000]` kUSD per mission. Every other scenario probability,
consequence, and expected loss stays fixed.

At `100` kUSD, A&B ranks second. It ties A-only at exactly `108` kUSD and moves ahead above that
point. This crossover is auditable because the axes retain physical decision units.

## Deliberately broken case: multiply ordinal ratings

Suppose a workshop assigns occurrence categories `[2,2,5,5]` and severity categories
`[5,5,2,2]`. Multiplication produces `[10,10,10,10]` and calls the products quantitative priority
scores.

The symptom is a four-way tie even though common-unit expected loss ranges from `0.6000` to
`1.0746` kUSD per mission. Ordered categories say that 5 is above 2; they do not say the step from
1 to 2 equals the step from 4 to 5, or that category 4 is twice category 2. The product therefore
has no ratio-scale unit, cannot be added to an expected-loss total, and cannot defend a tie break.

Ordinal categories can remain useful screening labels when their limits are explicit. The broken
move is treating their product as probability, consequence, expected loss, or precise distance
between priorities.

## Observable effects and controls still matter

P06 observables help estimate whether a mode occurred and whether evidence is missing. Detection
coverage by itself does not reduce the P07 physical scenario probabilities. A justified detection,
switching, repair, or recovery action could change probability or consequence, but that mechanism
and its evidence must be modeled explicitly rather than credited inside a score.

Expected economic loss is also not a waiver for a safety constraint. A low-frequency catastrophic
hazard may require treatment regardless of its position in this economic ranking. Keep safety
acceptance, compliance, and non-compensable harms as explicit decision constraints.

## Common misconceptions to correct directly

- Rank disjoint scenarios or use a model that accounts for overlap; do not add overlapping event
  probabilities or expected losses twice.
- Do not equate a priced component-failure outcome with mission failure. Here the first two ledger
  states fail the mission; the two single-pump states succeed in degraded operation.
- Probability must use a stated mission boundary, and consequence values must share a defensible
  unit and scope.
- A high consequence does not automatically mean highest expected loss; probability also matters.
- A high occurrence probability does not automatically mean highest expected loss; consequence
  also matters.
- Better detection evidence is not physical prevention unless a response path is modeled.
- Multiplying ordinal category numbers does not make them ratio-scale measurements.
- A precise computed rank can still be fragile when its input estimates are uncertain or close.
- An economic ranking does not override safety, legal, or design constraints.

## Completion standard

The learner can derive the four failure-scenario probabilities from P07, state the common units,
reproduce each expected-loss contribution and rank, explain both isolated lever mechanisms,
diagnose the ordinal-product tie, pass `run_checks.m`, and give a two-sentence mechanism-first
teach-back without relying on MATLAB syntax.
