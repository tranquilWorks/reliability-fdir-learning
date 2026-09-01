# P07 lesson: Construct a Reliability Block Diagram

## Guiding question

What inputs, observable effects, and failure modes matter when you construct a Reliability Block Diagram?

## Start from P06's functions, not from a diagram template

P06 traced three cooling-system failure modes from item function to end effect over a fixed
1000-hour, no-repair mission. Reverse each statement:

- shared supply absent becomes “the shared supply energizes the cooling bus”;
- Pump A no flow becomes “Pump A carries the cooling load”;
- Pump B no flow becomes “Pump B carries the cooling load.”

The FMEA effects decide the functional arrangement. Shared supply loss alone makes cooling
unavailable, so every success path needs the supply. Either single pump failure only loses
redundancy while its companion carries the load, so either pump is sufficient. The success rule is:

```text
S works AND (A works OR B works).
```

This is why the RBD contains one shared supply block in series with a one-out-of-two parallel pump
group. An RBD is not a wiring, piping, or floor-plan diagram. Series means every named function is
required for success; parallel means the branches are true functional alternatives.

## Define inputs and assumptions before multiplying

Every block reliability must use the same boundary and mission duration. For P06's synthetic
per-mission failure probabilities `q=[0.005,0.10,0.10]`, the success probabilities are
`R=1-q=[0.995,0.90,0.90]`.

To quantify the RBD, explicitly assume the `S`, `A`, and `B` block-success events are independent.
Topology tells us what success requires; it does not establish statistical independence. P04 showed
how shared environment, design, or support can defeat a nominally redundant group.

Use a disjoint form for the pump group:

```text
R_pumps = P(A works) + P(A fails and B works)
        = R_A + (1-R_A)R_B.
```

Then:

```text
R_system = R_S[R_A + (1-R_A)R_B] = 0.98505
Q_system = (1-R_S) + R_S(1-R_A)(1-R_B) = 0.01495.
```

The two failure terms are disjoint: either the supply fails, or it works and both pumps fail. This
is exactly the P05 top event `S OR (A AND B)` under the same assumptions, so `R_system+Q_system=1`.

## Audit the success paths without double counting

The minimal success paths are `S-A` and `S-B`. Their baseline probabilities are both `0.89550`, but
their raw sum `1.79100` is not a probability because the paths overlap. The intersection is the state
where `S`, `A`, and `B` all work, with probability `0.80595`. Inclusion-exclusion gives:

```text
P(SA OR SB) = P(SA) + P(SB) - P(SAB)
            = 0.89550 + 0.89550 - 0.80595
            = 0.98505.
```

The disjoint outcome ledger makes the same result visible. Supply failure has probability `0.00500`;
supply success with both pumps failed has probability `0.00995`; the A-only, B-only, and both-pump
success states have probabilities `0.08955`, `0.08955`, and `0.80595`. All five sum to one, and the
last three sum to system success.

## Observe one lever at a time

Make one prediction: should the one shared supply appear once before the split or once in each pump
branch? Inspect the correct topology and the outcome ledger before moving a control.

First sweep only `R_S` through `[0,0.50,0.90,0.995,1]` while both pump reliabilities stay `0.90`.
System reliability becomes `[0,0.495,0.891,0.98505,0.99]`. The pump group remains `0.99`; every valid
path moves because every path crosses `S`.

Reset. Sweep only `R_A` through `[0,0.25,0.50,0.75,1]` while `R_S=0.995` and `R_B=0.90`. System
reliability becomes `[0.8955,0.920375,0.94525,0.970125,0.995]`. Pump A matters only in outcomes where
Pump B fails, so its slope is smaller than the shared-supply slope.

## Deliberately broken case

Redraw the one physical supply inside each pump branch, label the two drawings as if they were
independent supplies, and combine the apparent `S-A` and `S-B` paths as independent parallel events:

```text
R_wrong = P(SA) + [1-P(SA)]P(SB).
```

The redraw did not create a second supply. At a stressed `R_S=0.80` and `R_A=R_B=0.90`, the correct
one-supply RBD gives `0.7920`, while the broken independent-path calculation claims `0.9216`. Blindly
adding the two path probabilities claims `1.44`, which is impossible. Both symptoms come from the
same violated assumption: success paths that share the physical `S` event are neither disjoint nor
independent.

## Observable effects do not define topology

P06 associated low bus voltage with `S`, abnormal Pump-A current with `A`, and low Pump-B branch flow
with `B`. These observables help identify evidence about a block. Detection coverage partitions
observed and latent occurrences, but it does not change the RBD probability unless the model also
contains a justified detection, switching, repair, or recovery mechanism.

## Common misconceptions to correct directly

- Series and parallel describe functional success logic, not physical geometry.
- A component that appears in every success path belongs upstream of the branch; copying its picture
  does not create independent hardware.
- Two minimal success paths may overlap. Add them only when they are disjoint, or subtract their
  intersection.
- Topology does not prove independence; dependencies need their own model and evidence.
- Block reliabilities cannot be combined when they refer to different mission durations or boundaries.
- Detection coverage is not reliability improvement without a modeled recovery action.
- A high computed reliability is conditional on the chosen boundary, inputs, topology, and assumptions;
  it is not qualification evidence.

## Completion standard

The learner can translate P06's three rows into `S AND (A OR B)`, justify each series or parallel
placement, reproduce the baseline from either the RBD or P05's complement, explain both isolated
sweeps, diagnose the duplicated-supply case, pass `run_checks.m`, and give a two-sentence,
mechanism-first teach-back without relying on MATLAB syntax.
