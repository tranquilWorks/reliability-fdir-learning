%% P03 - Compute Availability from Failure and Repair
% Guiding question:
% What inputs, observable effects, and failure modes matter when you compute
% Availability from Failure and Repair?

%% Read the mechanism before touching a control
disp(['P02 survival measured whether the first failure had happened. ' ...
    'Availability measures whether a repairable item is up now.']);
disp(['Failure flow is lambda*A; repair flow is mu*(1-A), where ' ...
    'mu=1/MTTR. Their balance sets A_inf=mu/(lambda+mu).']);

%% Make one prediction before the baseline
disp(['Prediction: if lambda stays fixed but MTTR becomes four times longer, ' ...
    'will steady expected downtime rise or fall?']);
disp(['Run experiment.m one %% section at a time: baseline state, baseline ' ...
    'flow mechanism, first lever, second lever, then broken case.']);

%% Open the live controls after observing the baseline
disp(['In interactive.m, reset before each comparison. Move failure rate ' ...
    'first; then reset and move only MTTR. Switch the one-at-a-time view ' ...
    'from state occupancy to transition flow to explain A(t).']);
interactive;

%% Explain and teach back
disp(['Mechanism first: A(t) changes by repair flow into up minus failure ' ...
    'flow out of up; at steady state those flows are equal.']);
disp(['Teach back in two sentences: name lambda and MTTR with units, then ' ...
    'explain why exp(-lambda*t) is not repairable availability.']);
