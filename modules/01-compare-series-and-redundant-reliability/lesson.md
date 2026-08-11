# Lesson: Compare Series and Redundant Reliability

## Guiding question

How do required functions, redundancy, and common causes determine mission reliability?

## Mental model

A series system fails when any required component fails. Redundancy changes the logic from 'all must work' toward 'at least one must work,' but common-cause failures can defeat that benefit.

## What to manipulate

Use `interactive.m`. Change one lever at a time before combining effects.

## First observation

Add required series components and watch mission reliability fall. Add redundant channels and watch it rise, then introduce common-cause probability and see the apparent redundancy gain collapse.

## Common mistakes

- Adding hardware can reduce system reliability when every added component is required.
- Redundancy is not independent when channels share power, software, environment, or design defects.
- High component reliability does not automatically imply high mission reliability for a long chain.

## Completion standard

The learner can explain the baseline, identify what each lever changes, diagnose the deliberately broken case, and pass `run_checks.m`.
