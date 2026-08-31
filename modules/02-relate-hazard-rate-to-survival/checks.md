# P02 checks: Relate Hazard Rate to Survival

## Observation questions

Answer one at a time after observing the relevant plot.

1. Why do the post-change sweep curves overlap before 1000 h?
2. Which has units `1/hour`: hazard, cumulative hazard, or survival?
3. Why may cumulative hazard exceed one while survival may not?
4. What constant-hazard result from P01 appears when the multiplier is one?

## Limiting cases

- With zero baseline hazard, explain why `H(t)=0` and `S(t)=1` for the whole mission.
- With a zero post-change multiplier, explain why survival becomes a plateau after the change.
- With multiplier one, independently calculate `S(T)=exp(-lambda*T)` and compare it with the model.

## Broken-case diagnosis

Name the violated assumption precisely: `1-H` is only a small-cumulative-hazard approximation to
`exp(-H)`. A negative claimed survival is the recognizable symptom that it was extended beyond its
valid range.

## Executable checks

In MATLAB, run:

```matlab
run_checks
```

The checks cover determinism, probability bounds, monotonicity, `-log(S)=H`, the P01 constant-hazard
limit, independent pre/post exposure, zero-hazard limits, the broken case, malformed inputs, and the
10,000-sample resource bound.

## Teach-back gate

In two sentences, answer the guiding question. Sentence one must connect hazard rate, cumulative
hazard, and survival with units. Sentence two must explain the negative-probability broken-case
symptom without referring to MATLAB syntax.

Passing static repository tests does not mean these executable checks or the UI ran in MATLAB.
