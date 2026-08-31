%% P02 - Relate Hazard Rate to Survival
% Guiding question:
% What inputs, observable effects, and failure modes matter when you relate
% Hazard Rate to Survival?

%% Read, then visualize the deterministic baseline
% Hazard lambda(t) is a conditional failure rate with units of 1/hour.
% Its accumulated exposure is H(t) = integral_0^t lambda(u) du, so the
% surviving fraction is S(t) = exp(-H(t)). P01's exp(-lambda*t) component
% reliability is the special case where lambda never changes. This lesson
% assumes a nonrepairable population with a known common hazard history.
baseline = model(2e-4,1,1000,3000,601);

figure('Name','P02 baseline: hazard creates survival loss');
subplot(2,1,1);
stairs(baseline.timeHours,baseline.hazardPerHour,'LineWidth',1.4);
grid on; xlabel('Mission time (h)'); ylabel('Hazard rate (failures/h)');
title('Baseline input: constant conditional failure rate');
subplot(2,1,2);
plot(baseline.timeHours,baseline.survivalProbability,'LineWidth',1.4, ...
    'DisplayName','Survival S(t)'); hold on;
plot(baseline.timeHours,baseline.failureProbability,'--','LineWidth',1.2, ...
    'DisplayName','Failure probability 1-S(t)'); hold off;
grid on; ylim([0 1.02]); xlabel('Mission time (h)'); ylabel('Probability');
title('Observable effect: survival falls as hazard accumulates');
legend('Location','best');

fprintf(['Baseline metrics: lambda = %.4g /h, H(T) = %.4f, ' ...
    'S(T) = %.6f, expected survivors = %.1f per 1000\n'], ...
    baseline.baseHazardPerHour,baseline.missionCumulativeHazard, ...
    baseline.missionSurvival,baseline.expectedSurvivorsPerThousand);

%% Sweep 1 - move only the baseline hazard-rate lever
baseHazardSweepPerHour = [1e-4 2e-4 5e-4];
figure('Name','P02 sweep 1: baseline hazard rate'); hold on; grid on;
for k = 1:numel(baseHazardSweepPerHour)
    changed = model(baseHazardSweepPerHour(k),1,1000,3000,601);
    plot(changed.timeHours,changed.survivalProbability,'LineWidth',1.3, ...
        'DisplayName',sprintf('lambda_0 = %.1g /h',baseHazardSweepPerHour(k)));
end
xlabel('Mission time (h)'); ylabel('Survival probability S(t)');
title('Higher hazard accumulates exposure faster'); ylim([0 1.02]);
legend('Location','best');
disp('Mechanism: increasing lambda_0 steepens H(t), so exp(-H(t)) falls sooner.');

%% Sweep 2 - reset, then move only the post-change multiplier
postChangeMultiplierSweep = [0.25 1 4];
changeTimeHours = 1000;
figure('Name','P02 sweep 2: operating-condition change'); hold on; grid on;
for k = 1:numel(postChangeMultiplierSweep)
    changed = model(2e-4,postChangeMultiplierSweep(k),changeTimeHours,3000,601);
    plot(changed.timeHours,changed.survivalProbability,'LineWidth',1.3, ...
        'DisplayName',sprintf('post-change multiplier = %.2g', ...
        postChangeMultiplierSweep(k)));
end
plot([changeTimeHours changeTimeHours],[0 1],'k:','LineWidth',1.1, ...
    'DisplayName','condition changes');
xlabel('Mission time (h)'); ylabel('Survival probability S(t)');
title('A later hazard change bends the survival curve'); ylim([0 1.02]);
legend('Location','best');
disp(['Mechanism: only exposure after 1000 h changes; the curves share the ' ...
    'same history before that time, and survival remains continuous at the change.']);

%% Deliberately broken case - extend S approximately equal to 1-H too far
brokenCase = model(1e-3,3,500,2000,601);
linearSurvival = 1-brokenCase.cumulativeHazard;
firstInvalidIndex = find(linearSurvival < 0,1,'first');

figure('Name','P02 broken case: invalid linear survival');
plot(brokenCase.timeHours,brokenCase.survivalProbability,'LineWidth',1.4, ...
    'DisplayName','Correct: exp(-H)'); hold on;
plot(brokenCase.timeHours,linearSurvival,'--','LineWidth',1.4, ...
    'DisplayName','Broken: 1-H');
plot(brokenCase.timeHours,[0*brokenCase.timeHours],'k:','HandleVisibility','off');
hold off; grid on; xlabel('Mission time (h)'); ylabel('Claimed survival probability');
title('Broken assumption: a small-exposure approximation is not a survival law');
legend('Location','best');

fprintf(['Broken-case symptom: 1-H first becomes negative at %.1f h, ' ...
    'while exp(-H) remains %.6f at mission end.\n'], ...
    brokenCase.timeHours(firstInvalidIndex),brokenCase.missionSurvival);
assert(any(linearSurvival < 0),'The deliberately broken approximation should cross below zero.');
assert(all(brokenCase.survivalProbability >= 0 & ...
    brokenCase.survivalProbability <= 1),'Exact survival must remain a probability.');
