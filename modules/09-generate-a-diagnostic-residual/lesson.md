# P09 lesson: Generate a Diagnostic Residual

## Guiding question

What inputs, observable effects, and failure modes matter when you generate a Diagnostic Residual?

## Why this follows P08

P08 used P07's disjoint scenarios to rank synthetic expected economic loss. Its `A only` scenario
ranked first, but Pump B still preserved degraded mission success. Priority tells us where diagnostic
attention may be valuable; it does not create evidence that Pump A has lost effectiveness.

P09 begins the detection-and-isolation phase by constructing that evidence. We observe Pump-A
cooling flow and compare it with a nominal expectation derived from the known speed command. The
comparison is analytical redundancy: the command-conditioned model supplies the reference.

Keep two quantities separate:

- P08 `q_A` is the occurrence probability of a Pump-A basic event over a fixed mission.
- P09 `L` is the conditional fraction of flow effectiveness lost after a deterministic injection.

`L=0.20` means measured flow is 20% lower for the same command after injection. It is not an
occurrence probability, field rate, or probability that the diagnosis is correct.

## Mental model and sign convention

The transparent teaching equations are

```text
y_hat(t|u) = K_hat u(t)
y(t)       = K[1-L f(t)]u(t) + n(t)
r(t)       = y(t)-y_hat(t|u)
           = [K-K_hat]u(t) - K L f(t)u(t) + n(t).
```

`u(t)` is normalized speed command. `K=10 L/min per normalized command` is the deterministic plant
gain; `K_hat` is the predictor gain. `f(t)` changes from zero to one at 20 seconds. `n(t)` is a
bounded deterministic `0.5 Hz` ripple with baseline amplitude `0.1 L/min`.

The sign convention is part of the interface: `r=y-y_hat`. A negative residual means measured flow
is below the command-conditioned prediction. Reversing the subtraction would reverse every sign and
must be treated as a different convention, not a cosmetic plotting choice.

The decomposition names three reasons a residual can exist:

1. a physical effectiveness loss;
2. mismatch between the plant and predictor gains;
3. measurement ripple or another unmodeled disturbance.

That is why a nonzero residual is not automatically a fault and a zero residual at one operating
point is not automatically health.

## Deterministic baseline

The fixed 301-sample record runs from 0 to 30 seconds at 0.1-second spacing.

| Interval | Known command | Injected loss | Nominal predicted flow | Mean measured flow |
| --- | ---: | ---: | ---: | ---: |
| before 10 s | `0.5` | 0% | `5 L/min` | `5 L/min` |
| 10 to 20 s | `0.8` | 0% | `8 L/min` | `8 L/min` |
| after 20 s | `0.8` | 20% | `8 L/min` | `6.4 L/min` |

Make one prediction before viewing the baseline: should a correct residual jump when the known
command changes normally at 10 seconds?

It should not. The prediction receives the command, so expected and measured flow both rise by
`3 L/min`. Their difference stays centered at zero. After the injected loss, expected flow remains
`8 L/min`, mean measured flow becomes `6.4 L/min`, and residual mean becomes `-1.6 L/min`.

Equal three-cycle reference windows avoid transition samples. The baseline high-command healthy
RMS is `0.1/sqrt(2) = 0.0707107 L/min`; the post-fault RMS is
`sqrt(1.6^2+0.1^2/2) = 1.60156 L/min`. Those are deterministic reference values, not measured noise
statistics or false-alarm performance.

## Lever 1: conditional effectiveness loss

Hold `K_hat=10` and ripple amplitude `0.1 L/min`, then sweep
`L=[0,0.05,0.10,0.20,0.30]`. At the high command, the expected signature is

```text
post-fault mean r = -K L u = -10 L(0.8).
```

The means are `[0,-0.4,-0.8,-1.6,-2.4] L/min`. The prediction, command, and every pre-fault signal
stay fixed. Larger conditional loss makes the residual more negative because less physical flow is
measured for the same expected flow.

This sweep varies magnitude after injection. It does not vary how often the fault occurs.

## Lever 2: predictor gain

Reset to `L=0.20`, then sweep `K_hat=[8,9,10,11,12] L/min per normalized command`. Physical command,
true flow, measured flow, fault injection, and ripple remain fixed; only the nominal expectation
changes.

At the healthy high-command window, mean residuals become `[1.6,0.8,0,-0.8,-1.6] L/min`. After the
fault they become `[0,-0.8,-1.6,-2.4,-3.2] L/min`. The before/after fault shift stays `-1.6 L/min`
because both reference windows use the same `0.8` command.

At `K_hat=8`, positive model mismatch cancels the negative fault signature after injection. The
post-fault mean is zero even though the physical 20% loss remains. Elsewhere the same mismatched
predictor creates a healthy residual. Operating-point coverage and model validation therefore matter
before a residual can support a decision.

## Deliberately broken case: omit a known input

Freeze predicted flow at the initial-command value instead of conditioning it on `u(t)`. In a
healthy run, the broken residual is near zero before 10 seconds and near `+3 L/min` afterward. The
correct residual mean changes by zero across the normal command transition; the broken residual
mean changes by `+3 L/min`.

The violated assumption is precise: the nominal predictor must receive every known input that
materially drives the observable. The symptom is also precise: a legitimate command change creates a
large fault-like residual before any fault injection. Repair the residual generator by restoring the
known command to the prediction, not by inventing a threshold that masks the modeling error.

## What the residual does and does not establish

A well-formed residual makes a discrepancy visible in a defined unit and sign convention. It can be
sensitive to a Pump-A effectiveness loss. It does not by itself establish:

- an alarm threshold or false-alarm/missed-detection tradeoff — P10;
- which of several physical faults caused the discrepancy — P11;
- a posterior probability of a diagnosis — P12;
- a recovery or degraded-mode decision — later phases;
- that Pump-A loss causes overall mission failure — P07's companion pump still matters;
- that the deterministic ripple represents a field sensor or environment.

## Common misconceptions to correct directly

- **“Any nonzero residual proves a fault.”** No. Predictor mismatch and disturbances also appear in
  the residual.
- **“Zero residual proves health.”** No. Mismatch can cancel a fault at one operating point.
- **“A threshold can repair a poor predictor.”** No. Thresholding cannot restore an omitted known
  input or correct a sign/units error.
- **“Twenty percent loss means 20% fault probability.”** No. Conditional magnitude and occurrence
  probability answer different questions.
- **“Synthetic ripple is measured noise evidence.”** No. It only makes bounded nuisance behavior
  visible in this deterministic lesson.
- **“Residual sensitivity is fault specificity.”** No. More than one cause can produce the same
  discrepancy; isolation requires additional structure.

## Tutor sequence

Ask the one prediction, show measured and predicted flow, then show the residual. Ask what canceled at
10 seconds and what remained at 20 seconds. Move only effectiveness loss, reset, then move only
predictor gain. Show the omitted-command broken case last. Use the equations to explain the observed
sign and magnitude, then request the two-sentence teach-back in `checks.md`.

Static repository checks do not mean `model.m`, plots, UI callbacks, or executable checks ran in
MATLAB. The signals are simulated deterministic teaching artifacts, not bench, HIL, field, or
production evidence.
