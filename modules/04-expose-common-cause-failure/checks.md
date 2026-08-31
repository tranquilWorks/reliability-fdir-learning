# P04 checks: Expose Common-Cause Failure

## Observation questions

Answer one at a time after observing the relevant view.

1. Why can two channels keep the same marginal `exp(-lambda*t)` reliability while their joint
   system reliability changes with `beta`?
2. Which failure term can added channels reduce, and which term stays unchanged at fixed mission
   time?
3. Why is `beta` a fraction of marginal channel hazard rather than a correlation coefficient?
4. Why is this nonrepairable mission reliability not the point availability studied in P03?

## Limiting cases

- With zero hazard, independently show why reliability remains one for every beta and channel count.
- With `beta=0`, recover ordinary independent one-out-of-`n` redundancy.
- With `beta=1`, show why every channel count reduces to `exp(-lambda*t)`.
- With one channel, show why the hazard split recombines to `exp(-lambda*t)` for every beta.
- At one fixed mission time, explain why increasing channel count approaches the shared-event
  contribution. Do not call that a positive long-time reliability floor: finite-channel
  nonrepairable reliability still approaches zero as time grows.

## Broken-case diagnosis

Name the violated assumption precisely: multiplying marginal channel failure probabilities assumes
independent outcomes, but the beta model allocates some marginal hazard to one event shared by all
channels. In the six-channel case, an independence calculation below `1e-6` while correct mission
failure probability remains above `0.004` is the recognizable symptom, not a rounding effect.

## Executable checks

In MATLAB, run:

```matlab
run_checks
```

The checks cover determinism, probability bounds and complement, the mutually exclusive
decomposition, independent reference equations, both lever directions, marginal-hazard
preservation, beta-zero and beta-one limits, the one-channel limit, zero and tiny exposure,
equal-exposure compatibility, extreme finite-domain behavior, the broken optimism factor,
malformed inputs, post-rejection recovery, and channel/sample resource bounds.

## Teach-back gate

In two sentences, answer the guiding question. Sentence one must connect `lambda`, dimensionless
`beta`, channel count, and mission time to the two failure terms, with units. Sentence two must
identify exactly why assuming independence can hide common-cause risk, without referring to MATLAB
syntax.

Passing static repository tests does not mean these executable checks or the UI ran in MATLAB.
