# P07 walkthrough: Construct a Reliability Block Diagram

1. Read the guiding question: What inputs, observable effects, and failure modes matter when you construct a Reliability Block Diagram?
2. Recall P06's fixed 1000-hour, no-repair FMEA rows `S`, `A`, and `B`. Turn each failure mode into
   the required-function success statement that belongs in an RBD block.
3. State the success boundary before drawing: cooling succeeds when the shared supply works and at
   least one pump carries the load. Also state that quantification assumes independent `S`, `A`, and
   `B` block events.
4. Make one prediction: should the one physical supply appear once before the split or once inside
   each pump branch?
5. Run only the baseline topology section of `experiment.m`. Trace minimal success paths `S-A` and
   `S-B`; explain why the supply is series and the pumps are parallel without referring to geometry.
6. Advance once to the disjoint outcome ledger. Verify that the five outcomes sum to one, the last
   three success outcomes sum to `0.98505`, and the two failure outcomes sum to P05's `0.01495`.
7. Compare the two minimal path probabilities with their shared `S-A-B` intersection. Explain why
   `0.89550+0.89550` is not a valid reliability and how inclusion-exclusion restores `0.98505`.
8. Run sweep 1. Change only shared-supply reliability and observe that the pump group stays `0.99`
   while every system success path moves.
9. Reset, then run sweep 2. Change only Pump-A reliability and observe that `R_S=0.995` and
   `R_B=0.90` remain fixed; explain why Pump A matters only when Pump B fails.
10. Open `interactive.m`. Select one view at a time, reproduce each lever transition, and use Reset
    baseline before comparing the two mechanisms.
11. Run the deliberately broken section. Diagnose why two drawings of the same supply do not create
    two independent supplies; compare correct `0.7920`, wrong `0.9216`, and impossible raw sum `1.44`.
12. Explain why P06 detection coverage is useful evidence but cannot enter the physical RBD without
    an explicit detection-and-recovery mechanism.
13. Run `run_checks.m` in MATLAB when a MATLAB runtime is available, answer `checks.md` one question
    at a time, and give the two-sentence teach-back.

Static repository checks do not substitute for executing the model, figures, controls, or numerical
assertions in MATLAB.
