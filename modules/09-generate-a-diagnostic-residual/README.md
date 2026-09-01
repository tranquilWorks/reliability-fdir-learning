# P09 — Generate a Diagnostic Residual

**Track:** Reliability, Diagnostics, and Fault-Tolerant Systems  
**Phase 3:** Detection and isolation  
**Status:** implemented

## Guiding question

What inputs, observable effects, and failure modes matter when you generate a Diagnostic Residual?

## Compounds on P08

P08 ranked the `A only` scenario first in its synthetic expected-loss example. That scenario is a
Pump-A component loss with Pump B preserving degraded mission success, not automatically a mission
failure. P09 takes the next step: make a loss of Pump-A effectiveness observable by comparing its
measured cooling flow with the flow predicted from the known speed command.

P08's `q_A` is an occurrence probability over a fixed mission. P09's effectiveness-loss fraction is
a conditional injected magnitude after 20 seconds. A value of `0.20` means 20% less Pump-A flow for
the same command after injection; it does not mean a 20% probability of occurrence.

## Diagnostic mental model

The residual is analytical redundancy: one measured signal is checked against an independently
calculated expectation that uses a known input.

```text
nominal prediction: y_hat(t|u) = K_hat u(t)
measured flow:      y(t)       = K[1-L f(t)]u(t) + n(t)
residual:           r(t)       = y(t) - y_hat(t|u)
                                 ^ fault + model mismatch + ripple
```

Here `u` is normalized Pump-A speed command, `K=10 L/min per normalized command`, `L` is the
conditional effectiveness loss, `f(t)` activates at 20 seconds, and `n(t)` is a deterministic
`0.5 Hz` teaching ripple. The sign convention is fixed: a negative residual means measured flow is
below the command-conditioned prediction.

The baseline changes command from `0.5` to `0.8` at 10 seconds, injects a 20% effectiveness loss at
20 seconds, and uses `K_hat=K`. The correct residual rejects the legitimate command step and changes
from a zero-mean `0.1 L/min` ripple to a `-1.6 L/min` mean. That discrepancy is evidence to inspect;
it is not yet an alarm, a unique diagnosis, a posterior probability, or a recovery decision.

## Required learning flow

1. Read the Pump-A boundary and make one prediction about the normal command transition.
2. Compare measured and command-conditioned predicted flow at the deterministic baseline.
3. View the signed residual and its exact model-mismatch, fault, and ripple decomposition.
4. Sweep only effectiveness loss and observe the post-fault mean move
   `[0,-0.4,-0.8,-1.6,-2.4] L/min`.
5. Reset, then sweep only predictor gain. Observe a healthy residual from model mismatch and the
   gain-8 cancellation that hides the fault mean at one operating point.
6. Break the predictor by freezing its initial expected flow. Observe a normal command transition
   masquerade as a `+3 L/min` fault-like signature.
7. Run independent checks, answer one interpretation question at a time, and teach back the
   mechanism without relying on MATLAB syntax.

## Artifact, assumption, and dependency contract

- `model.m` owns the fixed 301-sample signal construction, residual decomposition, reference-window
  metrics, sensitivities, and broken-predictor arithmetic.
- `experiment.m` owns labeled flow and residual views, two isolated parameter sweeps, metrics, and
  the deliberately broken case.
- `interactive.m` exposes bounded effectiveness-loss, predictor-gain, and ripple controls, reset,
  immediate feedback, and one visible view at a time.
- `lesson.m`, `lesson.md`, and `walkthrough.md` connect P08 risk priority to diagnostic evidence
  before introducing controls or syntax.
- `checks.md` and `run_checks.m` cover equations, sign and units, exact references, limits,
  malformed inputs, mismatch cancellation, recovery, isolation, applicability, and teach-back.

The plant, fault, and ripple are synthetic deterministic teaching signals. The model assumes the
known command is available and aligned with the flow measurement; it omits dynamics, delay,
calibration drift, correlated disturbances, real sensor-noise characterization, thresholds, fault
isolation, posterior inference, and response logic. It uses base MATLAB only and requires no
toolbox, random source, data file, network, service, or hardware. Static and independent-reference
validation are distinct from MATLAB-runtime, rendered-UI, numerical-fidelity, bench, HIL, field,
and production evidence.
