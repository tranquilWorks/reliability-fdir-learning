# P04 walkthrough: Expose Common-Cause Failure

1. Read the guiding question: What inputs, observable effects, and failure modes matter when you expose Common-Cause Failure?
2. Recall that P03 availability included repair. State why P04 uses no-repair mission reliability
   to isolate dependence between redundant channels.
3. Predict whether six channels drive mission failure probability to zero when `beta=0.05`.
4. Run only the reliability-baseline section of `experiment.m`. Read time in hours, reliability,
   marginal channel hazard, beta, channel count, and endpoint metrics.
5. Advance once to the failure-mode section. Verify visually that the shared-event and
   no-shared-event/all-independent terms add to total system failure probability.
6. Run sweep 1. Increase only beta and observe higher system failure probability even though the
   one-channel marginal reliability remains unchanged. Explain the changed joint dependence.
7. Return to baseline, then run sweep 2. Increase only channel count. Identify which endpoint term
   falls and which term is unchanged at the fixed 1000-hour mission.
8. Open `interactive.m`. Move one control at a time. Switch from reliability comparison to the
   failure-mode decomposition only after explaining the first view.
9. Run the deliberately broken section. Diagnose the independence assumption when the nominal
   six-channel estimate is more than 1000 times smaller than correct failure probability.
10. Run `run_checks.m` in MATLAB when a MATLAB runtime is available, then answer the interpretation
    prompts in `checks.md` one at a time.
11. Teach back in two sentences: first connect `lambda`, beta, channel count, and mission time to
    both failure terms; second explain why equal marginals do not prove independence.

The notebook sections expose one transition at a time. Static repository checks do not substitute
for executing the figures, controls, or numerical assertions in MATLAB.
