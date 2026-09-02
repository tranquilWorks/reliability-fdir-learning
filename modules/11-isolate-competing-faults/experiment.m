%% P11 - Isolate Competing Faults
% Guiding question:
% What inputs, observable effects, and failure modes matter when you isolate
% Competing Faults?

%% Read the P10 detection boundary before adding a second residual
% P10 preserved r_Q=y_Q-y_Q_hat(u) in L/min and alarmed when r_Q<=-0.50.
% That detects a negative flow discrepancy, but Pump-A effectiveness loss
% and a negative flow-sensor bias can create the same flow residual. P11
% adds r_P=y_P-y_P_hat(u) in kPa. Under the declared synthetic sensitivity,
% pump loss affects flow and pressure while sensor bias affects flow only.
%
% Fixed-window tests form the dimensionless signature
%       s = [flow test, pressure test].
% Candidate signatures are healthy 00, pump loss 11, and sensor bias 10.
% A signature match is deterministic evidence, not a posterior probability.
healthy = model(0,0);
baseline = model(0.20,0);
competingFault = model(0,1.60);

%% Baseline view 1 - one P10 flow alarm, two possible causes
flowFigure = figure('Name','P11 baseline: competing flow signatures');
flowAxes = axes('Parent',flowFigure);
plot(flowAxes,baseline.timeSeconds,baseline.flowResidualLpm, ...
    'LineWidth',2.2,'DisplayName','20% Pump-A loss');
hold(flowAxes,'on');
plot(flowAxes,competingFault.timeSeconds,competingFault.flowResidualLpm,'--', ...
    'LineWidth',1.4,'DisplayName','-1.6 L/min flow-sensor bias');
plot(flowAxes,baseline.timeSeconds,baseline.p10SignedThresholdLpm,':', ...
    'LineWidth',1.6,'DisplayName','P10 signed threshold');
xline(flowAxes,baseline.faultTimeSeconds,':','Injection', ...
    'HandleVisibility','off');
yline(flowAxes,0,'k:','Zero residual','HandleVisibility','off');
hold(flowAxes,'off'); grid(flowAxes,'on');
xlabel(flowAxes,'Time (s)');
ylabel(flowAxes,'Flow residual r_Q (L/min)');
title(flowAxes,'The competing faults have identical flow residuals');
legend(flowAxes,'Location','best');
flowBounds = [baseline.flowResidualLpm; ...
    competingFault.flowResidualLpm;baseline.p10SignedThresholdLpm;0];
flowSpan = max([0.2 max(flowBounds)-min(flowBounds)]);
ylim(flowAxes,[min(flowBounds)-0.12*flowSpan ...
    max(flowBounds)+0.12*flowSpan]);
fprintf(['Baseline flow means: pump %.2f L/min, sensor %.2f L/min; ' ...
    'both cross the P10 flow test.\n'],baseline.postFaultMeanFlowResidualLpm, ...
    competingFault.postFaultMeanFlowResidualLpm);
disp(['Observe: the two traces overlap. A valid flow alarm detects a ' ...
    'discrepancy but cannot name its cause.']);

%% Baseline view 2 - the pressure channel supplies discriminating evidence
pressureFigure = figure('Name','P11 baseline: pressure discrimination');
pressureAxes = axes('Parent',pressureFigure);
plot(pressureAxes,baseline.timeSeconds,baseline.pressureResidualKpa, ...
    'LineWidth',2.0,'DisplayName','20% Pump-A loss');
hold(pressureAxes,'on');
plot(pressureAxes,competingFault.timeSeconds, ...
    competingFault.pressureResidualKpa,'--','LineWidth',1.5, ...
    'DisplayName','Flow-sensor bias');
plot(pressureAxes,baseline.timeSeconds, ...
    baseline.pressureSignedThresholdKpa,':','LineWidth',1.6, ...
    'DisplayName','Pressure signed threshold');
xline(pressureAxes,baseline.faultTimeSeconds,':','Injection', ...
    'HandleVisibility','off');
yline(pressureAxes,0,'k:','Zero residual','HandleVisibility','off');
hold(pressureAxes,'off'); grid(pressureAxes,'on');
xlabel(pressureAxes,'Time (s)');
ylabel(pressureAxes,'Discharge-pressure residual r_P (kPa)');
title(pressureAxes,'Only the physical pump loss crosses the pressure test');
legend(pressureAxes,'Location','best');
pressureBounds = [baseline.pressureResidualKpa; ...
    competingFault.pressureResidualKpa; ...
    baseline.pressureSignedThresholdKpa;0];
