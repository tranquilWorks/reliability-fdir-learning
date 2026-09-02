function out = model(effectivenessLossFraction,flowSensorBiasLpm)
%MODEL Isolate two competing faults with a transparent residual signature.
%   P10 detected a negative Pump-A flow residual. P11 keeps that exact flow
%   record and adds a command-conditioned discharge-pressure residual. A
%   pump effectiveness loss affects both residuals; a negative flow-sensor
%   bias affects only the flow residual. Fixed-window threshold tests form
%   the signature [flowTest pressureTest]. This is a deterministic teaching
%   library, not a posterior probability or a field diagnosis.
arguments
    effectivenessLossFraction (1,1) double = 0.20
    flowSensorBiasLpm (1,1) double = 0
end

validateattributes(effectivenessLossFraction,{'double'}, ...
    {'real','finite','>=',0,'<=',1},mfilename, ...
    'effectivenessLossFraction');
validateattributes(flowSensorBiasLpm,{'double'}, ...
    {'real','finite','>=',0,'<=',10},mfilename, ...
    'flowSensorBiasLpm');

% Preserve the P09/P10 deterministic timing, command, flow gain, ripple,
% sign convention, and reference windows.
samplePeriodSeconds = 0.1;
timeSeconds = (0:samplePeriodSeconds:30).';
commandStepTimeSeconds = 10;
faultTimeSeconds = 20;
lowCommand = 0.5;
highCommand = 0.8;
nominalGainLpmPerCommand = 10;
rippleFrequencyHz = 0.5;
rippleAmplitudeLpm = 0.10;
flowThresholdMagnitudeLpm = 0.50;

speedCommand = lowCommand*ones(size(timeSeconds));
speedCommand(timeSeconds >= commandStepTimeSeconds) = highCommand;
faultActive = double(timeSeconds >= faultTimeSeconds);
deterministicFlowRippleLpm = rippleAmplitudeLpm* ...
    sin(2*pi*rippleFrequencyHz*timeSeconds);

predictedFlowLpm = nominalGainLpmPerCommand*speedCommand;
pumpLossFlowResidualLpm = -nominalGainLpmPerCommand* ...
    effectivenessLossFraction*faultActive.*speedCommand;
sensorBiasFlowResidualLpm = -flowSensorBiasLpm*faultActive;
trueFlowLpm = predictedFlowLpm+pumpLossFlowResidualLpm;
measuredFlowLpm = trueFlowLpm+sensorBiasFlowResidualLpm+ ...
    deterministicFlowRippleLpm;
% Preserve P10's direct component-sum operation order when bias is zero.
% Measured minus predicted closes to this value within floating precision.
flowResidualLpm = pumpLossFlowResidualLpm+ ...
    sensorBiasFlowResidualLpm+deterministicFlowRippleLpm;

% The synthetic pressure channel has a calibrated sensitivity five times
% the numerical flow sensitivity, with corresponding deterministic ripple.
% That visible assumption makes a pump loss affect both channels while a
% flow-sensor bias leaves pressure unchanged.
pressureToFlowScaleKpaPerLpm = 5;
nominalPressureGainKpaPerCommand = ...
    pressureToFlowScaleKpaPerLpm*nominalGainLpmPerCommand;
pressureRippleAmplitudeKpa = ...
    pressureToFlowScaleKpaPerLpm*rippleAmplitudeLpm;
pressureThresholdMagnitudeKpa = 4;
deterministicPressureRippleKpa = pressureRippleAmplitudeKpa* ...
    sin(2*pi*rippleFrequencyHz*timeSeconds);
predictedPressureKpa = nominalPressureGainKpaPerCommand*speedCommand;
pumpLossPressureResidualKpa = -nominalPressureGainKpaPerCommand* ...
    effectivenessLossFraction*faultActive.*speedCommand;
truePressureKpa = predictedPressureKpa+pumpLossPressureResidualKpa;
measuredPressureKpa = truePressureKpa+deterministicPressureRippleKpa;
pressureResidualKpa = measuredPressureKpa-predictedPressureKpa;

