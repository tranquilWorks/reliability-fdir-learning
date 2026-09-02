# P11 lesson: Isolate Competing Faults

## Guiding question

What inputs, observable effects, and failure modes matter when you isolate Competing Faults?

## Why this follows P10

P10 kept P09's command-conditioned flow residual and applied an inclusive signed boundary:

```text
r_Q(t) = y_Q(t) - y_Q_hat(t|u(t))  [L/min]
alarm when r_Q(t) <= -0.50 L/min.
```

That decision answers “is this negative flow discrepancy large enough?” It does not answer “which
fault caused it?” A physical Pump-A effectiveness loss and a primary flow sensor biased low can
produce the same `r_Q` trace. Moving the same threshold cannot separate identical evidence.

P11 adds a complementary pressure residual:

```text
r_P(t) = y_P(t) - y_P_hat(t|u(t))  [kPa].
```

The synthetic teaching model declares a calibrated pressure-to-flow sensitivity of
`5 kPa/(L/min)`. Pump loss therefore drives both residuals negative. Flow-sensor bias changes only
the measured flow channel and leaves pressure at its healthy command-conditioned prediction.

## From alarms to a residual signature

Use the fixed high-command window `W=22–28 s`, which contains 60 samples and three deterministic
ripple cycles. Threshold its two mean residuals:

```text
s_Q = [mean_W(r_Q) <= -0.50 L/min]
s_P = [mean_W(r_P) <= -4.00 kPa]
s   = [s_Q, s_P].
```

The implementation applies a visible `16 eps` comparison tolerance at each feature magnitude. It
keeps analytically exact inclusive settings—`0.50 L/min` sensor bias and 10% pump loss—on their
flow and pressure boundaries despite finite sampled-sine means. This is numerical hygiene, not a
confidence interval or physical uncertainty model.

Square brackets here mean a Boolean test: each component is zero or one. The candidate signature
matrix is visible rather than hidden in a toolbox:

```text
healthy                    00
Pump-A effectiveness loss  11
flow-sensor negative bias  10
```

Hamming distance counts unequal bits between the observed signature and each candidate. One exact
match has distance zero. This deterministic lookup is not Bayesian inference, a likelihood, or
confidence. P12 will add probability explicitly.

## Baseline: equal flow evidence, different pressure evidence

The command steps from `0.5` to `0.8` at 10 seconds and injection begins at 20 seconds. Both cases
below produce the exact same post-fault flow mean and trace:

| Teaching injection | Mean flow residual | Mean pressure residual | Code |
| --- | ---: | ---: | ---: |
| 20% Pump-A loss | `-1.6 L/min` | `-8 kPa` | `11` |
| `1.6 L/min` negative flow-sensor bias | `-1.6 L/min` | `0 kPa` | `10` |

The first view deliberately withholds pressure. Both flow traces overlap and both cross P10's
boundary. The second view adds pressure; only the pump case crosses. The third view presents the
two-bit pattern. Isolation comes from how evidence changes across channels, not from giving the
faults different names.

The model also exposes

```text
r_P(t) - 5 r_Q(t) = 5 B f(t)  [kPa],
```

where `B` is the nonnegative magnitude of a negative primary-flow sensor bias and `f(t)` activates
at injection. Pump loss and the calibrated ripple cancel from this consistency residual. That
identity is an independent check of this declared model, not a general pump law.

## Lever 1: Pump-A loss and a coverage gap

Hold bias at zero and sweep conditional Pump-A loss `[0,0.04,0.08,0.12,0.20]`.

| Loss | Mean `r_Q` (L/min) | Mean `r_P` (kPa) | Code | Correct modeled isolation? |
| ---: | ---: | ---: | ---: | --- |
| 0% | 0 | 0 | `00` | healthy |
| 4% | -0.32 | -1.6 | `00` | no — below both tests |
| 8% | -0.64 | -3.2 | `10` | no — matches sensor bias |
| 12% | -0.96 | -4.8 | `11` | yes |
| 20% | -1.60 | -8.0 | `11` | yes |

At 8%, the flow feature crosses before pressure. The signature table returns a unique exact match,
but it is the wrong candidate for the injected teaching case. A unique signature lookup is only as
good as its thresholds and coverage. The result is a deterministic coverage-gap example, not an
estimated field misisolation probability.

## Lever 2: flow-sensor bias

Reset pump loss to zero. Sweep negative bias magnitude `[0,0.30,0.60,1.00,1.60] L/min`.

| Bias magnitude | Mean `r_Q` (L/min) | Mean `r_P` (kPa) | Code |
| ---: | ---: | ---: | ---: |
| 0 | 0 | 0 | `00` |
| 0.30 | -0.30 | 0 | `00` |
| 0.60 | -0.60 | 0 | `10` |
| 1.00 | -1.00 | 0 | `10` |
| 1.60 | -1.60 | 0 | `10` |

Only the bias component and flow residual change. Pressure, pump-loss components, command, timing,
thresholds, and candidate matrix remain fixed. Once flow crosses, the expected sensor signature is
stable.

## Deliberately broken case: remove the discriminating channel

If the decoder discards pressure, the library becomes:

```text
healthy  0
pump     1
sensor   1
```

A flow alarm now gives two exact matches. The symptom is explicit ambiguity, and the violated
assumption is diagnosability: modeled candidates must have distinct signatures over the channels
actually used. Threshold tuning cannot recreate pressure evidence after it has been removed.

## Applicability boundary

The library assumes at most one modeled fault. If Pump-A loss and flow-sensor bias are both nonzero,
the raw signature can still be `11` and look like pure pump loss. The simulator knows both inputs,
so it marks the single-fault decoder not applicable instead of presenting the raw match as a
complete diagnosis. Operational systems need explicit multiple-fault hypotheses, uncertainty
handling, or a justified exclusion argument.

The fixed window also omits online latency, persistence, hysteresis, debounce, mode scheduling, and
recovery. Conditional injected magnitude is not occurrence probability. Fixed-window outcomes are
not field detection, isolation, or false-alarm rates.

## Common misconceptions to correct directly

- **“One alarm identifies one fault.”** No. P10 detects a discrepancy; P11 needs a pattern that
  distinguishes candidate causes.
- **“Different fault names imply different signatures.”** No. Diagnosability depends on the
  channels actually observed and retained.
- **“One exact match means certainty.”** No. It is exact only within the declared thresholds,
  candidate library, and single-fault assumptions.
- **“The 8% pump result proves the sensor failed.”** No. It exposes insufficient pressure-channel
  coverage for a real pump-loss teaching injection.
- **“Twenty percent loss means 20% probability.”** No. It is a conditional fault magnitude.
- **“Dropping pressure can be repaired by tuning flow.”** No. Tuning cannot restore discarded
  discriminatory information.
- **“Code 11 remains valid when both controls are nonzero.”** The bits are valid evidence, but the
  single-fault interpretation is not applicable.

## Tutor sequence

Ask the single prediction, then show only the overlapping flow residuals. Ask what was detected and
what remains unknown. Show pressure next, then the signature pattern and its Hamming distances.
Move only Pump-A loss, reset, and move only sensor bias. Correct the 8% misisolation directly. Show
the flow-only broken decoder last and request the two-sentence teach-back in `checks.md`.

Static repository checks do not mean the model, plots, controls, callbacks, or executable checks ran
in MATLAB. These are synthetic deterministic teaching artifacts, not bench, HIL, field, or
production evidence.
