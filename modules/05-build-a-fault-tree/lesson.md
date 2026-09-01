# P05 lesson: Build a Fault Tree

## Guiding question

What inputs, observable effects, and failure modes matter when you build a Fault Tree?

## Start from P04, not from syntax

P04 showed that a shared cause and channel-specific failures create different system-level paths.
P05 makes those paths visible as a fault tree. The shared electrical-supply loss is one event `S`.
It is not copied into two pump branches and then treated as two independent events.

The system boundary is a two-pump cooling function over one fixed 1000-hour no-repair mission. `A`
means pump A has a pump-specific failure during those 1000 hours, and `B` means the same for pump B.
Repair, switching, sequence, and events outside the mission boundary are not part of this tree.

## Mental model: gates define sufficient event combinations

The top event `T` is “the cooling function is unavailable by the mission boundary.” Either the
shared supply is lost, or both pumps have their pump-specific failures:

```text
T = S OR (A AND B)

             cooling unavailable T
                       OR
                 /             \
       shared supply S         AND
                              /   \
                        pump A     pump B
```

The minimal cut sets are `{S}` and `{A,B}`. A cut set is a sufficient combination: `S` alone reaches
the top, while `A` alone and `B` alone do not. “Minimal” means removing any event from the set makes
it insufficient.

All three inputs are dimensionless probabilities over the same 1000-hour mission. With `S`, `A`,
and `B` independent in this teaching calculation, the exact top-event probability is

```text
qT = qS + (1-qS)*qA*qB.
```

The displayed contributions are deliberately non-overlapping: `qS` accounts for every mission
where `S` occurs, and `(1-qS)qAqB` accounts for missions with no `S` where both pumps fail. The raw
minimal-cut-set probabilities are `qS` and `qAqB`; simply adding them double-counts the state where
all three events occur. Inclusion-exclusion gives the same exact result:

```text
qT = qS + qA*qB - qS*qA*qB.
```

The AND gate is Boolean logic, not permission to multiply. The products additionally use the
declared independence of all three basic events. Any unmodeled pump common cause or dependence
between supply and pump-specific events would make the quantified result wrong.

## Observe one transition at a time

Make one prediction: with the supply healthy, does pump A failing alone activate the top event?
Then view only the baseline tree. Name the top event, all three basic events, both gates, the mission
boundary, and the two minimal cut sets before advancing.

Next view the probability decomposition. At `qS=0.005` and `qA=qB=0.10`, the shared contribution is
`0.005`, the no-shared/dual-pump contribution is `0.00995`, and the exact top-event probability is
`0.01495` per mission.

First increase only `qS`. The singleton cut set rises directly. The mutually exclusive dual-pump
contribution falls slightly because fewer missions remain in the “no shared event” state, while the
total still rises.

Reset. Next increase only `qA` while `qS` and `qB` stay fixed. The shared contribution does not move.
The dual-pump contribution rises in proportion to fixed `qB`; pump A still cannot reach the top
without pump B when the supply remains healthy.

## Deliberately broken case

Replace the redundant-pump AND gate with OR:

```text
broken: T = S OR A OR B.
```

At the baseline this gives `0.19405`, more than ten times the correct `0.01495`. The stronger
diagnostic is logical, not just numerical: state `S=0, A=1, B=0` falsely activates the broken top
event even though pump B can still provide cooling.

## Common misconceptions to correct directly

- OR is not generally arithmetic addition; event overlap must be handled.
- AND means every named event in that branch occurs within the mission, not necessarily at the
  same instant.
- Gate logic and statistical independence are separate claims.
- A minimal cut set is a sufficient event combination, not a mutually exclusive root-cause label.
- Repeating the same shared event in a diagram does not create independent copies.
- A fault tree is a static model of how defined events reach a defined top event. It does not prove
  an observed root cause or represent repair and event sequence by itself.

## Completion standard

The learner can state the boundary, events, gates, cut sets, probability assumptions, and units;
explain both isolated lever sweeps; reject the broken OR gate using a Boolean state; pass
`run_checks.m`; and give a two-sentence mechanism-first teach-back.