pressureSpan = max([1 max(pressureBounds)-min(pressureBounds)]);
ylim(pressureAxes,[min(pressureBounds)-0.12*pressureSpan ...
    max(pressureBounds)+0.12*pressureSpan]);
fprintf(['Baseline pressure means: pump %.2f kPa, sensor %.2f kPa.\n'], ...
    baseline.postFaultMeanPressureResidualKpa, ...
    competingFault.postFaultMeanPressureResidualKpa);

%% Baseline view 3 - compare the two-bit residual signatures
signatureFigure = figure('Name','P11 baseline: residual signatures');
signatureAxes = axes('Parent',signatureFigure);
bar(signatureAxes,[baseline.observedSignature; ...
    competingFault.observedSignature],0.72);
grid(signatureAxes,'on');
xticks(signatureAxes,[1 2]);
xticklabels(signatureAxes,{'Pump-A loss','Flow-sensor bias'});
ylabel(signatureAxes,'Thresholded residual test (0 or 1)');
title(signatureAxes,'Distinct two-channel signatures isolate the candidates');
legend(signatureAxes,{'Flow mean test','Pressure mean test'}, ...
    'Location','best');
ylim(signatureAxes,[0 1.15]); yticks(signatureAxes,[0 1]);
fprintf(['Baseline signatures: Pump-A loss %s -> %s; flow-sensor bias ' ...
    '%s -> %s.\n'],baseline.signatureCode, ...
    baseline.decodedCandidateLabel,competingFault.signatureCode, ...
    competingFault.decodedCandidateLabel);
disp(['Mechanism: detection asks whether evidence crossed a boundary; ' ...
    'isolation compares the pattern across independently informative channels.']);

%% Sweep 1 - move only Pump-A effectiveness loss
pumpLossSweep = [0 0.04 0.08 0.12 0.20];
pumpFlowEvidenceRatio = zeros(size(pumpLossSweep));
pumpPressureEvidenceRatio = zeros(size(pumpLossSweep));
pumpSignatures = zeros(numel(pumpLossSweep),2);
pumpCorrectIsolation = false(size(pumpLossSweep));
for k = 1:numel(pumpLossSweep)
    changed = model(pumpLossSweep(k),0);
    pumpFlowEvidenceRatio(k) = ...
        -changed.postFaultMeanFlowResidualLpm/ ...
        changed.flowThresholdMagnitudeLpm;
    pumpPressureEvidenceRatio(k) = ...
        -changed.postFaultMeanPressureResidualKpa/ ...
        changed.pressureThresholdMagnitudeKpa;
    pumpSignatures(k,:) = changed.observedSignature;
    pumpCorrectIsolation(k) = changed.isCorrectIsolation;
end
pumpSweepFigure = figure('Name','P11 sweep 1: Pump-A loss coverage');
pumpSweepAxes = axes('Parent',pumpSweepFigure);
plot(pumpSweepAxes,100*pumpLossSweep,pumpFlowEvidenceRatio,'o-', ...
    'LineWidth',1.6,'DisplayName','Flow evidence / threshold');
hold(pumpSweepAxes,'on');
plot(pumpSweepAxes,100*pumpLossSweep,pumpPressureEvidenceRatio,'s-', ...
    'LineWidth',1.6,'DisplayName','Pressure evidence / threshold');
yline(pumpSweepAxes,1,':','Test boundary','HandleVisibility','off');
hold(pumpSweepAxes,'off'); grid(pumpSweepAxes,'on');
xlabel(pumpSweepAxes,'Conditional Pump-A effectiveness loss (%)');
ylabel(pumpSweepAxes,'Signed evidence magnitude / threshold (dimensionless)');
title(pumpSweepAxes,'Both tests must cross for the modeled pump signature 11');
legend(pumpSweepAxes,'Location','best');
fprintf(['Pump-loss sweep signatures = [%d%d %d%d %d%d %d%d %d%d]; ' ...
    'correct-isolation flags = [%d %d %d %d %d].\n'], ...
    pumpSignatures(1,1),pumpSignatures(1,2), ...
    pumpSignatures(2,1),pumpSignatures(2,2), ...
    pumpSignatures(3,1),pumpSignatures(3,2), ...
    pumpSignatures(4,1),pumpSignatures(4,2), ...
    pumpSignatures(5,1),pumpSignatures(5,2),pumpCorrectIsolation);
