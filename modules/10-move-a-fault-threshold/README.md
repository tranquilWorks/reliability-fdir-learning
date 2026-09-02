# P10 — Move a Fault Threshold

**Track:** Reliability, Diagnostics, and Fault-Tolerant Systems  
**Phase 3:** Detection and isolation  
**Status:** implemented

## Guiding question

What inputs, observable effects, and failure modes matter when you move a Fault Threshold?

## Compounds on P09

P09 generated a signed Pump-A residual from normalized speed command and measured cooling flow:

```text
r(t) = y(t) - y_hat(t|u).
```

Its convention is part of the interface: a Pump-A effectiveness loss makes `r` negative, in
`L/min`. P10 does not redesign that residual. It asks what happens when a nonnegative threshold
magnitude `T` is placed at the signed boundary `-T`:

```text
alarm when r(t) <= -T, for T >= 0.
```

The threshold turns a continuous discrepancy into a decision. Lowering `T` makes the detector more
sensitive to small negative excursions, including nuisance ripple. Raising `T` rejects more
nuisance but can miss a small fault. Neither direction is universally safer without representative
residual evidence and explicit consequences for false alarms and missed detections.

## Deterministic teaching record

The fixed 301-sample record retains P09's `0:0.1:30 s` command and fault timing, matched predictor,
`10 L/min per normalized command` plant gain, and `0.5 Hz` deterministic ripple. The baseline uses
`T=0.50 L/min`, a 20% conditional loss after 20 seconds, and `0.10 L/min` ripple amplitude. In equal
three-cycle high-command windows, healthy residual spans `[-0.1,+0.1] L/min` and the faulted
residual spans `[-1.7,-1.5] L/min`, so the baseline has 0 of 60 healthy samples alarming and all 60
fault samples alarming.

Those fractions are counts in two fixed synthetic windows. They are not estimated field false-alarm
probabilities, detection probabilities, event rates, confidence levels, or safety guarantees.

## Required learning flow

1. Recall P09's residual sign and unit before seeing a threshold.
2. Make one prediction about raising the threshold magnitude.
3. Compare the deterministic residual with the signed `-T` boundary.
4. View the resulting clear/alarm state and its fixed-window counts.
5. Sweep only `T=[0.06,0.12,0.50,1.49,1.56,1.72] L/min` and observe nuisance rejection followed by
   reduced fault detection.
6. Reset `T=0.50 L/min`; sweep only conditional loss `[0,4,6,8,20]%` and observe a small fault move
   through the fixed boundary.
7. Break the comparator by placing the boundary at `+T` while retaining `<=`; identify the healthy
   always-alarm symptom as a wrong-sign error, not a tuning tradeoff.
8. Run independent checks, answer one interpretation question at a time, and teach back the
   mechanism without relying on MATLAB syntax.

## Artifact, assumption, and dependency contract

- `model.m` owns fixed signal construction, the inclusive signed comparison, reference-window
  counts/fractions, and the broken comparator; it contains no presentation.
- `experiment.m` owns labeled residual and decision views, the two isolated sweeps, visible metrics,
  and the deliberately broken case.
- `interactive.m` exposes bounded threshold, conditional-loss, and ripple controls, reset, immediate
  feedback, and one visible view at a time.
- `lesson.m`, `lesson.md`, and `walkthrough.md` preserve the P09 sign/unit boundary and put
  interpretation before controls or syntax.
- `checks.md` and `run_checks.m` cover equations, inclusive comparison, deterministic references,
  monotonic alarm sets, limits, malformed inputs, recovery, isolation, applicability, and teach-back.

The residual and labels are synthetic deterministic teaching artifacts. The model assumes an
already valid and aligned P09 residual, equal costs within each reference window, and a static
threshold without hysteresis, persistence, debounce, adaptation, or mode scheduling. It uses base
MATLAB only and requires no toolbox, random source, data file, network, service, or hardware. P10
does not prove fault isolation, posterior probability, recovery safety, mission impact, or field
performance. Static and independent-reference validation remain distinct from MATLAB-runtime,
rendered-UI, numerical-fidelity, bench, HIL, field, and production evidence.
