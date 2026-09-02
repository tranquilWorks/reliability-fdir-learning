# P10 checks: Move a Fault Threshold

## Observation questions

Answer one at a time after observing the relevant view.

1. Which P09 sign convention and unit determine where P10 must place the threshold?
2. Why does increasing nonnegative `T` move the signed boundary farther below zero?
3. Which physical signal changes when only `T` moves? Which decision output changes?
4. Why can raising `T` reduce healthy nuisance alarms and increase missed fault samples?
5. Which quantities stay fixed during the threshold sweep? Which stay fixed during the conditional
   loss sweep?
6. Why are the two 60-sample alarm fractions not field false-alarm and detection probabilities?
7. What does monotonic nesting of the threshold alarm sets prove about the static comparator?
8. Why can a valid threshold not repair P09 predictor mismatch, omitted inputs, or a sign error?
9. What exact assumption does the `r<=+T` broken case violate, and what symptom reveals it?
10. Why is a threshold decision neither unique fault isolation, posterior inference, nor recovery?

## Independent arithmetic and limiting cases

- Reproduce the 301 samples from 0 to 30 seconds at 0.1-second spacing. Confirm command `0.5` before
  10 seconds and `0.8` afterward, with conditional loss inactive before 20 seconds.
- Reproduce `r=-10 L f(t)u(t)+0.1 sin(2 pi 0.5 t) L/min` from P09's sign convention. Confirm the
  healthy high-command mean is zero and the baseline 20% post-fault mean is `-1.6 L/min`.
- Confirm the 12–18 and 22–28 second reference windows contain 60 samples and exactly three ripple
  cycles each. Their baseline ranges are `[-0.1,+0.1]` and `[-1.7,-1.5] L/min`.
- Apply the inclusive rule `r<=-T`. At `T=0.50 L/min`, confirm TN/FP=`60/0`,
  detected/missed=`60/0`, false-alarm fraction `0`, and detection fraction `1`.
- Sweep only `T=[0.06,0.12,0.50,1.49,1.56,1.72] L/min`. Confirm healthy false-alarm fractions
  `[0.25,0,0,0,0,0]`, fault detection fractions `[1,1,1,1,0.65,0]`, identical residuals, and
  monotonically shrinking alarm sets.
- Reset `T=0.50 L/min`; sweep only `L=[0,0.04,0.06,0.08,0.20]`. Confirm post-fault means
  `[0,-0.32,-0.48,-0.64,-1.6] L/min`, detection fractions `[0,0,0.45,1,1]`, identical pre-fault
  residuals, and monotonically growing fault-window alarm sets.
- As an independent regression for the interactive nuisance control, hold `T=0.55 L/min` and
  `L=0.20`, then use ripple amplitudes `[0,0.40,0.60,0.70,1.00] L/min`. Confirm healthy
  false-alarm counts `[0,0,9,15,21]` of 60, fault detection counts `[60,60,60,60,60]`, fixed
  command/fault/threshold histories, exact ripple-plus-fault residuals, and monotonically growing
  healthy-window alarm sets.
- With zero ripple, `L=0.20`, and `T=1.60 L/min`, confirm every fault-window sample exactly on the
  inclusive boundary alarms. With zero loss at `T=0.50`, confirm no fault-window sample alarms.
- With full loss, zero ripple, and `T=0.50`, confirm post-fault residual is `-8 L/min` and every
  fault-window sample alarms. With `T=10`, full loss, and maximum ripple, confirm all fixed-size
  outputs stay finite and no fault-window sample reaches the boundary.

## Broken-case diagnosis

At the baseline, compare the correct boundary `-0.5 L/min` with the broken `+0.5 L/min` boundary
while keeping the `<=` direction. Confirm the healthy false-alarm fraction changes from `0` to `1`.

Name the violated assumption precisely: the signed threshold boundary must preserve P09's
`r=y-y_hat` convention, under which loss is negative. The recognizable symptom is an alarm asserted
throughout ordinary healthy ripple. Restore `r<=-T` or use the equivalent `-r>=T`; do not disguise a
sign defect by tuning the magnitude.

## Executable checks and applicability

In MATLAB, run:

```matlab
run_checks
```

The executable checks cover positive deterministic behavior, independent residual and decision
equations, sign/unit identity, exact window counts, confusion-count closure, both exact sweeps,
pointwise comparator behavior, monotonic alarm-set nesting, the interactive ripple-control
regression, zero/full-loss and inclusive-boundary limits, the negative wrong-sign case, scalar
shape, range, NaN, Inf, and complex malformed inputs, and exact recovery after rejected calls.

The model has three bounded scalar inputs, 301 fixed samples, no input-size-dependent loop, no file
or network operation, and no asynchronous task. A dedicated model timeout is not applicable;
shared learner CLI subprocess tests retain a ten-second timeout. Cancellation is not applicable
because there is no timer, job, request lifecycle, blocking prompt, or partial write.
Static scans cover the fixed resource bound, base-MATLAB compatibility path, and absence of opaque
toolbox calls. Isolation checks prove the threshold sweep preserves the residual and the loss sweep
preserves threshold plus all pre-fault residuals. The ripple-control regression separately proves
that nuisance amplitude leaves command, fault signature, and threshold fixed while its alarm counts
close against the pointwise comparator. Recovery recomputes the exact baseline after malformed
calls. Rollback is file-based, requires no migration or persistent module state, is documented in
retained P10 evidence, and was not executed.

## Teach-back gate

In two sentences, answer the guiding question. Sentence one must connect P09's command-conditioned
negative residual and `L/min` unit to the inclusive `r<=-T` decision and explain the baseline
counts. Sentence two must explain the threshold-versus-loss tradeoff, identify the wrong-sign
symptom, distinguish deterministic sample fractions from field probabilities, and state why
detection alone is not isolation, posterior inference, or recovery without referring to MATLAB
syntax.

Passing static repository tests does not mean these executable checks or the UI ran in MATLAB.