disp(['At 8% loss, flow crosses first and the observed code is 10. The ' ...
    'library misisolates that weak pump case as sensor bias: a coverage gap.']);

%% Sweep 2 - reset pump loss, then move only flow-sensor bias
sensorBiasSweepLpm = [0 0.30 0.60 1.00 1.60];
sensorFlowEvidenceRatio = zeros(size(sensorBiasSweepLpm));
sensorPressureEvidenceRatio = zeros(size(sensorBiasSweepLpm));
sensorSignatures = zeros(numel(sensorBiasSweepLpm),2);
sensorCorrectIsolation = false(size(sensorBiasSweepLpm));
for k = 1:numel(sensorBiasSweepLpm)
    changed = model(0,sensorBiasSweepLpm(k));
    sensorFlowEvidenceRatio(k) = ...
        -changed.postFaultMeanFlowResidualLpm/ ...
        changed.flowThresholdMagnitudeLpm;
    sensorPressureEvidenceRatio(k) = ...
        -changed.postFaultMeanPressureResidualKpa/ ...
        changed.pressureThresholdMagnitudeKpa;
    sensorSignatures(k,:) = changed.observedSignature;
    sensorCorrectIsolation(k) = changed.isCorrectIsolation;
end
sensorSweepFigure = figure('Name','P11 sweep 2: flow-sensor bias');
sensorSweepAxes = axes('Parent',sensorSweepFigure);
plot(sensorSweepAxes,sensorBiasSweepLpm,sensorFlowEvidenceRatio,'o-', ...
    'LineWidth',1.6,'DisplayName','Flow evidence / threshold');
hold(sensorSweepAxes,'on');
plot(sensorSweepAxes,sensorBiasSweepLpm,sensorPressureEvidenceRatio,'s-', ...
    'LineWidth',1.6,'DisplayName','Pressure evidence / threshold');
yline(sensorSweepAxes,1,':','Test boundary','HandleVisibility','off');
hold(sensorSweepAxes,'off'); grid(sensorSweepAxes,'on');
xlabel(sensorSweepAxes,'Negative flow-sensor bias magnitude (L/min)');
ylabel(sensorSweepAxes,'Signed evidence magnitude / threshold (dimensionless)');
title(sensorSweepAxes,'Sensor bias crosses only the flow test');
legend(sensorSweepAxes,'Location','best');
fprintf(['Sensor-bias sweep signatures = [%d%d %d%d %d%d %d%d %d%d]; ' ...
    'correct-isolation flags = [%d %d %d %d %d].\n'], ...
    sensorSignatures(1,1),sensorSignatures(1,2), ...
    sensorSignatures(2,1),sensorSignatures(2,2), ...
    sensorSignatures(3,1),sensorSignatures(3,2), ...
    sensorSignatures(4,1),sensorSignatures(4,2), ...
    sensorSignatures(5,1),sensorSignatures(5,2),sensorCorrectIsolation);
disp(['Only bias moved. Pressure, pump-loss components, command, timing, ' ...
    'thresholds, and the candidate library remained fixed.']);

%% Deliberately broken case - remove the discriminating pressure channel
% Diagnosability requires distinct signatures over the retained channels.
brokenCase = model(0.20,0);
brokenFigure = figure('Name','P11 broken case: flow-only ambiguity');
brokenAxes = axes('Parent',brokenFigure);
bar(brokenAxes,brokenCase.brokenFlowOnlyHammingDistances,0.62);
grid(brokenAxes,'on');
xticks(brokenAxes,1:3);
xticklabels(brokenAxes,brokenCase.candidateLabels);
ylabel(brokenAxes,'Flow-only Hamming distance (bits)');
title(brokenAxes,'Removing pressure gives two exact fault matches');
ylim(brokenAxes,[0 1.2]); yticks(brokenAxes,[0 1]);
fprintf(['Broken flow-only exact matches = %d (Pump-A loss and ' ...
    'flow-sensor bias).\n'],brokenCase.brokenFlowOnlyExactMatchCount);
disp(['Violated assumption: candidate faults must retain distinct ' ...
    'signatures over the channels actually used. More tuning cannot ' ...
    'recover information that the decoder discarded.']);

%% Read the scope boundary
disp(['A unique exact signature is not certainty or probability. The ' ...
    'single-fault library can misisolate a weak fault and is not applicable ' ...
    'when both injected faults are active. P12 adds probabilistic reasoning.']);
