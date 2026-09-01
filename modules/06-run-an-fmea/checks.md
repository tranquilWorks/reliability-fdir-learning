# P06 checks: Run an FMEA

## Observation questions

Answer one at a time after observing the relevant view.

1. What makes “Pump A delivers no flow on demand” a failure mode rather than a cause or end effect?
2. Which row-under-analysis premise lets the Pump-A row end in degraded redundancy, and when must
   you return to P05's combined-event logic instead?
3. Which columns describe physical propagation, and which name evidence that the mode occurred?
4. Why does increasing `qA` grow both detected and latent paths while increasing `cA` only transfers
   occurrence between those paths?
5. How does P06's bottom-up row analysis complement P05's top-down gate combinations?

## Independent arithmetic and limiting cases

- At the baseline, independently calculate detected occurrence as `q*c` and latent occurrence as
  `q*(1-c)` for all three rows. Confirm `[0.0049,0.0700,0.0900]` detected and
  `[0.0001,0.0300,0.0100]` latent.
- Confirm each row identity `detected + latent = q` and the expected-count identity
  `0.1649 + 0.0401 = 0.2050` mode occurrences per mission.
- With one row's `q=0`, both observability paths for that row must be zero for every coverage.
- With `c=0`, the row is entirely latent. With `c=1`, it is entirely detected. Neither limit changes
  the physical occurrence input.
- Set all three occurrence probabilities to one. The expected row count is three, which proves that
  a row sum is not constrained like a union probability.
- A tiny representable occurrence must remain positive in both partitions at coverage `0.5`.
- Changing Pump-A occurrence must leave the supply and Pump-B rows, all coverage values, and every
  causal label unchanged.
- Changing Pump-A coverage must leave all physical occurrence probabilities and causal labels
  unchanged.
- Confirm every pump effect explicitly conditions continued cooling on the companion pump being
  available; the row labels must not claim to describe simultaneous pump modes.

## Broken-case diagnosis

First grant the broken worksheet a favorable logging premise: one oracle-filtered true-positive
record per detected occurrence, perfect specificity, and unique mode attribution. Then name the
violated assumption precisely: it treats those records as complete and assumes every relevant
failure-mode occurrence annunciates. At `qA=0.10, cA=0`, it reports Pump-A occurrence as zero while
the correct latent path remains `0.10`.

Also explain the coverage-sweep symptom. The broken reported occurrence rises from zero to `0.10`
as coverage improves even though Pump-A physics stays fixed. Observation quality has been mistaken
for occurrence prevention. Also state the model's limitation: raw logs may contain false alarms,
duplicates, and ambiguous indicators, so they can overcount or misattribute as well as undercount.

## Executable checks

In MATLAB, run:

```matlab
run_checks
```

The checks cover deterministic fixed-size outputs, complete row metadata, bounded inputs and
outputs, conditional chain-rule partitions, independent baseline references, both exact sweeps and
lever isolation, zero/full/tiny limiting cases, expected counts above one, the broken inventory,
malformed vectors, and exact recovery after rejected calls. The model has two fixed `1x3` inputs,
fixed-size output, no external wait, no asynchronous work, and no variable-size resource; process
timeout and cancellation behavior are therefore not applicable.

## Teach-back gate

In two sentences, answer the guiding question. Sentence one must describe a complete bottom-up FMEA
row, state its single-mode/healthy-companion premise, and connect its three modes to P05's fixed
mission. Sentence two must distinguish occurrence from conditional detection coverage, explain both
lever effects, and reject even filtered true-positive logs as a complete inventory without referring
to MATLAB syntax.

Passing static repository tests does not mean these executable checks or the UI ran in MATLAB.