% This continuous consistency residual cancels the modeled pump signature
% and calibrated ripple. A positive value therefore exposes primary-flow
% sensor bias under the declared two-channel model.
biasConsistencyResidualKpa = pressureResidualKpa- ...
    pressureToFlowScaleKpaPerLpm*flowResidualLpm;

healthyReferenceWindow = timeSeconds >= 12 & timeSeconds < 18;
faultReferenceWindow = timeSeconds >= 22 & timeSeconds < 28;
healthyReferenceCount = sum(healthyReferenceWindow);
faultReferenceCount = sum(faultReferenceWindow);
healthyMeanFlowResidualLpm = mean(flowResidualLpm(healthyReferenceWindow));
healthyMeanPressureResidualKpa = ...
    mean(pressureResidualKpa(healthyReferenceWindow));
postFaultMeanFlowResidualLpm = mean(flowResidualLpm(faultReferenceWindow));
postFaultMeanPressureResidualKpa = ...
    mean(pressureResidualKpa(faultReferenceWindow));
postFaultMeanBiasConsistencyKpa = ...
    mean(biasConsistencyResidualKpa(faultReferenceWindow));

% Treat analytically exact boundaries as inclusive despite the finite
% mean of a sampled sinusoid. The tolerance is explicit, deterministic,
% and only a small multiple of spacing at the compared magnitude.
flowFeatureComparisonToleranceLpm = 16*eps(max([1 ...
    flowThresholdMagnitudeLpm abs(postFaultMeanFlowResidualLpm)]));
pressureFeatureComparisonToleranceKpa = 16*eps(max([1 ...
    pressureThresholdMagnitudeKpa abs(postFaultMeanPressureResidualKpa)]));
flowFeatureCrossed = postFaultMeanFlowResidualLpm <= ...
    -flowThresholdMagnitudeLpm+flowFeatureComparisonToleranceLpm;
pressureFeatureCrossed = postFaultMeanPressureResidualKpa <= ...
    -pressureThresholdMagnitudeKpa+pressureFeatureComparisonToleranceKpa;

% Retain P10's pointwise signed flow decision as an explicit compatibility
% output. P11 isolation then thresholds two fixed-window mean features.
p10SignedThresholdLpm = -flowThresholdMagnitudeLpm*ones(size(timeSeconds));
p10Alarm = flowResidualLpm <= p10SignedThresholdLpm;
p10FalseAlarmSampleFraction = sum( ...
    p10Alarm & healthyReferenceWindow)/healthyReferenceCount;
p10DetectionSampleFraction = sum( ...
    p10Alarm & faultReferenceWindow)/faultReferenceCount;
pressureSignedThresholdKpa = ...
    -pressureThresholdMagnitudeKpa*ones(size(timeSeconds));
pressureAlarm = pressureResidualKpa <= pressureSignedThresholdKpa;

observedSignature = double([flowFeatureCrossed pressureFeatureCrossed]);
candidateSignatureMatrix = [0 0;1 1;1 0];
candidateLabels = {'No modeled fault', ...
    'Pump-A effectiveness loss','Flow-sensor negative bias'};
hammingDistances = sum(abs(candidateSignatureMatrix-observedSignature),2);
minimumHammingDistance = min(hammingDistances);
bestCandidateIndexes = find( ...
    hammingDistances == minimumHammingDistance).';
exactMatchMask = hammingDistances == 0;
exactMatchCount = sum(exactMatchMask);
if exactMatchCount == 1
    decodedCandidateIndex = find(exactMatchMask,1,'first');
    decodedCandidateLabel = candidateLabels{decodedCandidateIndex};
elseif exactMatchCount == 0
    decodedCandidateIndex = 0;
    decodedCandidateLabel = 'No exact signature match';
else
    decodedCandidateIndex = 0;
    decodedCandidateLabel = 'Ambiguous exact matches';
end

if effectivenessLossFraction == 0 && flowSensorBiasLpm == 0
    injectedConditionLabel = candidateLabels{1};
