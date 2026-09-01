# P08 checks: Prioritize Risk Quantitatively

## Observation questions

Answer one at a time after observing the relevant view.

1. Why does P08 rank four disjoint P07 loss-bearing scenarios rather than the three P06 basic-event
   rows directly?
2. Which two priced outcomes fail the mission, and why are the two single-pump outcomes still
   mission successes?
3. Which units make `probability × consequence` an expected loss that can be compared and added?
4. Why can A-only outrank the rarer, more expensive shared-supply scenario at baseline?
5. Why does increasing `q_S` lower supply-up pump contributions without making supply failure
   beneficial?
6. Why does changing A&B consequence leave every scenario probability fixed?
7. What exactly is invalid about multiplying ordinal occurrence and severity category numbers?

## Independent arithmetic and limiting cases

- From `q=[0.005,0.10,0.10]`, independently calculate P07-order outcome probabilities
  `[0.00500,0.00995,0.08955,0.08955,0.80595]`. Confirm they are mutually exclusive and sum to one.
- Confirm the first two outcomes sum to mission failure `0.01495`, while the last three sum to
  mission success `0.98505`. With `q=[0,1,0]`, confirm Pump A fails and incurs `12` kUSD/mission of
  expected loss while Pump B preserves certain mission success.
- Multiply the first four by `[120,100,8,12]` kUSD per occurrence. Confirm expected losses
  `[0.6000,0.9950,0.7164,1.0746]` kUSD per mission, total `3.3860`, ranks `[4,2,3,1]`, and priority
  order `[A only,A&B,B only,S]`.
- Sweep `q_S=[0,0.005,0.01,0.02,0.05]` while `q_A=q_B=0.10`. Confirm total expected loss
  `[2.800,3.386,3.972,5.144,8.660]` and that only the basic-event probability lever changed.
- Reset, then sweep A&B consequence `[0,25,50,100,200]` kUSD. Confirm its expected loss
  `[0,0.24875,0.49750,0.99500,1.99000]`, total expected loss
  `[2.39100,2.63975,2.88850,3.38600,4.38100]`, and unchanged scenario probabilities.
- Verify the A&B contribution equals A-only at exactly `108` kUSD per occurrence.
- With `q=[0,0,0]`, the healthy probability is one and every risk contribution is zero. With
  `q_S=1`, only the shared-supply scenario has probability one. With `q_S=0,q_A=q_B=1`, only A&B
  has probability one.
- With all consequences zero, total expected loss and every risk share are zero; exact ties retain
  canonical P07 order deterministically.
- Swapping Pump A and Pump B probabilities together with the B-only/A-only consequences must
  preserve total expected loss and swap the corresponding scenario contributions.
- A representable tiny scenario probability and expected loss must remain positive even when its
  complement rounds to one.

## Broken-case diagnosis

Confirm ordinal occurrence ratings `[2,2,5,5]` and severity ratings `[5,5,2,2]` produce four scores
of `10`. Then contrast the zero score spread with the `0.4746` kUSD/mission expected-loss spread.

Name the violated assumption precisely: ordered category labels do not define equal intervals,
meaningful ratios, or a common physical unit. Their product is not an occurrence probability,
consequence, expected loss, or defensible distance between priorities. Repair the analysis by using
bounded scenario probabilities and comparable consequence measurements, retaining safety
constraints separately and exposing uncertainty rather than hiding it inside a score.

## Executable checks and applicability

In MATLAB, run:

```matlab
run_checks
```

The checks cover positive baseline behavior, independent equations, probability closure,
common-unit loss and rank identities, both exact sweeps, non-target isolation, rank crossovers,
zero/certain/tiny limiting cases, pump symmetry, the negative ordinal-product case, malformed shape,
range, nonfinite, and complex inputs, and exact recovery after rejected calls.

The model has two fixed-size vector inputs, fixed `1x3`, `1x4`, and `1x5` outputs, no file or network
operation, no asynchronous task, and no input-size-dependent loop. Dedicated model timeout and
cancellation tests are therefore not applicable; shared learner CLI subprocess tests retain a
ten-second timeout. The fixed consequence ceiling bounds numeric magnitude, and static scans cover
the resource bound, base-MATLAB compatibility path, and state isolation. Rollback is file-based,
requires no migration, and is documented in retained P08 evidence; it was not executed.

## Teach-back gate

In two sentences, answer the guiding question. Sentence one must connect P06 modes to P07 disjoint
scenarios, state the probability and consequence inputs with units and assumptions, and explain the
baseline priority. Sentence two must explain both lever effects, reject the ordinal product, and
keep economic priority separate from evidence quality and safety acceptance without referring to
MATLAB syntax.

Passing static repository tests does not mean these executable checks or the UI ran in MATLAB.
