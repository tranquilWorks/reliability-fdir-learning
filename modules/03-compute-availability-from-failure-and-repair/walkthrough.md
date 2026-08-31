# P03 walkthrough: Compute Availability from Failure and Repair

1. Read the guiding question: What inputs, observable effects, and failure modes matter when you compute Availability from Failure and Repair?
2. Recall that P02 survival excludes an item after its first failure. State why current up/down
   status may differ after repair.
3. Predict whether steady downtime rises or falls if MTTR becomes four times longer while failure
   rate stays fixed.
4. Run only the state-baseline section of `experiment.m`. Read time in hours, state probability,
   `A_inf`, `A(T)`, and expected downtime hours/year.
5. Advance once to the transition-flow section. Read transitions/hour and explain why failure flow
   starts above repair flow before the two approach balance.
6. Run sweep 1. Increase only failure rate and observe the lower availability curve. Explain the
   change as stronger probability flow from up to down.
7. Return to baseline, then run sweep 2. Increase only MTTR and observe higher annual downtime.
   Explain that a longer duration means a smaller repair rate `mu=1/MTTR`.
8. Open `interactive.m`. Move one control at a time. Toggle the initial state and verify that it
   changes the transient direction but not the displayed steady balance. Switch the visible view
   from state occupancy to transition flow only after explaining the first view.
9. Run the deliberately broken section. Identify the missing repair transition when
   `exp(-lambda*t)` approaches zero but correct repairable availability stays near `A_inf`.
10. Run `run_checks.m` in MATLAB when a MATLAB runtime is available, then answer the interpretation
   prompts in `checks.md`.
11. Teach back in two sentences: first connect failure and repair inputs to availability; second
    distinguish current availability from P02's no-first-failure survival.

The notebook sections expose one transition at a time. Static repository checks do not substitute
for executing the figures, controls, or numerical assertions in MATLAB.
