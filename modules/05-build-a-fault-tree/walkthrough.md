# P05 walkthrough: Build a Fault Tree

1. Read the guiding question: What inputs, observable effects, and failure modes matter when you build a Fault Tree?
2. Recall P04's distinction between one shared event and channel-specific events. State why shared
   supply loss appears once as `S` in this tree.
3. Define the fixed 1000-hour no-repair mission boundary, top event, and basic events before using
   a probability.
4. Predict whether `S=0, A=1, B=0` activates correct loss of cooling.
5. Run only the tree-baseline section of `experiment.m`. Name the OR gate, AND gate, and minimal cut
   sets `{S}` and `{A,B}`.
6. Advance once to the non-overlapping contribution view. Verify that `0.005 + 0.00995 = 0.01495`
   per mission at the baseline.
7. Run sweep 1. Increase only `qS` and explain why the direct shared path rises while the
   no-shared/dual-pump contribution falls slightly.
8. Return to baseline, then run sweep 2. Increase only `qA`; explain why the shared contribution is
   unchanged and why fixed `qB` conditions pump A's effect through the AND gate.
9. Open `interactive.m`. Use the reset control between levers and show one view at a time.
10. Run the deliberately broken section. Diagnose the wrong OR gate from its false trigger for one
    failed pump, not just from its probability overstatement.
11. Run `run_checks.m` in MATLAB when a MATLAB runtime is available, then answer the interpretation
    prompts in `checks.md` one at a time.
12. Teach back in two sentences: first state the boundary, inputs, gates, cut sets, assumptions, and
    units; second explain both lever effects and the broken-gate symptom.

Static repository checks do not substitute for executing the figures, controls, or numerical
assertions in MATLAB.
