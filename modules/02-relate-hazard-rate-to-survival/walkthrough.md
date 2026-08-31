# P02 walkthrough: Relate Hazard Rate to Survival

1. Read the guiding question: What inputs, observable effects, and failure modes matter when you relate Hazard Rate to Survival?
2. Recall P01's component curve and state its hidden constant-hazard assumption.
3. Predict whether a hazard change at 1000 h can alter survival before 1000 h.
4. Run only the baseline section of `experiment.m`. Read the hazard axis in failures/hour, the time
   axis in hours, and survival as a probability. Record `H(T)` and `S(T)`.
5. Run sweep 1. Increase only baseline hazard and observe that the survival curve separates from
   time zero. Explain: cumulative hazard grows faster from the start.
6. Return to the baseline, then run sweep 2. Change only the post-change multiplier and observe that
   curves remain identical until 1000 h. Explain: their earlier accumulated exposure is identical.
7. Open `interactive.m`. Move one control at a time and use the displayed `H(T)` before describing
   the resulting `S(T)`.
8. Run the deliberately broken section. Identify the violated small-exposure assumption from the
   moment `1-H` crosses below zero; do not call the symptom a plotting error.
9. Run `run_checks.m` in MATLAB when a MATLAB runtime is available, then answer the interpretation
   prompts in `checks.md`.
10. Teach back in two sentences: first relate hazard to cumulative hazard and survival; second name
    why the broken approximation fails.

The notebook sections intentionally expose one plot transition at a time. Static repository checks
do not substitute for executing the figures, controls, or numerical assertions in MATLAB.
