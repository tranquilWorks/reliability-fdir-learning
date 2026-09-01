%% P09 - Generate a Diagnostic Residual
% Guiding question:
% What inputs, observable effects, and failure modes matter when you
% generate a Diagnostic Residual?

%% Read the physical boundary before subtracting two signals
% P08 ranked a Pump-A-only degraded-success scenario. P09 monitors Pump A
% with normalized speed command u(t) and measured cooling flow y(t). The
% nominal predictor sees the same known command:
%
%       y_hat(t|u) = K_hat*u(t)
%       r(t)       = y(t)-y_hat(t|u)
%
% Residual r has units L/min. A negative value means less measured flow
% than the command-conditioned prediction. The injected loss below is a
% conditional magnitude, not P08's probability q_A.
baseline = model(0.20,10,0.10);

%% Baseline view 1 - compare measured flow with the input-conditioned prediction
flowFigure = figure('Name','P09 baseline: measured and predicted Pump-A flow');
flowAxes = axes('Parent',flowFigure);
plot(flowAxes,baseline.timeSeconds,baseline.measuredFlowLpm, ...
    'LineWidth',1.5,'DisplayName','Measured flow y');
hold(flowAxes,'on');
plot(flowAxes,baseline.timeSeconds,baseline.predictedFlowLpm,'--', ...
    'LineWidth',1.7,'DisplayName','Predicted flow y-hat(u)');
xline(flowAxes,baseline.commandStepTimeSeconds,':', ...
    'Command 0.5 to 0.8','LabelVerticalAlignment','bottom');
xline(flowAxes,baseline.faultTimeSeconds,':','20% loss injected', ...
    'LabelVerticalAlignment','bottom');
hold(flowAxes,'off'); grid(flowAxes,'on');
xlabel(flowAxes,'Time (s)');
ylabel(flowAxes,'Pump-A cooling flow (L/min)');
title(flowAxes,'Known command explains the normal flow change');
legend(flowAxes,'Location','best'); ylim(flowAxes,[0 9]);
fprintf(['Baseline: command changes at %.1f s and a %.0f%% conditional ' ...
    'effectiveness loss begins at %.1f s.\n'], ...
    baseline.commandStepTimeSeconds,100*baseline.effectivenessLossFraction, ...
    baseline.faultTimeSeconds);
disp(['Observe the measured and predicted traces move together at 10 s. ' ...
    'After 20 s, measured flow falls below the prediction for the same command.']);

%% Baseline view 2 - generate the signed residual
residualFigure = figure('Name','P09 baseline: diagnostic residual');
residualAxes = axes('Parent',residualFigure);
plot(residualAxes,baseline.timeSeconds,baseline.residualLpm, ...
    'LineWidth',1.6,'DisplayName','r = y-y-hat(u)');
hold(residualAxes,'on');
yline(residualAxes,0,'k:','Zero discrepancy','HandleVisibility','off');
xline(residualAxes,baseline.commandStepTimeSeconds,':', ...
    'Normal command change','HandleVisibility','off');
xline(residualAxes,baseline.faultTimeSeconds,':','Loss injected', ...
    'HandleVisibility','off');
hold(residualAxes,'off'); grid(residualAxes,'on');
xlabel(residualAxes,'Time (s)');
ylabel(residualAxes,'Diagnostic residual r = y-y-hat (L/min)');
title(residualAxes,'Matched prediction rejects command and exposes flow loss');
ylim(residualAxes,[-1.9 0.3]); legend(residualAxes,'Location','best');
fprintf(['Healthy high-command mean = %.4f L/min; post-fault mean = ' ...
    '%.4f L/min; fault-induced shift = %.4f L/min.\n'], ...
    baseline.highCommandHealthyMeanResidualLpm, ...
    baseline.postFaultMeanResidualLpm,baseline.faultResidualChangeLpm);
