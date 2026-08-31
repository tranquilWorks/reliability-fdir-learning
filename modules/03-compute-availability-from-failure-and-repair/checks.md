# P03 checks: Compute Availability from Failure and Repair

## Observation questions

Answer one at a time after observing the relevant view.

1. Why are failure and repair transition flows unequal immediately after an item starts up?
2. Which input has units hours, and which derived input has units repairs/hour?
3. Why can two systems have the same `A_inf` but approach it at different speeds?
4. How can an item be available even after its P02 first-failure reliability has become small?

## Limiting cases

- With zero failure rate and an initially up item, explain why availability stays exactly one.
- When `lambda=mu`, independently show why `A_inf=0.5`.
- With an initially down item and zero failure rate, show why repair drives availability toward one.
- If `lambda*MTTR` is unchanged, explain why steady availability is unchanged even though the
  relaxation time may differ.
- As repair becomes negligible, compare the transient with P02's `exp(-lambda*t)` no-repair law.

## Broken-case diagnosis

Name the violated assumption precisely: `exp(-lambda*t)` is no-first-failure reliability for a
nonrepairable item, not point availability for an item that can return from down to up. A curve
that decays toward zero while the repairable state balance remains positive is the recognizable
symptom that repair was omitted.

## Executable checks

In MATLAB, run:

```matlab
run_checks
```

The checks cover determinism, probability bounds, state complement, rate balance, the closed-form
transient, P02's no-repair limit, initial-state recovery, two independent lever effects, limiting
cases, positive-rate initial-state direction, the broken case, malformed inputs, and the
10,000-sample resource bound.

## Teach-back gate

In two sentences, answer the guiding question. Sentence one must relate failure rate and MTTR to
the competing state flows and steady availability, with units. Sentence two must distinguish
repairable point availability from P02 survival without referring to MATLAB syntax.

Passing static repository tests does not mean these executable checks or the UI ran in MATLAB.
