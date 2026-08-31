%% P02 - Relate Hazard Rate to Survival
% Guiding question:
% What inputs, observable effects, and failure modes matter when you relate
% Hazard Rate to Survival?

%% Read the mechanism before touching a control
disp('Hazard is the conditional failure rate among items still surviving.');
disp(['Cumulative hazard H(t) is exposure accumulated over time; survival ' ...
    'is S(t)=exp(-H(t)).']);
disp(['P01 used exp(-lambda*t) for a component. That is this same rule with ' ...
    'a constant hazard rate.']);

%% Make one prediction before the baseline
disp(['Prediction: if hazard becomes four times larger after 1000 h, which ' ...
    'part of the survival curve can change?']);
disp('Run experiment.m one %% section at a time: baseline, first lever, second lever, then broken case.');

%% Open the live controls after observing the baseline
disp(['In interactive.m, reset before each comparison. Move baseline hazard ' ...
    'first; then reset and move only the post-change multiplier.']);
interactive;

%% Explain and teach back
disp(['Mechanism first: lambda(t) changes the rate at which H(t) accumulates; ' ...
    'H(t) changes S(t) through exp(-H(t)).']);
disp(['Teach back in two sentences: name the inputs and units, then explain ' ...
    'the negative-probability symptom of the broken 1-H approximation.']);