disp(['Mechanism: subtraction removes the expected command-driven flow. ' ...
    'The remaining negative mean is the modeled effectiveness-loss signature; ' ...
    'the small periodic part is deterministic teaching ripple.']);

%% Baseline view 3 - audit the residual decomposition
decompositionFigure = figure('Name','P09 baseline: residual decomposition');
decompositionAxes = axes('Parent',decompositionFigure);
plot(decompositionAxes,baseline.timeSeconds, ...
    baseline.modelMismatchResidualLpm,'LineWidth',1.3, ...
    'DisplayName','Model mismatch');
hold(decompositionAxes,'on');
plot(decompositionAxes,baseline.timeSeconds,baseline.faultResidualLpm, ...
    'LineWidth',1.3,'DisplayName','Effectiveness loss');
plot(decompositionAxes,baseline.timeSeconds, ...
    baseline.deterministicRippleLpm,'LineWidth',1.3, ...
    'DisplayName','Deterministic ripple');
plot(decompositionAxes,baseline.timeSeconds,baseline.residualLpm,'k--', ...
    'LineWidth',1.6,'DisplayName','Sum = residual');
hold(decompositionAxes,'off'); grid(decompositionAxes,'on');
xlabel(decompositionAxes,'Time (s)');
ylabel(decompositionAxes,'Residual contribution (L/min)');
title(decompositionAxes,'Residual is fault + model mismatch + ripple');
legend(decompositionAxes,'Location','best'); ylim(decompositionAxes,[-1.9 0.3]);
fprintf('Maximum decomposition closure error = %.3g L/min.\n', ...
    baseline.maxAbsResidualDecompositionErrorLpm);

%% Sweep 1 - change only conditional effectiveness loss
effectivenessLossSweep = [0 0.05 0.10 0.20 0.30];
postFaultMeanSweepLpm = zeros(size(effectivenessLossSweep));
faultShiftSweepLpm = zeros(size(effectivenessLossSweep));
healthyMeanSweepLpm = zeros(size(effectivenessLossSweep));
for k = 1:numel(effectivenessLossSweep)
    changed = model(effectivenessLossSweep(k),10,0.10);
    postFaultMeanSweepLpm(k) = changed.postFaultMeanResidualLpm;
    faultShiftSweepLpm(k) = changed.faultResidualChangeLpm;
    healthyMeanSweepLpm(k) = changed.highCommandHealthyMeanResidualLpm;
end
lossSweepFigure = figure('Name','P09 sweep 1: Pump-A effectiveness loss');
lossSweepAxes = axes('Parent',lossSweepFigure);
plot(lossSweepAxes,100*effectivenessLossSweep,postFaultMeanSweepLpm, ...
    'o-','LineWidth',1.6,'MarkerFaceColor',[0.1 0.45 0.8]);
grid(lossSweepAxes,'on');
xlabel(lossSweepAxes,'Conditional Pump-A effectiveness loss after injection (%)');
ylabel(lossSweepAxes,'Post-fault mean diagnostic residual (L/min)');
title(lossSweepAxes,'More conditional flow loss makes the signed residual more negative');
fprintf(['Loss sweep post-fault means = [%.1f %.1f %.1f %.1f %.1f] ' ...
    'L/min; healthy means remain within %.3g L/min of zero.\n'], ...
    postFaultMeanSweepLpm(1),postFaultMeanSweepLpm(2), ...
    postFaultMeanSweepLpm(3),postFaultMeanSweepLpm(4), ...
    postFaultMeanSweepLpm(5),max(abs(healthyMeanSweepLpm)));
disp(['Only the conditional loss changed. Command, predictor gain, ripple, ' ...
    'and every pre-fault measurement remain fixed.']);

