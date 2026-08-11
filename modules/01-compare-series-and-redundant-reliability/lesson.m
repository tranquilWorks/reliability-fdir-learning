%% P01 - Compare Series and Redundant Reliability
% Guiding question:
% How do required functions, redundancy, and common causes determine mission reliability?
%
% Mental model:
% A series system fails when any required component fails. Redundancy changes the logic from 'all must work' toward 'at least one must work,' but common-cause failures can defeat that benefit.

%% Read the baseline lesson
disp('How do required functions, redundancy, and common causes determine mission reliability?');
disp('A series system fails when any required component fails. Redundancy changes the logic from ''all must work'' toward ''at least one must work,'' but common-cause failures can defeat that benefit.');

%% Run the deterministic experiment
experiment;

%% Open the live lever panel
% Move one control at a time and connect the visible change to the model.
interactive;
