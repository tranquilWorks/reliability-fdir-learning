# P06 lesson: Run an FMEA

## Guiding question

What inputs, observable effects, and failure modes matter when you run an FMEA?

## Start from P05, not from a rating formula

P05 asked a top-down question: which combinations of `S`, `A`, and `B` make cooling unavailable?
P06 asks the complementary bottom-up question: if one item fails one required function while the
other items remain available, what happens locally, what propagates upward, what reaches the mission,
and what evidence could reveal it?

The boundary stays fixed: a two-pump cooling function over one 1000-hour no-repair mission. The
three rows reuse P05's shared supply, Pump A, and Pump B events. P06 does not recompute
`S OR (A AND B)`. Its effect columns trace each mode separately under the row-under-analysis premise:
only that mode is present and companion items are available. That is why one pump row says redundancy
is lost while the companion pump continues cooling.

## Mental model: write one complete causal row

Begin with the required function. A failure mode says how that function fails; it is not an end
effect, a vague component name, or a guessed root cause. Then trace forward:

```text
item / required function → failure mode → local effect
                         → next-higher effect → end effect
```

Add an example cause to show why the mode might occur. Add prevention controls that act on the
cause or occurrence, then name the observable effect and detection control that can reveal an
occurrence. Those columns answer different questions and should not be swapped.

The bounded worksheet contains:

- `S`: shared supply output absent; the bus is de-energized, both pumps stop, and cooling is lost;
- `A`: Pump A delivers no flow on demand; with Pump B available, Pump B carries the load and
  redundancy is lost;
- `B`: Pump B delivers no flow on demand; with Pump A available, Pump A carries the load and
  redundancy is lost.

Consequence classes are categorical. P06 does not multiply consequence, occurrence, and detection
labels into an RPN. P08 owns the later question of quantitative prioritization.

## Occurrence and observability are separate inputs

For row `i`, `q_i` is the synthetic probability that the mode occurs during the fixed mission. The
detection coverage is conditional:

```text
c_i = P(indicator annunciates | mode i occurs)
```

Therefore the chain rule gives

```text
detected_i = q_i*c_i
latent_i   = q_i*(1-c_i)
q_i        = detected_i + latent_i.
```

No independence assumption is needed for this partition. At the baseline
`q=[0.005,0.10,0.10]` and `c=[0.98,0.70,0.90]`, detected occurrence is
`[0.0049,0.0700,0.0900]` and latent occurrence is `[0.0001,0.0300,0.0100]`.

The row sums are expected counts: `0.2050` listed mode occurrences per mission, split into `0.1649`
detected and `0.0401` latent. They are not the probability of at least one system event. Rows can
co-occur, but the effect text still describes one row at a time with companion items available.
P05's gate logic—not an FMEA column sum—defines combined cooling-loss effects.

## Observe one transition at a time

Make one prediction: if the Pump-A indicator misses a failure, has that physical failure mode
disappeared? Inspect the worksheet first, then view the detected/latent partition.

First increase only Pump-A occurrence `qA` while its coverage stays `0.70`. Both the detected
portion `0.70*qA` and latent portion `0.30*qA` grow. The cause/effect chain and every other row stay
unchanged.

Reset. Next increase only Pump-A coverage `cA` while `qA` stays `0.10`. Detected occurrence rises
and latent occurrence falls by the same amount. Their sum stays `0.10`, because better observation
does not prevent the bearing seizure in this model.

## Deliberately broken case

Build the worksheet only from oracle-filtered detector records. To isolate the completeness error,
grant the broken analysis one true-positive record per detected occurrence, perfect specificity, and
unique mode attribution:

```text
broken reported occurrence = detected occurrence.
```

Even under that favorable logging premise, the analysis silently assumes every relevant occurrence
annunciates. At `qA=0.10` and `cA=0`, the broken inventory reports zero Pump-A occurrence while the
correct analysis retains `0.10` entirely in the latent path. Across a coverage sweep, the broken
reported occurrence rises when the detector improves even though the physical occurrence input never
changes. Raw logs are harder: false alarms, duplicate records, or non-specific indicators can also
overcount or misattribute modes, and this bounded counterexample does not model them.

The symptom reveals the category error: missing evidence has been treated as evidence of absence.
FMEA must use functional analysis, plausible modes, causes, and controls—not only the failures an
existing monitor happened to record.

## Common misconceptions to correct directly

- A failure mode is how an item fails a function; an end effect is what that failure ultimately does.
- A cause precedes the mode. An observable effect is evidence after the mode occurs.
- Detection coverage does not reduce physical occurrence unless a separate prevention mechanism is
  modeled and justified.
- `q*c` is a conditional chain-rule product, not an independence claim.
- Summed row probabilities are expected counts, not a union probability or a fault-tree result.
- FMEA row effects assume the named mode alone with companion items available; use P05's logic for
  combined-event effects.
- A high-coverage detector can still leave a nonzero latent path; a log cannot prove completeness.
- An FMEA is prospective analysis. It does not prove the root cause of an observed incident.

## Completion standard

The learner can define the boundary; distinguish function, mode, cause, effects, observable, and
controls; explain both isolated sweeps; reject the detected-log-only inventory; connect the rows
back to P05 without combining them incorrectly; pass `run_checks.m`; and give a two-sentence,
mechanism-first teach-back without referring to MATLAB syntax.