%% Sweep 2 - reset loss, then change only predictor gain
predictorGainSweepLpmPerCommand = [8 9 10 11 12];
healthyHighMeanSweepLpm = zeros(size(predictorGainSweepLpmPerCommand));
postFaultGainSweepLpm = zeros(size(predictorGainSweepLpmPerCommand));
faultShiftGainSweepLpm = zeros(size(predictorGainSweepLpmPerCommand));
for k = 1:numel(predictorGainSweepLpmPerCommand)
    changed = model(0.20,predictorGainSweepLpmPerCommand(k),0.10);
    healthyHighMeanSweepLpm(k) = ...
        changed.highCommandHealthyMeanResidualLpm;
    postFaultGainSweepLpm(k) = changed.postFaultMeanResidualLpm;
    faultShiftGainSweepLpm(k) = changed.faultResidualChangeLpm;
end
gainSweepFigure = figure('Name','P09 sweep 2: predictor gain mismatch');
gainSweepAxes = axes('Parent',gainSweepFigure);
plot(gainSweepAxes,predictorGainSweepLpmPerCommand, ...
    healthyHighMeanSweepLpm,'o-','LineWidth',1.5, ...
    'DisplayName','Healthy high-command mean');
hold(gainSweepAxes,'on');
plot(gainSweepAxes,predictorGainSweepLpmPerCommand, ...
    postFaultGainSweepLpm,'s-','LineWidth',1.5, ...
    'DisplayName','Post-fault mean');
yline(gainSweepAxes,0,'k:','Zero discrepancy','HandleVisibility','off');
hold(gainSweepAxes,'off'); grid(gainSweepAxes,'on');
xlabel(gainSweepAxes,'Predictor gain K-hat (L/min per normalized command)');
ylabel(gainSweepAxes,'Reference-window mean residual (L/min)');
title(gainSweepAxes,'Model mismatch can create or cancel a residual mean');
legend(gainSweepAxes,'Location','best');
fprintf(['Gain sweep healthy means = [%.1f %.1f %.1f %.1f %.1f] ' ...
    'L/min; every fault-induced shift = %.1f L/min.\n'], ...
    healthyHighMeanSweepLpm(1),healthyHighMeanSweepLpm(2), ...
    healthyHighMeanSweepLpm(3),healthyHighMeanSweepLpm(4), ...
    healthyHighMeanSweepLpm(5),faultShiftGainSweepLpm(1));
disp(['At K-hat = 8, predictor mismatch cancels the post-fault mean at the ' ...
    'high command. Zero residual at one operating point is not proof of health.']);

%% Deliberately broken case - omit the known command from the predictor
brokenCase = model(0,10,0.10);
brokenFigure = figure('Name','P09 broken case: constant prediction');
brokenAxes = axes('Parent',brokenFigure);
plot(brokenAxes,brokenCase.timeSeconds,brokenCase.residualLpm, ...
    'LineWidth',1.5,'DisplayName','Correct r = y-y-hat(u)');
hold(brokenAxes,'on');
plot(brokenAxes,brokenCase.timeSeconds,brokenCase.brokenResidualLpm,'--', ...
    'LineWidth',1.5,'DisplayName','Broken r: command omitted');
xline(brokenAxes,brokenCase.commandStepTimeSeconds,':', ...
    'Normal command change','HandleVisibility','off');
yline(brokenAxes,0,'k:','','HandleVisibility','off');
hold(brokenAxes,'off'); grid(brokenAxes,'on');
xlabel(brokenAxes,'Time (s)');
ylabel(brokenAxes,'Diagnostic residual (L/min)');
title(brokenAxes,'A frozen prediction turns a normal command into a false signature');
legend(brokenAxes,'Location','best'); ylim(brokenAxes,[-0.3 3.3]);
fprintf(['Correct command-step residual change = %.4f L/min; broken change = ' ...
    '%.4f L/min.\n'],brokenCase.commandStepResidualChangeLpm, ...
    brokenCase.brokenCommandStepResidualChangeLpm);
disp(['Violated assumption: the nominal predictor must condition on every ' ...
    'known input that materially drives the observable. A discrepancy is ' ...
    'not a fault-specific alarm; P10 adds threshold tradeoffs and P11 asks ' ...
    'whether competing faults can be isolated.']);
