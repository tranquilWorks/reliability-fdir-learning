# P09 checks: Generate a Diagnostic Residual

## Observation questions

Answer one at a time after observing the relevant view.

1. Which known input must the nominal predictor receive, and why is measured flow alone
   insufficient to generate a useful discrepancy?
2. Under `r=y-y_hat`, what physical condition does a negative `L/min` residual represent?
3. Why does the matched residual reject the normal 10-second command transition but retain the
   20-second effectiveness-loss signature?
4. Why is P09's 20% conditional loss different from P08's Pump-A occurrence probability `q_A`?
5. Which signals remain fixed when effectiveness loss is swept? Which remain fixed when predictor
   gain is swept?
6. How can predictor mismatch create a healthy residual or cancel a real fault at one operating
   point?
7. Why is a residual neither an alarm threshold nor proof of one unique root cause?
8. What makes the constant-prediction case broken, and why would threshold tuning be the wrong
   repair?

## Independent arithmetic and limiting cases

- Reproduce the 301 samples from 0 to 30 seconds at 0.1-second spacing. Confirm normalized command
  `0.5` before 10 seconds and `0.8` afterward, with loss injection inactive before 20 seconds.
- At matched gain `K_hat=K=10`, calculate mean healthy flows `5` and `8 L/min`. With `L=0.20`,
  calculate post-fault mean flow `10(1-0.20)(0.8)=6.4 L/min`.
- Apply `r=y-y_hat`: healthy reference-window means are zero, command-step residual change is zero,
  post-fault mean and fault-induced shift are `-1.6 L/min`, and a negative sign means less measured
  flow than expected.
- For `0.1 L/min` sinusoidal ripple over equal whole-cycle reference windows, confirm healthy RMS
  `0.1/sqrt(2)=0.0707106781 L/min` and post-fault RMS
  `sqrt(1.6^2+0.1^2/2)=1.6015617378 L/min`.
- Independently add `(K-K_hat)u`, `-K L f u`, and ripple. Confirm the vector equals `y-y_hat` to
  numerical precision.
- Sweep `L=[0,0.05,0.10,0.20,0.30]` with matched gain. Confirm post-fault means and shifts
  `[0,-0.4,-0.8,-1.6,-2.4] L/min`, unchanged prediction, and unchanged pre-fault measurement.
- Reset `L=0.20`; sweep `K_hat=[8,9,10,11,12]`. Confirm healthy high-command means
  `[1.6,0.8,0,-0.8,-1.6] L/min`, post-fault means `[0,-0.8,-1.6,-2.4,-3.2] L/min`, unchanged
  physical measured flow, and an unchanged `-1.6 L/min` before/after fault shift.
- With `L=0`, matched gain, and zero ripple, every correct residual sample is exactly zero. With
  `L=1` and zero ripple, post-fault measured flow is zero and residual is `-8 L/min`.
- With `L=0.20`, `K_hat=8`, and zero ripple, the post-fault residual is zero even though true flow
  remains `6.4 L/min`; inspect the positive healthy mismatch rather than declaring health.
- At all maximum supported scalar inputs, confirm every fixed-size output stays finite. At a small
  positive ripple amplitude equal to floating-point spacing near `5 L/min`, confirm the
  deterministic ripple is not silently replaced by an input-sized operation or external state.

## Broken-case diagnosis

Run a healthy matched model and freeze predicted flow at the initial-command value `5 L/min`.
Confirm the correct residual mean changes by zero at 10 seconds while the broken residual mean
changes by `+3 L/min`.

Name the violated assumption precisely: the nominal predictor omitted the known command input that
materially drives the observable. The recognizable symptom is a large command-correlated discrepancy before
any fault injection. Repair the prediction by conditioning it on speed command. Do not use a
threshold to hide the omitted-input error.

## Executable checks and applicability

In MATLAB, run:

```matlab
run_checks
```

The executable checks cover positive deterministic baseline behavior, independent equations, sign
and unit identity, reference-window means and RMS values, both exact sweeps, non-target isolation,
pointwise component attribution across both sweeps, zero/full-loss and cancellation limiting cases,
the negative omitted-command case, scalar shape, range, nonfinite, infinite, and complex malformed
inputs, and exact recovery after rejected calls.

The model has three bounded scalar inputs, 301 fixed samples, no input-size-dependent loop, no file
or network operation, and no asynchronous task. A dedicated model timeout is therefore not applicable;
shared learner CLI subprocess tests retain a ten-second timeout. Cancellation is not applicable
because there is no timer, job, request lifecycle, blocking prompt, or partial write.
Static scans cover the fixed resource bound, base-MATLAB compatibility path, and absence of opaque
toolbox calls. Isolation checks prove each sweep preserves its non-target physical or predictor
signals. Recovery recomputes the exact baseline after malformed calls. Rollback is file-based,
requires no migration or persistent module state, is documented in retained P09 evidence, and was
not executed.

## Teach-back gate

In two sentences, answer the guiding question. Sentence one must connect P08 priority to Pump-A
command and measured-flow inputs, state `r=y-y_hat` with its sign and unit, and explain why the normal
command change cancels while the 20% loss produces `-1.6 L/min`. Sentence two must distinguish loss
magnitude from occurrence probability, explain the loss and predictor-gain levers plus the broken
omitted-command symptom, and state why residual generation alone is not thresholding, isolation,
posterior inference, or recovery without referring to MATLAB syntax.

Passing static repository tests does not mean these executable checks or the UI ran in MATLAB.
