%% P10 - Move a Fault Threshold
% Guiding question:
% What inputs, observable effects, and failure modes matter when you move a
% Fault Threshold?

%% Read the P09 sign convention before making a decision
disp(['P09 generated r=y-y-hat(u) in L/min. A Pump-A effectiveness loss ' ...
    'made that residual negative. P10 keeps the residual fixed and adds a ' ...
    'nonnegative threshold magnitude T at the signed boundary -T.']);
disp(['The transparent rule is alarm when r <= -T. Window alarm fractions ' ...
    'below are counts from a fixed synthetic record, not field ' ...
    'false-alarm or detection probabilities.']);

%% Make one prediction, then inspect the residual and boundary
disp(['Prediction: if T increases and moves -T farther below zero, which ' ...
    'error should eventually grow: healthy false alarms or missed fault samples?']);
baseline = model(0.50,0.20,0.10);
residualFigure = figure('Name','P10 lesson baseline: residual threshold');
residualAxes = axes('Parent',residualFigure);
plot(residualAxes,baseline.timeSeconds,baseline.residualLpm, ...
    'LineWidth',1.6,'DisplayName','P09 residual r');
hold(residualAxes,'on');
plot(residualAxes,baseline.timeSeconds,baseline.signedThresholdLpm,'--', ...
    'LineWidth',1.6,'DisplayName','Signed threshold -T');
yline(residualAxes,0,'k:','Zero residual','HandleVisibility','off');
xline(residualAxes,baseline.faultTimeSeconds,':','Loss injection', ...
    'HandleVisibility','off');
hold(residualAxes,'off'); grid(residualAxes,'on');
xlabel(residualAxes,'Time (s)');
ylabel(residualAxes,'Diagnostic residual and threshold (L/min)');
title(residualAxes,'A negative loss signature crosses the signed boundary');
legend(residualAxes,'Location','best');
values = [baseline.residualLpm;baseline.signedThresholdLpm;0];
span = max([0.2 max(values)-min(values)]);
ylim(residualAxes,[min(values)-0.12*span max(values)+0.12*span]);
disp(['Healthy ripple remains above -0.5 L/min. The 20% loss centers the ' ...
    'fault window at -1.6 L/min, below the boundary.']);

%% Advance once to the threshold decision
alarmFigure = figure('Name','P10 lesson baseline: alarm decision');
alarmAxes = axes('Parent',alarmFigure);
stairs(alarmAxes,baseline.timeSeconds,double(baseline.alarm),'LineWidth',1.6);
hold(alarmAxes,'on');
xline(alarmAxes,baseline.faultTimeSeconds,':','Loss injection');
hold(alarmAxes,'off'); grid(alarmAxes,'on');
xlabel(alarmAxes,'Time (s)'); ylabel(alarmAxes,'Alarm state (0 or 1)');
title(alarmAxes,'Baseline decision: nuisance clear, sustained loss alarmed');
ylim(alarmAxes,[-0.1 1.1]); yticks(alarmAxes,[0 1]);
yticklabels(alarmAxes,{'clear','alarm'});
fprintf(['Healthy FP/TN = %d/%d samples; fault detected/missed = %d/%d ' ...
    'samples.\n'],baseline.falseAlarmCount,baseline.trueNegativeCount, ...
    baseline.detectionCount,baseline.missedDetectionCount);

%% Move one lever, reset, then move the independent lever
disp(['Run experiment.m one section at a time. First move only T and keep ' ...
    'the residual identical. Observe the low-T nuisance alarms and the ' ...
    'high-T missed fault samples.']);
disp(['Reset T. Then move only conditional loss magnitude. The threshold ' ...
    'and every healthy sample stay fixed while the fault signature crosses ' ...
    'the boundary.']);
disp(['Show the wrong-sign +T broken case last. Moving a magnitude cannot ' ...
    'repair a comparator that discarded P09''s sign convention.']);
disp(['A threshold creates a detection decision. P11 adds competing-fault ' ...
    'isolation, P12 adds posterior reasoning, and later phases add response.']);
interactive;
