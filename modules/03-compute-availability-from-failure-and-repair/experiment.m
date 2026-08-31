%% P03 - Compute Availability from Failure and Repair
% Guiding question:
% What inputs, observable effects, and failure modes matter when you compute
% Availability from Failure and Repair?

%% Read, then visualize the deterministic baseline
% P02 used R(t)=exp(-lambda*t) for the probability of no failure yet. A
% repairable item can return from down to up, so point availability instead
% follows dA/dt = mu*(1-A)-lambda*A, where mu=1/MTTR. The baseline starts up.
baseline = model(1e-3,10,100,601,1);

figure('Name','P03 baseline: current state probability');
plot(baseline.timeHours,baseline.availabilityProbability,'LineWidth',1.4, ...
    'DisplayName','Available A(t)'); hold on;
plot(baseline.timeHours,baseline.unavailabilityProbability,'--','LineWidth',1.2, ...
    'DisplayName','Unavailable 1-A(t)'); hold off;
grid on; ylim([0 1.02]); xlabel('Time since observation starts (h)');
ylabel('State probability');
title('Observable state: availability relaxes toward a nonzero balance');
legend('Location','best');

fprintf(['Baseline metrics: lambda = %.4g /h, MTTR = %.1f h, mu = %.4g /h, ' ...
    'A_inf = %.6f, U_inf = %.6f, downtime = %.2f h/year, ' ...
    'A(T) = %.6f, time constant = %.2f h\n'], ...
    baseline.failureRatePerHour,baseline.meanRepairTimeHours, ...
    baseline.repairRatePerHour,baseline.steadyAvailability, ...
    baseline.steadyUnavailability,baseline.steadyExpectedDowntimeHoursPerYear, ...
    baseline.endpointAvailability,baseline.relaxationTimeHours);

%% Read the baseline mechanism in one complementary view
figure('Name','P03 baseline mechanism: probability flow');
plot(baseline.timeHours,baseline.failureTransitionFlowPerHour,'LineWidth',1.4, ...
    'DisplayName','Up to down: lambda A(t)'); hold on;
plot(baseline.timeHours,baseline.repairTransitionFlowPerHour,'--','LineWidth',1.4, ...
    'DisplayName','Down to up: mu[1-A(t)]'); hold off;
grid on; xlabel('Time since observation starts (h)');
ylabel('Expected transitions per hour');
title('Mechanism: failure and repair flows approach equality');
legend('Location','best');
disp(['Mechanism: the initially up item has failure flow but no repair flow. ' ...
    'As down-state probability accumulates, repair flow rises until the flows balance.']);

%% Sweep 1 - move only the failure-rate lever
failureRateSweepPerHour = [5e-4 1e-3 5e-3];
figure('Name','P03 sweep 1: failure rate'); hold on; grid on;
for k = 1:numel(failureRateSweepPerHour)
    changed = model(failureRateSweepPerHour(k),10,100,601,1);
    plot(changed.timeHours,changed.availabilityProbability,'LineWidth',1.3, ...
        'DisplayName',sprintf('lambda = %.1g /h',failureRateSweepPerHour(k)));
end
xlabel('Time since observation starts (h)');
ylabel('Point availability A(t)');
title('More frequent failures lower the up-state balance'); ylim([0.94 1.002]);
legend('Location','best');
disp(['Mechanism: MTTR stays at 10 h; increasing lambda sends probability ' ...
    'from up to down faster, so both A(t) and A_inf fall.']);

%% Sweep 2 - reset, then move only the mean-repair-time lever
meanRepairTimeSweepHours = [2 10 40];
steadyDowntimeHoursPerYear = zeros(size(meanRepairTimeSweepHours));
steadyAvailabilitySweep = zeros(size(meanRepairTimeSweepHours));
for k = 1:numel(meanRepairTimeSweepHours)
    changed = model(1e-3,meanRepairTimeSweepHours(k),100,601,1);
    steadyDowntimeHoursPerYear(k) = changed.steadyExpectedDowntimeHoursPerYear;
    steadyAvailabilitySweep(k) = changed.steadyAvailability;
end
figure('Name','P03 sweep 2: mean repair time');
plot(meanRepairTimeSweepHours,steadyDowntimeHoursPerYear,'o-','LineWidth',1.4, ...
    'MarkerFaceColor',[0.2 0.45 0.75]);
grid on; xlabel('Mean time to repair, MTTR (h)');
ylabel('Steady expected downtime (h/year)');
title('Slower repair converts the same failure rate into more downtime');
fprintf(['Repair sweep metrics: A_inf = [%.6f %.6f %.6f] for MTTR = ' ...
    '[%.0f %.0f %.0f] h\n'],steadyAvailabilitySweep(1), ...
    steadyAvailabilitySweep(2),steadyAvailabilitySweep(3), ...
    meanRepairTimeSweepHours(1),meanRepairTimeSweepHours(2), ...
    meanRepairTimeSweepHours(3));
disp(['Mechanism: lambda stays at 0.001 /h; a longer MTTR lowers mu, so ' ...
    'probability leaves the down state more slowly.']);

%% Deliberately broken case - label P02 survival as availability
brokenCase = model(1e-3,10,5000,1001,1);
brokenReliabilityAsAvailability = exp( ...
    -brokenCase.failureRatePerHour*brokenCase.timeHours);

figure('Name','P03 broken case: reliability is not repairable availability');
plot(brokenCase.timeHours,brokenCase.availabilityProbability,'LineWidth',1.4, ...
    'DisplayName','Correct: repairable A(t)'); hold on;
plot(brokenCase.timeHours,brokenReliabilityAsAvailability,'--','LineWidth',1.4, ...
    'DisplayName','Broken: exp(-lambda t) labeled availability'); hold off;
grid on; xlabel('Time since observation starts (h)'); ylabel('Claimed probability');
title('Broken assumption: a repaired item is treated as permanently failed');
legend('Location','best'); ylim([0 1.02]);

fprintf(['Broken-case symptom at 5000 h: no-first-failure reliability = %.6f, ' ...
    'but repairable point availability = %.6f.\n'], ...
    brokenReliabilityAsAvailability(end),brokenCase.endpointAvailability);
assert(brokenReliabilityAsAvailability(end) < 0.01, ...
    'The broken no-repair curve should decay close to zero.');
assert(brokenCase.endpointAvailability > 0.98, ...
    'The correct repairable availability should remain near its nonzero balance.');
