%% P11 - Isolate Competing Faults
% Guiding question:
% What inputs, observable effects, and failure modes matter when you isolate
% Competing Faults?

%% Read the P10 boundary before comparing causes
disp(['P10 detected a negative command-conditioned flow residual in L/min ' ...
    'with r_Q <= -0.50. P11 keeps that evidence interface. A Pump-A ' ...
    'effectiveness loss and a negative flow-sensor bias can produce the ' ...
    'same flow residual, so one alarm does not identify one cause.']);
disp(['P11 adds a command-conditioned pressure residual in kPa. Under the ' ...
    'declared synthetic sensitivity, pump loss moves flow and pressure; ' ...
    'flow-sensor bias moves flow only.']);

%% Make one prediction, then inspect the ambiguous flow evidence
disp(['Prediction: if the flow traces are identical for two faults, can ' ...
    'moving the same flow threshold make their signatures distinct?']);
pumpFault = model(0.20,0);
sensorFault = model(0,1.60);
flowFigure = figure('Name','P11 lesson: ambiguous flow residual');
flowAxes = axes('Parent',flowFigure);
plot(flowAxes,pumpFault.timeSeconds,pumpFault.flowResidualLpm, ...
    'LineWidth',2.1,'DisplayName','20% Pump-A loss');
hold(flowAxes,'on');
plot(flowAxes,sensorFault.timeSeconds,sensorFault.flowResidualLpm,'--', ...
    'LineWidth',1.4,'DisplayName','-1.6 L/min sensor bias');
plot(flowAxes,pumpFault.timeSeconds,pumpFault.p10SignedThresholdLpm,':', ...
    'LineWidth',1.5,'DisplayName','P10 threshold');
xline(flowAxes,pumpFault.faultTimeSeconds,':','Injection', ...
    'HandleVisibility','off');
yline(flowAxes,0,'k:','Zero','HandleVisibility','off');
hold(flowAxes,'off'); grid(flowAxes,'on');
xlabel(flowAxes,'Time (s)'); ylabel(flowAxes,'Flow residual r_Q (L/min)');
title(flowAxes,'Both faults cross the same flow test');
legend(flowAxes,'Location','best');
flowValues = [pumpFault.flowResidualLpm; ...
    sensorFault.flowResidualLpm;pumpFault.p10SignedThresholdLpm;0];
flowSpan = max([0.2 max(flowValues)-min(flowValues)]);
ylim(flowAxes,[min(flowValues)-0.12*flowSpan ...
    max(flowValues)+0.12*flowSpan]);
disp(['Both post-fault flow means are -1.6 L/min. Detection is valid, ' ...
    'but the flow channel alone leaves two competing explanations.']);

%% Advance once to the discriminating pressure residual
pressureFigure = figure('Name','P11 lesson: pressure discrimination');
pressureAxes = axes('Parent',pressureFigure);
plot(pressureAxes,pumpFault.timeSeconds,pumpFault.pressureResidualKpa, ...
    'LineWidth',2.0,'DisplayName','20% Pump-A loss');
hold(pressureAxes,'on');
plot(pressureAxes,sensorFault.timeSeconds,sensorFault.pressureResidualKpa, ...
    '--','LineWidth',1.4,'DisplayName','Flow-sensor bias');
plot(pressureAxes,pumpFault.timeSeconds, ...
    pumpFault.pressureSignedThresholdKpa,':','LineWidth',1.5, ...
    'DisplayName','Pressure threshold');
xline(pressureAxes,pumpFault.faultTimeSeconds,':','Injection', ...
    'HandleVisibility','off');
yline(pressureAxes,0,'k:','Zero','HandleVisibility','off');
hold(pressureAxes,'off'); grid(pressureAxes,'on');
xlabel(pressureAxes,'Time (s)');
ylabel(pressureAxes,'Discharge-pressure residual r_P (kPa)');
title(pressureAxes,'Only the physical pump loss crosses the pressure test');
legend(pressureAxes,'Location','best');
pressureValues = [pumpFault.pressureResidualKpa; ...
    sensorFault.pressureResidualKpa; ...
    pumpFault.pressureSignedThresholdKpa;0];
pressureSpan = max([1 max(pressureValues)-min(pressureValues)]);
ylim(pressureAxes,[min(pressureValues)-0.12*pressureSpan ...
    max(pressureValues)+0.12*pressureSpan]);

%% Read the residual signature and its limits
signatureFigure = figure('Name','P11 lesson: candidate signatures');
signatureAxes = axes('Parent',signatureFigure);
bar(signatureAxes,[pumpFault.observedSignature; ...
    sensorFault.observedSignature],0.72);
grid(signatureAxes,'on');
xticks(signatureAxes,[1 2]);
xticklabels(signatureAxes,{'Pump-A loss','Flow-sensor bias'});
ylabel(signatureAxes,'Thresholded residual test (0 or 1)');
title(signatureAxes,'Pump 11 and sensor 10 are now distinct');
legend(signatureAxes,{'Flow mean test','Pressure mean test'}, ...
    'Location','best');
ylim(signatureAxes,[0 1.15]); yticks(signatureAxes,[0 1]);
disp(['The decoder compares [flow test, pressure test] with healthy 00, ' ...
    'pump loss 11, and sensor bias 10. A match is not probability or certainty.']);
disp(['Run experiment.m one section at a time. Move Pump-A loss, reset, ' ...
    'then move sensor bias. Show the flow-only ambiguity last.']);
disp(['A weak pump can cross only flow and be misisolated; simultaneous ' ...
    'faults are outside this single-fault library. P12 adds probabilistic reasoning.']);
interactive;
