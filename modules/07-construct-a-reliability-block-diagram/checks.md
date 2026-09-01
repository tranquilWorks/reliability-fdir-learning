# P07 checks: Construct a Reliability Block Diagram

## Observation questions

Answer one at a time after observing the relevant view.

1. Which P06 end effects justify putting the shared supply in series and the two pumps in parallel?
2. Why is `S AND (A OR B)` a functional success statement rather than a physical-layout statement?
3. Why does changing `R_S` move every success path while changing `R_A` matters only when Pump B
   fails?
4. Which event belongs to both minimal success paths, and why does that make the paths neither
   disjoint nor independent?
5. Why must P06 detection coverage stay outside this RBD unless detection triggers a modeled
   recovery action?

## Independent arithmetic and limiting cases

- Convert P06's failure inputs `q=[0.005,0.10,0.10]` to block reliabilities
  `R=[0.995,0.90,0.90]` over the same fixed mission.
- Independently calculate `R_pumps=0.90+(0.10)(0.90)=0.99` and
  `R_system=(0.995)(0.99)=0.98505`.
- Calculate failure from disjoint terms:
  `(1-0.995)+(0.995)(0.10)(0.10)=0.01495`. Confirm it equals P05's top event and that success plus
  failure is one.
- Confirm the five disjoint outcome probabilities
  `[0.00500,0.00995,0.08955,0.08955,0.80595]` sum to one and that the final three sum to system
  reliability.
- Confirm `P(SA)+P(SB)-P(SAB)=0.89550+0.89550-0.80595=0.98505`.
- Sweep `R_S=[0,0.50,0.90,0.995,1]` with both pumps fixed. Confirm
  `R_system=[0,0.495,0.891,0.98505,0.99]` and that the pump group never moves.
- Reset and sweep `R_A=[0,0.25,0.50,0.75,1]`. Confirm
  `R_system=[0.8955,0.920375,0.94525,0.970125,0.995]` while the supply and Pump B never move.
- With `R_S=0`, success is zero. With both pumps at zero, success is zero. With either pump at one,
  system reliability equals `R_S`. With one pump at zero, the RBD reduces to the supply in series
  with the other pump.
- Swapping Pump A and Pump B must not change any system probability.
- A representable tiny success or failure contribution must remain positive in the directly computed
  outcome or failure ledger even when its complement rounds to one.

## Broken-case diagnosis

At `R_S=0.80` and `R_A=R_B=0.90`, calculate the correct one-supply result `0.7920`. Then diagnose
why drawing `S` inside both branches and combining `S-A` and `S-B` as independent paths claims
`0.9216`. Blindly adding the same two path probabilities gives `1.44`, which is an immediate bound
violation.

Name the violated assumption precisely: two drawings of one physical shared-supply success event are
not two independent events. The actual path intersection is `P(SAB)`, not `P(SA)P(SB)`. Repair the
analysis by representing `S` once before the split, or by using the actual intersection or a disjoint
outcome ledger.

## Executable checks

In MATLAB, run:

```matlab
run_checks
```

The checks cover deterministic fixed-size outputs, exact topology identity, complete block and path
metadata, probability bounds and closure, P05 complementarity, outcome and inclusion-exclusion
accounting, both exact sweeps, each sweep's five-state ledger and non-target isolation, symmetry,
limiting and tiny-value cases, the duplicated-supply symptom, malformed scalar inputs, exact recovery
after rejected calls.

The model has three scalar inputs, fixed `1x3`, `1x2`, `2x3`, and `1x5` outputs, no external wait,
file, network, asynchronous work, prompt, or input-size-dependent loop. Dedicated model timeout,
cancellation, and variable-resource tests are therefore not applicable. The existing learner CLI
tests retain bounded subprocess timeouts and isolated temporary state.

## Teach-back gate

In two sentences, answer the guiding question. Sentence one must translate P06's failure modes into
the success rule `S AND (A OR B)` and justify the topology, mission boundary, inputs, and independence
assumption. Sentence two must explain both lever effects and reject the duplicated shared-supply
paths without referring to MATLAB syntax.

Passing static repository tests does not mean these executable checks or the UI ran in MATLAB.
