# P02 lesson: Relate Hazard Rate to Survival

## Guiding question

What inputs, observable effects, and failure modes matter when you relate Hazard Rate to Survival?

## Start from P01, not from syntax

P01 plotted `exp(-lambda*t)` as component reliability. That curve assumed the component's
conditional failure rate stayed constant. Here the rate itself becomes visible, so a changing
environment or operating condition can change later survival without changing earlier history.

## Mental model

For a nonrepairable population with a known shared exposure history, hazard `lambda(t)` answers a
conditional question: among the items still alive at time `t`, how
quickly are failures occurring per hour? It is not the fraction that has already failed. The area
under that rate is cumulative hazard,

```text
H(t) = integral from 0 to t of lambda(u) du,
S(t) = exp(-H(t)).
```

`H(t)` is dimensionless; `S(t)` is a probability. Nonnegative hazard makes `H(t)` nondecreasing and
survival nonincreasing. A step in hazard changes the survival slope
`dS/dt = -lambda(t)*S(t)` but does not make survival jump. Repair and unmodeled population
heterogeneity are outside this lesson's deterministic boundary.

## Observe one transition at a time

Before the baseline, ask one prediction: if hazard rises only after 1000 h, can survival before
1000 h change? Then run only the baseline section of `experiment.m`.

First move the baseline hazard-rate lever. A larger rate makes cumulative hazard grow faster from
the start, so survival falls sooner. Reset. Next move only the post-change multiplier. All curves
must agree before the condition-change time because they have accumulated identical exposure.

## Deliberately broken case

For very small cumulative hazard, `exp(-H)` is close to `1-H`. Treating that local approximation as
a survival law is the named broken assumption. Once `H > 1`, it claims negative survival. The
symptom is not a rounding problem: a probability below zero proves the approximation was used
outside its valid small-exposure range. At `H=0.01` the approximation is close, so the lesson is
about respecting its domain of validity, not rejecting local approximations altogether.

## Common misconceptions to correct directly

- Hazard is a conditional rate with units `1/hour`; it is not a probability.
- Cumulative hazard is not capped at one. Survival is capped because the exponential maps any
  nonnegative cumulative hazard into `[0,1]`.
- A later hazard change cannot alter the survival history before the change.
- Constant hazard is an assumption, not a universal property of hardware.

## Completion standard

The learner can name both levers and their units, use `H(t)` to explain each visible transition,
diagnose the broken approximation from its negative-probability symptom, pass `run_checks.m`, and
give a two-sentence mechanism-first teach-back.