elseif effectivenessLossFraction > 0 && flowSensorBiasLpm == 0
    injectedConditionLabel = candidateLabels{2};
elseif effectivenessLossFraction == 0 && flowSensorBiasLpm > 0
    injectedConditionLabel = candidateLabels{3};
else
    injectedConditionLabel = 'Combined fault outside single-fault library';
end
singleFaultLibraryApplicable = ~( ...
    effectivenessLossFraction > 0 && flowSensorBiasLpm > 0);
isCorrectIsolation = singleFaultLibraryApplicable && ...
    exactMatchCount == 1 && ...
    strcmp(decodedCandidateLabel,injectedConditionLabel);
if ~singleFaultLibraryApplicable
    diagnosisStatement = [ ...
        'Not applicable: both injected faults are active but the candidate ' ...
        'library assumes at most one modeled fault.'];
elseif exactMatchCount ~= 1
    diagnosisStatement = [ ...
        'No unique exact signature match under the declared library.'];
elseif isCorrectIsolation
    diagnosisStatement = ['Unique exact signature: ' decodedCandidateLabel '.'];
else
    diagnosisStatement = [ ...
        'Unique signature match disagrees with the injected teaching case; ' ...
        'threshold coverage is insufficient for this magnitude.'];
end

% Deliberately broken decoder: removing pressure collapses the two fault
% candidates to the same flow-only signature.
brokenFlowOnlyCandidateSignatures = candidateSignatureMatrix(:,1);
brokenFlowOnlyObservedSignature = observedSignature(1);
brokenFlowOnlyHammingDistances = abs( ...
    brokenFlowOnlyCandidateSignatures-brokenFlowOnlyObservedSignature);
brokenFlowOnlyExactMatchMask = brokenFlowOnlyHammingDistances == 0;
brokenFlowOnlyExactMatchCount = sum(brokenFlowOnlyExactMatchMask);

out = struct();
out.samplePeriodSeconds = samplePeriodSeconds;
out.sampleCount = numel(timeSeconds);
out.timeSeconds = timeSeconds;
out.commandStepTimeSeconds = commandStepTimeSeconds;
out.faultTimeSeconds = faultTimeSeconds;
out.lowCommand = lowCommand;
out.highCommand = highCommand;
out.speedCommand = speedCommand;
out.faultActive = faultActive;
out.nominalGainLpmPerCommand = nominalGainLpmPerCommand;
out.rippleFrequencyHz = rippleFrequencyHz;
out.rippleAmplitudeLpm = rippleAmplitudeLpm;
out.effectivenessLossFraction = effectivenessLossFraction;
out.flowSensorBiasLpm = flowSensorBiasLpm;
out.predictedFlowLpm = predictedFlowLpm;
out.trueFlowLpm = trueFlowLpm;
out.measuredFlowLpm = measuredFlowLpm;
out.deterministicFlowRippleLpm = deterministicFlowRippleLpm;
out.pumpLossFlowResidualLpm = pumpLossFlowResidualLpm;
out.sensorBiasFlowResidualLpm = sensorBiasFlowResidualLpm;
out.flowResidualLpm = flowResidualLpm;
out.pressureToFlowScaleKpaPerLpm = pressureToFlowScaleKpaPerLpm;
out.nominalPressureGainKpaPerCommand = nominalPressureGainKpaPerCommand;
out.pressureRippleAmplitudeKpa = pressureRippleAmplitudeKpa;
out.predictedPressureKpa = predictedPressureKpa;
out.truePressureKpa = truePressureKpa;
out.measuredPressureKpa = measuredPressureKpa;
out.deterministicPressureRippleKpa = deterministicPressureRippleKpa;
out.pumpLossPressureResidualKpa = pumpLossPressureResidualKpa;
out.pressureResidualKpa = pressureResidualKpa;
out.biasConsistencyResidualKpa = biasConsistencyResidualKpa;
out.healthyReferenceWindow = healthyReferenceWindow;
out.faultReferenceWindow = faultReferenceWindow;
out.healthyReferenceCount = healthyReferenceCount;
out.faultReferenceCount = faultReferenceCount;
out.healthyMeanFlowResidualLpm = healthyMeanFlowResidualLpm;
out.healthyMeanPressureResidualKpa = healthyMeanPressureResidualKpa;
out.postFaultMeanFlowResidualLpm = postFaultMeanFlowResidualLpm;
out.postFaultMeanPressureResidualKpa = postFaultMeanPressureResidualKpa;
out.postFaultMeanBiasConsistencyKpa = postFaultMeanBiasConsistencyKpa;
out.flowFeatureComparisonToleranceLpm = ...
    flowFeatureComparisonToleranceLpm;
