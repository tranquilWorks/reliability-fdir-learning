# P08 walkthrough: Prioritize Risk Quantitatively

1. Read the guiding question: What inputs, observable effects, and failure modes matter when you prioritize Risk Quantitatively?
2. Recall P06's `S`, `A`, and `B` modes and P07's fixed 1000-hour success logic. Explain why a
   single pump failure and a dual-pump failure are different scenarios even though they share a
   basic event.
3. State the quantification boundary: P07's independent basic-event assumption, four disjoint
   loss-bearing outcomes, and synthetic comparable consequences in kUSD per scenario occurrence.
   Distinguish the first two mission failures from the two degraded-success single-pump outcomes.
4. Make one prediction: must the rarest, highest-consequence scenario become first priority?
5. Run only baseline view 1 in `experiment.m`. Verify the five P07 outcome probabilities sum to one,
   identify which four carry loss, and recover mission failure `0.01495` and success `0.98505`.
6. Advance once to the probability-consequence plane. Point to occurrence on the horizontal axis,
   consequence on the vertical axis, and state why neither coordinate alone is a priority.
7. Advance once to expected-loss bars. Reproduce `[0.6000,0.9950,0.7164,1.0746]` kUSD per mission
   and the order A-only, A&B, B-only, S.
8. Run sweep 1. Change only `q_S`; observe the S contribution rise and every supply-up contribution
   fall slightly as probability reallocates between mutually exclusive states. Identify the exact
   S/A-only crossover at `q_S=0.0089197` and `0.01` as the first sampled point after it.
9. Reset. Run sweep 2 and change only A&B consequence. Verify its probability stays `0.00995`, all
   other risks stay fixed, and A&B crosses A-only at `108` kUSD per occurrence.
10. Open `interactive.m`. Reproduce one probability transition and one consequence transition,
    using Reset baseline between them and selecting one visible view at a time.
11. Run the deliberately broken section. Explain why occurrence categories `[2,2,5,5]` times
    severity categories `[5,5,2,2]` create an all-10 tie without a ratio-scale unit.
12. Explain why P06 detection coverage cannot lower these physical risks without an explicit
    detection-and-response mechanism, and why economic priority cannot waive a safety constraint.
13. Run `run_checks.m` in MATLAB when a MATLAB runtime is available, answer `checks.md` one question
    at a time, and give the two-sentence teach-back.

Static repository checks do not substitute for executing the model, figures, controls, or numerical
assertions in MATLAB.
