%% P10 - Move a Fault Threshold
% Guiding question:
% What inputs, observable effects, and failure modes matter when you move a
% Fault Threshold?

%% Read the decision boundary inherited from P09
% P09 defined r(t)=y(t)-y_hat(t|u) in L/min. A Pump-A effectiveness loss is
% negative under that convention. P10 uses a nonnegative magnitude T and
% places the signed alarm boundary at -T:
%
%       alarm when r(t) <= -T.
%
% A threshold classifies evidence; it does not repair a poor residual,
% identify one root cause, estimate a posterior, or choose a recovery.
baseline = model(0.50,0.20,0.10);

%% Baseline view 1 - compare the residual with the signed threshold
residualFigure = figure('Name','P10 baseline: residual and signed threshold');
residualAxes = axes('Parent',residualFigure);
plot(residualAxes,baseline.timeSeconds,baseline.residualLpm, ...
    'LineWidth',1.6,'DisplayName','P09 residual r');
hold(residualAxes,'on');
plot(residualAxes,baseline.timeSeconds,baseline.signedThresholdLpm,'--', ...
    'LineWidth',1.6,'DisplayName','Signed threshold -T');
yline(residualAxes,0,'k:','Zero residual','HandleVisibility','off');
xline(residualAxes,baseline.faultTimeSeconds,':','Loss injected', ...
    'HandleVisibility','off');
hold(residualAxes,'off'); grid(residualAxes,'on');
xlabel(residualAxes,'Time (s)');
ylabel(residualAxes,'Diagnostic residual and threshold (L/min)');
title(residualAxes,'The residual must cross -T to become an alarm');
legend(residualAxes,'Location','best');
residualBounds = [baseline.residualLpm;baseline.signedThresholdLpm;0];
residualSpan = max([0.2 max(residualBounds)-min(residualBounds)]);
ylim(residualAxes,[min(residualBounds)-0.12*residualSpan ...
    max(residualBounds)+0.12*residualSpan]);
fprintf(['Baseline T = %.2f L/min: healthy mean %.4f L/min; ' ...
    'post-fault mean %.4f L/min.\n'],baseline.thresholdMagnitudeLpm, ...
    baseline.healthyMeanResidualLpm,baseline.postFaultMeanResidualLpm);
disp(['Observe the nuisance ripple stay above -T while the sustained ' ...
    'negative loss signature stays below it.']);

%% Baseline view 2 - inspect the resulting deterministic decision
alarmFigure = figure('Name','P10 baseline: threshold decision');
alarmAxes = axes('Parent',alarmFigure);
stairs(alarmAxes,baseline.timeSeconds,double(baseline.alarm), ...
    'LineWidth',1.6,'DisplayName','Alarm state');
hold(alarmAxes,'on');
xline(alarmAxes,baseline.faultTimeSeconds,':','Loss injected', ...
    'HandleVisibility','off');
hold(alarmAxes,'off'); grid(alarmAxes,'on');
xlabel(alarmAxes,'Time (s)'); ylabel(alarmAxes,'Alarm state (0 or 1)');
title(alarmAxes,'Baseline threshold rejects ripple and detects the loss');
ylim(alarmAxes,[-0.1 1.1]); yticks(alarmAxes,[0 1]);
yticklabels(alarmAxes,{'clear','alarm'});
fprintf(['Reference-window counts: TN=%d, FP=%d, detected=%d, missed=%d; ' ...
    'false-alarm fraction=%.2f, detection fraction=%.2f.\n'], ...
    baseline.trueNegativeCount,baseline.falseAlarmCount, ...
    baseline.detectionCount,baseline.missedDetectionCount, ...
    baseline.falseAlarmSampleFraction,baseline.detectionSampleFraction);
disp(['These are fractions of two fixed synthetic 60-sample windows, not ' ...
    'field false-alarm or detection probabilities.']);

%% Sweep 1 - move only the threshold magnitude
thresholdSweepLpm = [0.06 0.12 0.50 1.49 1.56 1.72];
falseAlarmThresholdSweep = zeros(size(thresholdSweepLpm));
detectionThresholdSweep = zeros(size(thresholdSweepLpm));
for k = 1:numel(thresholdSweepLpm)
    changed = model(thresholdSweepLpm(k),0.20,0.10);
    falseAlarmThresholdSweep(k) = changed.falseAlarmSampleFraction;
    detectionThresholdSweep(k) = changed.detectionSampleFraction;
end
thresholdFigure = figure('Name','P10 sweep 1: threshold tradeoff');
thresholdAxes = axes('Parent',thresholdFigure);
plot(thresholdAxes,thresholdSweepLpm,falseAlarmThresholdSweep,'o-', ...
    'LineWidth',1.6,'DisplayName','Healthy false-alarm fraction');
hold(thresholdAxes,'on');
plot(thresholdAxes,thresholdSweepLpm,detectionThresholdSweep,'s-', ...
    'LineWidth',1.6,'DisplayName','Fault detection fraction');
