# P11 — Isolate Competing Faults

**Track:** Reliability, Diagnostics, and Fault-Tolerant Systems
**Phase 3:** Detection and isolation
**Status:** implemented

## Guiding question

What inputs, observable effects, and failure modes matter when you isolate Competing Faults?

## Compounds on P10

P10 applied the signed rule `r_Q(t)<=-T_Q` to a command-conditioned Pump-A flow residual in
`L/min`. A negative discrepancy crossed the boundary, but one alarm could not say whether the pump
lost effectiveness or the primary flow sensor became biased low. Those competing faults can create
the same flow trace.

P11 retains P10's exact 301-sample flow record and its `T_Q=0.50 L/min` boundary. It adds a
command-conditioned discharge-pressure residual in `kPa`:

```text
r_Q(t) = y_Q(t) - y_Q_hat(t|u(t))
r_P(t) = y_P(t) - y_P_hat(t|u(t)).
```

Under the declared synthetic sensitivity, Pump-A effectiveness loss moves both residuals negative;
a negative primary flow-sensor bias moves only `r_Q`. Mean residuals in the fixed 22–28 second
window are compared with inclusive signed boundaries:

```text
flow test     = mean_W(r_Q) <= -0.50 L/min
pressure test = mean_W(r_P) <= -4.00 kPa
signature     = [flow test, pressure test].
```

Each mean comparison allows an explicit `16 eps` floating-point tolerance at the compared
magnitude, so a setting analytically on either inclusive boundary is not cleared by sampled-sine
roundoff. This numerical tolerance does not represent physical uncertainty or widen a field limit.

The candidate library is deliberately small and visible:

| Candidate | Flow test | Pressure test | Code |
| --- | ---: | ---: | ---: |
| no modeled fault | 0 | 0 | `00` |
| Pump-A effectiveness loss | 1 | 1 | `11` |
| negative flow-sensor bias | 1 | 0 | `10` |

The decoder uses exact binary signatures and Hamming distance. It does not compute probability,
confidence, risk, or a recovery command.

## Deterministic baseline

The fixed record runs from 0 to 30 seconds at 0.1-second spacing. Normalized command changes from
`0.5` to `0.8` at 10 seconds; injection begins at 20 seconds. P10's deterministic flow ripple is
`0.10 sin(2 pi 0.5 t) L/min`. The pressure residual uses the visible calibrated factor
`5 kPa/(L/min)` and `0.50 sin(2 pi 0.5 t) kPa` ripple.
P11 forms `r_Q` with P10's direct fault-plus-ripple operation order, adding sensor bias as a third
component; when bias is zero, the pointwise P10 flow residual and alarm record are preserved.

Two competing single-fault baselines have identical flow evidence:

| Injected teaching case | Mean `r_Q` | Mean `r_P` | Signature | Exact candidate |
| --- | ---: | ---: | ---: | --- |
| 20% Pump-A loss | `-1.6 L/min` | `-8 kPa` | `11` | Pump-A loss |
| `-1.6 L/min` flow-sensor bias | `-1.6 L/min` | `0 kPa` | `10` | flow-sensor bias |

The continuous consistency residual `r_P-5r_Q` cancels the modeled pump signature and calibrated
ripple. It is zero for pure pump loss and `5B kPa` for a negative flow-sensor bias magnitude `B`.
This identity depends on the declared calibration; it is not a universal physical law.

## Two independent levers

1. Hold sensor bias at zero and sweep Pump-A loss `[0,4,8,12,20]%`. Flow crosses first at 8%,
   producing code `10` and a wrong sensor-bias match before pressure crosses. This is a visible
   threshold-coverage gap, not a field misisolation rate.
2. Reset pump loss to zero and sweep negative flow-sensor bias
   `[0,0.30,0.60,1.00,1.60] L/min`. Once flow crosses, pressure remains clear and code `10`
   isolates the modeled sensor bias.

## Deliberately broken case

Remove the pressure channel from the decoder. The fault candidates collapse from `11` and `10` to
the same flow-only code `1`, so a flow alarm has two exact matches. The violated diagnosability
assumption is precise: candidate faults must retain distinct signatures over the channels actually
used. No threshold retuning can restore discarded information.

## Required learning flow

1. Recall P10's flow sign, unit, and detection boundary.
2. Make one prediction before viewing the baseline.
3. Observe the identical flow residuals one plot at a time.
4. Add pressure and observe which candidate changes.
5. Read the `11` versus `10` mechanism before touching controls.
6. Sweep only Pump-A loss, reset, then sweep only sensor bias.
7. Remove pressure and diagnose the two-match broken symptom.
8. Run independent checks, answer one interpretation question at a time, and teach back the
   mechanism without MATLAB syntax.

## Artifact, assumption, and dependency contract

- `model.m` owns fixed signals, residual decomposition, window features, signature/Hamming
  calculations, injected-case applicability, and the broken flow-only decoder; it has no plots.
- `experiment.m` owns six labeled views, baseline metrics, two isolated sweeps, and one broken case.
- `interactive.m` exposes bounded loss and bias controls, reset, immediate feedback, and one
  `uiaxes` view at a time.
- `lesson.m`, `lesson.md`, and `walkthrough.md` put the P10 evidence interface and isolation
  mechanism before controls or syntax.
- `checks.md` and `run_checks.m` cover equations, exact signatures, both sweeps, limiting cases,
  malformed inputs, compatibility, recovery, applicability, and teach-back.

The implementation uses base MATLAB only and needs no toolbox, randomness, data file, network,
service, or hardware. The library assumes aligned measurements, known command, calibrated channel
sensitivity, fixed windows and thresholds, distinct modeled signatures, and at most one modeled
fault. Delay, drift, saturation, correlated disturbances, operating-mode changes, unmodeled or
combined faults, persistence, hysteresis, and field coverage remain outside this lesson.

P12 will reason about diagnostic uncertainty. P11 does not establish a posterior probability,
field detection or isolation rate, latency, safety, mission effect, or recovery action. Static and
independent-reference validation remain distinct from MATLAB-runtime, rendered-UI,
numerical-fidelity, bench, HIL, field, and production evidence.
