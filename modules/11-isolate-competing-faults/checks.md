# P11 checks: Isolate Competing Faults

## Observation questions

Answer one at a time after observing the relevant view.

1. Which P10 sign, unit, and signed boundary does P11 preserve on the flow channel?
2. Why do the 20% pump-loss and `1.6 L/min` sensor-bias flow traces overlap exactly?
3. What does the flow alarm establish, and what cause information does it lack?
4. Why does pressure move for modeled pump loss but not primary flow-sensor bias?
5. How do the candidate signatures `00`, `11`, and `10` arise from the two mean tests?
6. Why is Hamming distance a bit mismatch count rather than a posterior probability or confidence?
7. Which quantities remain fixed in the Pump-A loss sweep? Which remain fixed in the sensor-bias
   sweep?
8. Why does an 8% pump loss match the sensor code `10`, and what does that say about isolation
   coverage?
9. What exact assumption does the flow-only broken case violate, and why can tuning not repair it?
10. Why is the single-fault interpretation not applicable when both fault controls are nonzero?
11. Why are fixed-window outcomes not field detection, isolation, or misisolation rates?
12. Why is deterministic isolation neither P12 Bayesian diagnosis nor a recovery or safety action?

## Independent arithmetic and limiting cases

- Reproduce the P10-compatible grid `0:0.1:30 s`, command `0.5` before 10 seconds and `0.8`
  afterward, and injection at 20 seconds. Confirm both 12–18 and 22–28 second windows contain 60
  samples and exactly three ripple cycles.
- Reproduce `r_Q=-10Lu-B+0.10 sin(2 pi 0.5t)` after activation, with `B` interpreted as the
  magnitude of a negative flow-sensor bias. Reproduce
  `r_P=-50Lu+0.50 sin(2 pi 0.5t)` in `kPa`.
- Independently confirm `r_P-5r_Q=5B` after activation. The identity cancels the declared pump
  signature and calibrated ripple.
- For 20% pump loss and zero bias, confirm means `[-1.6 L/min,-8 kPa]`, code `11`, Hamming distances
  `[2,0,1]`, and one exact Pump-A match.
- For zero pump loss and `1.6 L/min` bias, confirm the entire flow trace matches the pump baseline,
  pressure mean is zero, code `10`, distances `[1,1,0]`, and one exact sensor match.
- Sweep only pump loss `[0,0.04,0.08,0.12,0.20]`. Confirm flow means
  `[0,-0.32,-0.64,-0.96,-1.6] L/min`, pressure means `[0,-1.6,-3.2,-4.8,-8] kPa`, and codes
  `00,00,10,11,11`. Confirm the 8% injected pump case is deliberately marked incorrect.
- Reset pump loss; sweep only bias `[0,0.30,0.60,1.00,1.60] L/min`. Confirm flow means
  `[0,-0.30,-0.60,-1.00,-1.60] L/min`, pressure means all zero, and codes
  `00,00,10,10,10`.
- At zero inputs, confirm healthy code `00`. At full loss, confirm means `-8 L/min` and `-40 kPa`,
  finite fixed-size outputs, and code `11`. At maximum `10 L/min` bias, confirm pressure remains
  healthy and code is `10`.
- At exactly `0.50 L/min` bias, confirm the analytically inclusive flow boundary gives `10`. At
  exactly 10% loss, confirm the analytically inclusive pressure boundary gives `11`. Inspect the
  named `16 eps` tolerances and distinguish numerical inclusion from physical uncertainty.
- Move each input `128 eps(1)` below its analytic boundary. Confirm the just-clear sensor case stays
  `00` and the just-clear pressure case stays `10`; the roundoff tolerance must not become a wider
  physical decision band.
- At loss `0.0625` with zero bias, reproduce P10's pointwise direct fault-plus-ripple sum and confirm
  every P11 flow sample and P10 alarm bit is exactly identical, including boundary-adjacent samples.
- With both faults nonzero, confirm the raw bits still close mathematically but the simulator marks
  the single-fault library not applicable. Evidence and interpretation are separate outputs.
- Remove pressure from the baseline decoder. Confirm flow-only candidates are `[0,1,1]`, both fault
  candidates have zero Hamming distance, and exact-match count is two. Candidate faults no longer
  retain distinct signatures over the channels used by the decoder.

## Executable checks and applicability

In MATLAB, run:

```matlab
run_checks
```

The executable checks cover positive deterministic behavior, independent flow and pressure
equations, component closure, P10 compatibility outputs, fixed-window features, exact signatures
and Hamming distances, both isolated sweeps, the weak-pump negative case, the flow-only broken case,
zero/full/tiny/maximum limits, simultaneous-fault applicability, and scalar shape, range, NaN, Inf,
and complex malformed inputs. Recovery recomputes the exact baseline after rejected calls.

The model has two bounded scalar inputs, 301 fixed samples, no input-size-dependent loop, file,
network, process, service, timer, asynchronous work, blocking prompt, or persistent/global state.
A dedicated model timeout is not applicable; shared learner CLI subprocess tests retain a
ten-second timeout. Cancellation is not applicable because there is no request, job, timer,
partial write, or wait lifecycle.

Static scans cover the fixed resource bound, transparent base-MATLAB compatibility path, and
absence of opaque diagnostic toolbox calls. Isolation checks prove each sweep holds the other fault
path and the non-target channel fixed. A focused compatibility regression compares P11's zero-bias
flow residual and pointwise alarm with P10 over boundary and representative loss cases. Rollback is
selective and file-based, requires no migration or persistent state, is documented in retained P11
evidence, and was not executed.

## Teach-back gate

In two sentences, answer the guiding question. Sentence one must connect P10's negative flow alarm
to the need for a pressure residual and explain why `11` isolates modeled pump loss while `10`
isolates modeled sensor bias. Sentence two must identify the 8% coverage gap and flow-only ambiguity,
state the single-fault applicability boundary, distinguish a signature match from probability and
field performance, and avoid relying on MATLAB syntax.

Passing static repository tests does not mean these executable checks or the UI ran in MATLAB.
