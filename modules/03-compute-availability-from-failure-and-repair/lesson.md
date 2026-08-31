# P03 lesson: Compute Availability from Failure and Repair

## Guiding question

What inputs, observable effects, and failure modes matter when you compute Availability from Failure and Repair?

## Start from P02, not from syntax

P02's `exp(-lambda*t)` was nonrepairable survival: the probability that no first failure had
occurred. Availability asks a different question: is the item up now? A repairable item may fail,
return to service, and be available even though its first-failure reliability is already low.

## Mental model

Represent one repairable item with an up state and a down state. Constant failure rate `lambda`
moves probability from up to down. Mean time to repair `MTTR` implies constant repair rate
`mu=1/MTTR`, which moves probability back from down to up:

```text
dA/dt = repair flow - failure flow
      = mu*(1-A) - lambda*A,
A_inf = mu/(lambda+mu) = 1/(1+lambda*MTTR),
A(t) = A_inf + (A(0)-A_inf)*exp(-(lambda+mu)*t).
```

Rates have units `1/hour`, MTTR and time have units hours, and availability is dimensionless.
At steady state, `lambda*A_inf = mu*(1-A_inf)`: equal probability flows do not mean nothing fails;
they mean repair replenishes the up state at the same average rate that failure drains it.

This is inherent availability under exponential up and repair durations, immediate repair
coverage, and no logistics or preventive-maintenance downtime. The curve is a deterministic state
probability, not a randomly sampled sequence of outages. `8760*(1-A_inf)` converts steady
unavailability into expected downtime hours per 8760-hour year under those same assumptions.

## Observe one transition at a time

Before the baseline, make one prediction about a fourfold increase in MTTR. Then run only the
state-baseline section of `experiment.m` and pause on `A(t)` and `1-A(t)`. Advance once to the
separate flow section; it shows why the initially up item moves toward equilibrium. In
`interactive.m`, the visible-view selector preserves this one-transition-at-a-time pacing.

First increase only `lambda`. Failure flow grows, lowering the balance availability. Reset. Next
increase only MTTR. That lowers `mu`, so probability spends longer down and expected annual
downtime rises. The initial up/down choice changes how the curve approaches equilibrium but cannot
change `A_inf`, because the rates determine the long-run balance.

## Deliberately broken case

The broken calculation labels P02's `exp(-lambda*t)` as repairable availability. That expression
counts only items with no first failure, so it has no path from down back to up. Over a long horizon
it decays toward zero even while the repairable model approaches a positive availability. The
large divergence is the recognizable symptom that repair was omitted, not a plotting or rounding
error.

## Common misconceptions to correct directly

- Availability is not reliability. Reliability excludes every item after its first failure;
  point availability includes repaired items that are currently up.
- `lambda` and `mu` are rates in `1/hour`; MTTR is a duration in hours.
- High availability can coexist with frequent failures if repair is extremely fast. That does not
  make the failures harmless or the first-failure reliability high.
- The formula does not include logistics delay, repair coverage, preventive maintenance, multiple
  repair crews, or non-exponential durations unless those mechanisms are modeled explicitly.

## Completion standard

The learner can name both levers and units, use the competing flows to explain each visible change,
distinguish availability from P02 survival, pass `run_checks.m`, and give a two-sentence
mechanism-first teach-back.