out.pressureFeatureComparisonToleranceKpa = ...
    pressureFeatureComparisonToleranceKpa;
out.flowFeatureCrossed = flowFeatureCrossed;
out.pressureFeatureCrossed = pressureFeatureCrossed;
out.flowThresholdMagnitudeLpm = flowThresholdMagnitudeLpm;
out.pressureThresholdMagnitudeKpa = pressureThresholdMagnitudeKpa;
out.p10SignedThresholdLpm = p10SignedThresholdLpm;
out.p10Alarm = p10Alarm;
out.p10FalseAlarmSampleFraction = p10FalseAlarmSampleFraction;
out.p10DetectionSampleFraction = p10DetectionSampleFraction;
out.pressureSignedThresholdKpa = pressureSignedThresholdKpa;
out.pressureAlarm = pressureAlarm;
out.observedSignature = observedSignature;
out.signatureCode = sprintf('%d%d',observedSignature(1),observedSignature(2));
out.candidateSignatureMatrix = candidateSignatureMatrix;
out.candidateLabels = candidateLabels;
out.hammingDistances = hammingDistances;
out.minimumHammingDistance = minimumHammingDistance;
out.bestCandidateIndexes = bestCandidateIndexes;
out.exactMatchMask = exactMatchMask;
out.exactMatchCount = exactMatchCount;
out.decodedCandidateIndex = decodedCandidateIndex;
out.decodedCandidateLabel = decodedCandidateLabel;
out.injectedConditionLabel = injectedConditionLabel;
out.singleFaultLibraryApplicable = singleFaultLibraryApplicable;
out.isCorrectIsolation = isCorrectIsolation;
out.diagnosisStatement = diagnosisStatement;
out.brokenFlowOnlyCandidateSignatures = ...
    brokenFlowOnlyCandidateSignatures;
out.brokenFlowOnlyObservedSignature = brokenFlowOnlyObservedSignature;
out.brokenFlowOnlyHammingDistances = brokenFlowOnlyHammingDistances;
out.brokenFlowOnlyExactMatchMask = brokenFlowOnlyExactMatchMask;
out.brokenFlowOnlyExactMatchCount = brokenFlowOnlyExactMatchCount;
out.flowResidualEquation = 'r_Q(t) = y_Q(t) - y_Q_hat(t | u(t))';
out.pressureResidualEquation = 'r_P(t) = y_P(t) - y_P_hat(t | u(t))';
out.signatureEquation = [ ...
    's = [mean_W(r_Q)<=-0.50 L/min, mean_W(r_P)<=-4 kPa], ' ...
    'inclusive within 16 eps at each compared magnitude'];
out.flowResidualUnit = 'L/min';
out.pressureResidualUnit = 'kPa';
out.signatureUnit = 'dimensionless bits';
out.signConvention = [ ...
    'negative residual means measured output is below its ' ...
    'command-conditioned prediction'];
out.libraryAssumption = [ ...
    'aligned measurements, calibrated pressure sensitivity, distinct ' ...
    'candidate signatures, and at most one modeled fault'];
out.brokenAssumption = [ ...
    'candidate faults must retain distinct signatures over every channel ' ...
    'used by the decoder'];
out.scopeBoundary = [ ...
    'deterministic signature isolation only; no posterior probability, ' ...
    'field coverage, recovery action, or safety guarantee'];
end