hold(thresholdAxes,'off'); grid(thresholdAxes,'on');
xlabel(thresholdAxes,'Threshold magnitude T (L/min)');
ylabel(thresholdAxes,'Alarmed reference-window sample fraction (0 to 1)');
title(thresholdAxes,'Raising T rejects nuisance but eventually misses the fault');
legend(thresholdAxes,'Location','best'); ylim(thresholdAxes,[-0.05 1.05]);
fprintf(['Threshold sweep false-alarm fractions = [%.2f %.2f %.2f %.2f ' ...
    '%.2f %.2f]; detection fractions = [%.2f %.2f %.2f %.2f %.2f %.2f].\n'], ...
    falseAlarmThresholdSweep(1),falseAlarmThresholdSweep(2), ...
    falseAlarmThresholdSweep(3),falseAlarmThresholdSweep(4), ...
    falseAlarmThresholdSweep(5),falseAlarmThresholdSweep(6), ...
    detectionThresholdSweep(1),detectionThresholdSweep(2), ...
    detectionThresholdSweep(3),detectionThresholdSweep(4), ...
    detectionThresholdSweep(5),detectionThresholdSweep(6));
disp(['Only T moved. The residual, command, physical loss, ripple, and ' ...
    'reference windows remained identical.']);

%% Sweep 2 - reset T, then change only conditional fault magnitude
lossSweep = [0 0.04 0.06 0.08 0.20];
falseAlarmLossSweep = zeros(size(lossSweep));
detectionLossSweep = zeros(size(lossSweep));
postFaultMeanLossSweepLpm = zeros(size(lossSweep));
for k = 1:numel(lossSweep)
    changed = model(0.50,lossSweep(k),0.10);
    falseAlarmLossSweep(k) = changed.falseAlarmSampleFraction;
    detectionLossSweep(k) = changed.detectionSampleFraction;
    postFaultMeanLossSweepLpm(k) = changed.postFaultMeanResidualLpm;
end
lossFigure = figure('Name','P10 sweep 2: conditional loss magnitude');
lossAxes = axes('Parent',lossFigure);
plot(lossAxes,100*lossSweep,detectionLossSweep,'o-', ...
    'LineWidth',1.6,'DisplayName','Fault detection fraction');
hold(lossAxes,'on');
plot(lossAxes,100*lossSweep,falseAlarmLossSweep,'s--', ...
    'LineWidth',1.4,'DisplayName','Healthy false-alarm fraction');
hold(lossAxes,'off'); grid(lossAxes,'on');
xlabel(lossAxes,'Conditional Pump-A effectiveness loss (%)');
ylabel(lossAxes,'Alarmed reference-window sample fraction (0 to 1)');
title(lossAxes,'A fixed threshold misses losses whose residual is too small');
legend(lossAxes,'Location','best'); ylim(lossAxes,[-0.05 1.05]);
fprintf(['Loss sweep post-fault means = [%.2f %.2f %.2f %.2f %.2f] ' ...
    'L/min; detection fractions = [%.2f %.2f %.2f %.2f %.2f].\n'], ...
    postFaultMeanLossSweepLpm(1),postFaultMeanLossSweepLpm(2), ...
    postFaultMeanLossSweepLpm(3),postFaultMeanLossSweepLpm(4), ...
    postFaultMeanLossSweepLpm(5),detectionLossSweep(1), ...
    detectionLossSweep(2),detectionLossSweep(3), ...
    detectionLossSweep(4),detectionLossSweep(5));
disp(['Only conditional loss magnitude moved. The threshold, ripple, and ' ...
    'every healthy reference sample remained fixed.']);

%% Deliberately broken case - place the signed boundary on the wrong side
brokenCase = model(0.50,0.20,0.10);
brokenFigure = figure('Name','P10 broken case: wrong-sign threshold');
brokenAxes = axes('Parent',brokenFigure);
plot(brokenAxes,brokenCase.timeSeconds,brokenCase.residualLpm, ...
    'LineWidth',1.5,'DisplayName','Residual r');
hold(brokenAxes,'on');
plot(brokenAxes,brokenCase.timeSeconds,brokenCase.signedThresholdLpm,'--', ...
    'LineWidth',1.5,'DisplayName','Correct boundary -T');
plot(brokenAxes,brokenCase.timeSeconds, ...
    brokenCase.brokenSignedThresholdLpm,':','LineWidth',1.8, ...
    'DisplayName','Broken boundary +T');
hold(brokenAxes,'off'); grid(brokenAxes,'on');
xlabel(brokenAxes,'Time (s)');
ylabel(brokenAxes,'Diagnostic residual and threshold (L/min)');
title(brokenAxes,'Wrong sign makes ordinary healthy residuals alarm');
legend(brokenAxes,'Location','best');
brokenBounds = [brokenCase.residualLpm; ...
    brokenCase.signedThresholdLpm;brokenCase.brokenSignedThresholdLpm;0];
brokenSpan = max([0.2 max(brokenBounds)-min(brokenBounds)]);
ylim(brokenAxes,[min(brokenBounds)-0.12*brokenSpan ...
    max(brokenBounds)+0.12*brokenSpan]);
fprintf(['Correct healthy false-alarm fraction = %.2f; wrong-sign ' ...
    'fraction = %.2f.\n'],brokenCase.falseAlarmSampleFraction, ...
    brokenCase.brokenFalseAlarmSampleFraction);
disp(['Violated assumption: the signed boundary must preserve P09''s ' ...
    'negative loss-residual convention. Moving T cannot repair a sign error.']);
