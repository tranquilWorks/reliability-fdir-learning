# P04 lesson: Expose Common-Cause Failure

## Guiding question

What inputs, observable effects, and failure modes matter when you expose Common-Cause Failure?

## Start from P03, not from syntax

P03 used failure and repair rates to compute whether one repairable item was up at a point in time.
P04 asks a different question: will at least one channel in a redundant group survive a no-repair
mission? Holding repair outside the model makes dependence visible. The result is mission
reliability, not availability.

P01 gave the qualitative warning that a shared cause defeats redundancy. P04 now gives that
warning time, rate, units, a probability decomposition, and limiting cases. Each channel retains
the same marginal hazard so a comparison cannot explain the system gap by quietly making an
individual channel worse.

## Mental model

Take `n` identical channels where any one surviving channel can perform the required function.
Each channel has total marginal hazard `lambda` in failures/hour. The dimensionless beta factor
allocates that rate between one all-channel shared shock and a channel-specific mode:

```text
shared rate:       lambda_c = beta*lambda
independent rate:  lambda_i = (1-beta)*lambda
```

For a mission time `t` in hours, the group works only if no shared event occurs and at least one
independent channel mode survives:

```text
R_system(t) = exp(-lambda_c*t) *
              [1 - (1-exp(-lambda_i*t))^n].
```

It is often clearer to inspect failure probability directly. These mission states do not overlap:

```text
Q_common(t)      = 1-exp(-lambda_c*t)
Q_independent(t) = exp(-lambda_c*t) * (1-exp(-lambda_i*t))^n
Q_system(t)      = Q_common(t) + Q_independent(t).
```

`Q_common` means a shared event occurred by `t`. `Q_independent` means no shared event occurred,
but all channel-specific modes failed. This is a partition of endpoint mission states, not a claim
about which event occurred first on every failed mission.

## Observe one transition at a time

Make one prediction about replacing two channels with six while beta remains positive. Then run
only the baseline reliability section. The correct and assumed-independent curves use the same
single-channel marginal reliability `exp(-lambda*t)`; their separation therefore exposes
dependence rather than component quality.

Advance once to the failure-mode view. The two component curves add to system failure probability.
First increase only beta. The shared rate rises while the independent rate falls, but their sum—and
therefore marginal channel reliability—stays fixed. Joint redundant reliability falls because a
larger part of the hazard now defeats every channel together.

Reset. Next increase only channel count. The no-shared-event/all-independent term shrinks quickly,
while the shared-event contribution is unchanged at that fixed mission time. This is a
channel-count limit, not a positive time-asymptote: with finite channels and no repair, reliability
still tends to zero over an indefinitely long mission.

## Deliberately broken case

The broken calculation raises marginal channel failure probability to the sixth power as if all
six outcomes were independent. At the baseline exposure, that produces mission failure probability
below `1e-6`; the correct model remains above `0.004` because the shared event is not replicated six
times. The orders-of-magnitude optimism is the recognizable symptom that dependence was omitted.

## Common misconceptions to correct directly

- Beta is the fraction of each channel's marginal hazard allocated to the modeled shared event. It
  is not a correlation coefficient and is not automatically the observed fraction of system
  failures.
- More channels still help when beta is positive; they help only the independent-exhaustion term.
- Equal marginal channel reliability does not establish independent joint behavior.
- The simple all-channel beta model does not represent partial-subset causes, switching coverage,
  repair, design diversity, uncertain rates, or measured field performance.
- The model is nonrepairable mission reliability. P03 point availability needs explicit repair
  transitions and answers a different question.

## Completion standard

The learner can name both hazard parts and their units, use the failure decomposition to explain
both lever sweeps, distinguish marginal from joint reliability, diagnose the broken independence
claim, pass `run_checks.m`, and give a two-sentence mechanism-first teach-back.
