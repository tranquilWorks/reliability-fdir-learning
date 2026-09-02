# P10 lesson: Move a Fault Threshold

## Guiding question

What inputs, observable effects, and failure modes matter when you move a Fault Threshold?

## Why this follows P09

P09 converted Pump-A's known command and measured cooling flow into a signed diagnostic residual:

```text
r(t) = y(t) - y_hat(t|u).
```

The matched residual rejected a normal command transition. A 20% conditional Pump-A effectiveness
loss at normalized command `0.8` created a mean residual of `-1.6 L/min`, while a bounded
deterministic ripple remained. That discrepancy was evidence, not yet an alarm.

P10 adds the decision boundary. It deliberately leaves the P09 plant, predictor, sign, timing, and
units visible so threshold tuning cannot hide a residual-generation defect. Conditional loss
magnitude still is not P08 occurrence probability, and a residual sample still is not a diagnosis.

## Mental model and inclusive decision rule

Choose a nonnegative threshold magnitude `T`. Because the P09 loss signature is negative, place the
signed boundary at `-T`:

```text
decision statistic: z(t) = -r(t)
signed boundary:     b    = -T
alarm:               r(t) <= -T
equivalently:        z(t) >= T.
```

The comparison is inclusive. A sample exactly on the boundary alarms. `T` and `r` both have units
`L/min`; changing `T` moves a decision boundary, not the physical flow or residual.

Lower `T` places `-T` closer to zero. Small negative nuisance excursions can cross it, increasing
false alarms in a healthy labeled window. Higher `T` places `-T` farther below zero. Nuisance is
rejected, but a small fault signature can remain above the boundary and be missed.

The correct threshold depends on consequences, representative residual behavior, operating modes,
and requirements that this synthetic lesson does not supply. The lesson therefore exposes a
tradeoff; it does not optimize or certify a threshold.

## Deterministic baseline

The record runs from 0 to 30 seconds at 0.1-second spacing. Command changes normally from `0.5` to
`0.8` at 10 seconds, the conditional loss begins at 20 seconds, and the matched P09 residual is

```text
r(t) = -10 L f(t)u(t) + 0.1 sin(2 pi 0.5 t)  [L/min].
```

At `L=0.20` and high command `u=0.8`, the fault mean is `-10(0.20)(0.8)=-1.6 L/min`.
Equal three-cycle windows from 12–18 seconds and 22–28 seconds contain 60 samples each and avoid
transitions.

| Window | Residual range | Boundary at `T=0.50` | Alarmed samples |
| --- | ---: | ---: | ---: |
| healthy high command | `[-0.1,+0.1] L/min` | `-0.5 L/min` | `0/60` |
| 20% loss | `[-1.7,-1.5] L/min` | `-0.5 L/min` | `60/60` |

The resulting false-alarm sample fraction is `0` and detection sample fraction is `1` for these
two fixed windows. Those numbers are deterministic counts divided by 60. They are not statistical
estimates, field probabilities, rates, confidence bounds, or evidence that the threshold is safe.

## Lever 1: threshold magnitude

Hold `L=0.20` and ripple amplitude `0.10 L/min`, then sweep
`T=[0.06,0.12,0.50,1.49,1.56,1.72] L/min`.

| `T` (L/min) | Healthy false-alarm fraction | Fault detection fraction |
| ---: | ---: | ---: |
| 0.06 | 0.25 | 1.00 |
| 0.12 | 0.00 | 1.00 |
| 0.50 | 0.00 | 1.00 |
| 1.49 | 0.00 | 1.00 |
| 1.56 | 0.00 | 0.65 |
| 1.72 | 0.00 | 0.00 |

Only the signed boundary and resulting alarm set change. The residual, command, fault magnitude,
ripple, and reference windows remain bit-for-bit fixed. As `T` rises, the alarm set can only shrink.
That monotonic nesting is an independent invariant of this static comparator.

## Lever 2: conditional fault magnitude

Reset `T=0.50 L/min`, keep ripple amplitude `0.10 L/min`, and sweep conditional effectiveness loss
`L=[0,0.04,0.06,0.08,0.20]`.

| Conditional loss | Post-fault mean residual (L/min) | Fault detection fraction |
| ---: | ---: | ---: |
| 0% | 0.00 | 0.00 |
| 4% | -0.32 | 0.00 |
| 6% | -0.48 | 0.45 |
| 8% | -0.64 | 1.00 |
| 20% | -1.60 | 1.00 |

The threshold, ripple, command, and every pre-fault sample remain fixed. Increasing loss moves the
fault residual downward, so its alarm set can only grow. This is a sensitivity study over
conditional magnitude, not a change in occurrence probability or a claim about a field fault
population.

## Deliberately broken case: discard the sign convention

Keep the `<=` comparison but place the boundary at `+T`:

```text
broken alarm: r(t) <= +T.
```

At baseline `T=0.50 L/min`, every healthy ripple sample between `-0.1` and `+0.1 L/min` satisfies
`r<=+0.5`. The correct healthy false-alarm fraction is `0`; the broken fraction is `1`.

The violated assumption is exact: boundary placement must preserve P09's signed meaning. The
recognizable symptom is an alarm that is already asserted throughout ordinary healthy behavior.
Changing the magnitude `T` may hide some symptoms but does not repair the comparator. Restore the
negative boundary or use the equivalent positive statistic `-r>=T`.

## What the decision does and does not establish

A transparent threshold maps one signed residual into a clear/alarm state. It does not establish:

- which of several faults caused the residual — P11;
- a posterior probability for a diagnosis — P12;
- hysteresis, persistence, debounce, adaptation, or mode-dependent threshold scheduling;
- a recovery or degraded-mode action — later phases;
- mission-level failure when Pump B may preserve degraded success;
- field false-alarm rate, detection probability, latency, nuisance distribution, or safety.

## Common misconceptions to correct directly

- **“Raise the threshold to make the detector better.”** No. Nuisance rejection improves while
  sensitivity to small faults decreases.
- **“A low false-alarm fraction here means a low field false-alarm probability.”** No. It is a count
  in one deterministic teaching window.
- **“The threshold fixes model mismatch.”** No. P09 showed mismatch can create or cancel a residual;
  thresholding cannot repair the evidence source.
- **“A detected residual identifies Pump A uniquely.”** No. Detection precedes isolation.
- **“Twenty percent loss means 20% probability.”** No. It is a conditional injected magnitude.
- **“The wrong-sign case just needs retuning.”** No. A sign/interface defect must be corrected before
  magnitude tuning.

## Tutor sequence

Ask the single prediction, show residual versus `-T`, then show the binary decision. Ask which
quantity physically changed and which only classified it. Sweep only `T`, reset, and sweep only
conditional loss. Show the wrong-sign comparator last. Use the equations to explain observed alarm
sets and then request the two-sentence teach-back in `checks.md`.

Static repository checks do not mean `model.m`, figures, UI callbacks, or executable checks ran in
MATLAB. The residual and labels are simulated deterministic teaching artifacts, not bench, HIL,
field, or production evidence.
