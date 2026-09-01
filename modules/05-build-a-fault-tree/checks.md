# P05 checks: Build a Fault Tree

## Observation questions

Answer one at a time after observing the relevant view.

1. Why can `{S}` activate the top event alone while `{A}` cannot?
2. Which gate creates cut set `{A,B}`, and which gate joins it with `{S}`?
3. Why does changing only `qA` leave the shared contribution unchanged?
4. Why does an AND gate not by itself justify multiplying event probabilities?
5. Which P04 shared-failure idea became the singleton cut set in P05?

## Independent logic and limiting cases

- Enumerate all eight Boolean states of `S`, `A`, and `B`; confirm that exactly `011`, `100`, `101`,
  `110`, and `111` activate `S OR (A AND B)` when states are written in `SAB` order.
- With all three probabilities zero, the top-event probability is zero.
- With `qS=0`, recover `qT=qA*qB` under the declared pump independence.
- With either pump probability zero, recover `qT=qS`.
- With `qS=1`, the singleton cut set makes `qT=1` for every pump probability.
- With both pump probabilities one, loss of cooling is certain for every `qS`.
- Swapping pump A and pump B must not change the top-event probability.
- Show why `qS + qA*qB - qS*qA*qB` equals the disjoint form.

## Broken-case diagnosis

Name the construction error precisely: replacing `A AND B` with `A OR B` changes redundant-pump
logic so either pump failure becomes sufficient. At the baseline, `0.19405` instead of `0.01495`
is visible overstatement; the decisive symptom is that `S=0, A=1, B=0` falsely triggers the top.

Also distinguish a cut-set sum from a probability. At `qS=qA=qB=0.8`, the raw sum
`qS+qA*qB=1.44` is an upper bound with overlap, while the exact top-event probability remains
bounded at `0.928`.

## Executable checks

In MATLAB, run:

```matlab
run_checks
```

The checks cover determinism, bounds and complement, exact disjoint and inclusion-exclusion forms,
independent truth-state enumeration, baseline references, both lever directions and isolation,
symmetry, limiting cases, a representable tiny AND probability, the broken gate, cut-set overlap,
malformed scalar probabilities, and recovery after rejected calls. The calculation has three
bounded scalar inputs, fixed-size outputs, no asynchronous work, and no variable-size resource.

## Teach-back gate

In two sentences, answer the guiding question. Sentence one must connect the fixed 1000-hour
mission, `T = S OR (A AND B)`, and its two cut sets. Sentence two must explain why the shared and
pump-A levers act through different paths and why the wrong OR gate falsely reports loss of
cooling, without referring to MATLAB syntax.

Passing static repository tests does not mean these executable checks or the UI ran in MATLAB.
