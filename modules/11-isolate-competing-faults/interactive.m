function interactive
%INTERACTIVE Move competing-fault levers and inspect one view at a time.
% Pin this module's model before the launcher removes its folder from PATH.
modelForThisModule = @model;
baselineLossPercent = 20;
baselineSensorBiasLpm = 0;

fig = uifigure('Name','P11 Isolate Competing Faults', ...
    'Position',[60 60 1280 830]);
gridLayout = uigridlayout(fig,[8 2]);
gridLayout.RowHeight = {34,48,30,46,74,'1x',92,104};
gridLayout.ColumnWidth = {'1x','1x'};

lossLabel = uilabel(gridLayout, ...
    'Text','Conditional Pump-A effectiveness loss after 20 s (%)');
lossLabel.Layout.Row = 1; lossLabel.Layout.Column = 1;
biasLabel = uilabel(gridLayout, ...
    'Text','Negative flow-sensor bias magnitude after 20 s (L/min)');
biasLabel.Layout.Row = 1; biasLabel.Layout.Column = 2;

lossControl = uispinner(gridLayout,'Limits',[0 100], ...
    'Step',2,'Value',baselineLossPercent,'ValueDisplayFormat','%.0f');
lossControl.Layout.Row = 2; lossControl.Layout.Column = 1;
biasControl = uispinner(gridLayout,'Limits',[0 5], ...
    'Step',0.10,'Value',baselineSensorBiasLpm, ...
    'ValueDisplayFormat','%.2f');
biasControl.Layout.Row = 2; biasControl.Layout.Column = 2;

viewLabel = uilabel(gridLayout,'Text','Visible view (one at a time)');
viewLabel.Layout.Row = 3; viewLabel.Layout.Column = 1;
viewControl = uidropdown(gridLayout, ...
    'Items',{'Flow residual','Pressure residual','Residual signature', ...
    'Pump-loss coverage sweep','Sensor-bias sweep'}, ...
    'Value','Flow residual');
viewControl.Layout.Row = 4; viewControl.Layout.Column = 1;
resetButton = uibutton(gridLayout,'push','Text','Reset Pump-A baseline', ...
    'ButtonPushedFcn',@resetControls);
resetButton.Layout.Row = 4; resetButton.Layout.Column = 2;

boundary = uilabel(gridLayout,'WordWrap','on','Text',[ ...
    'Boundary: P10 flow detection is retained at r_Q <= -0.50 L/min. ' ...
    'P11 compares mean-flow and mean-pressure tests over 22-28 s: ' ...
    'healthy 00, pump loss 11, sensor bias 10. Matches are deterministic ' ...
    'signature evidence, not probabilities or recovery commands.']);
boundary.Layout.Row = 5; boundary.Layout.Column = [1 2];

displayAxes = uiaxes(gridLayout);
displayAxes.Layout.Row = 6; displayAxes.Layout.Column = [1 2];
summary = uilabel(gridLayout,'WordWrap','on');
summary.Layout.Row = 7; summary.Layout.Column = [1 2];
mechanism = uilabel(gridLayout,'WordWrap','on');
mechanism.Layout.Row = 8; mechanism.Layout.Column = [1 2];

lossControl.ValueChangedFcn = @(~,~) updateView();
biasControl.ValueChangedFcn = @(~,~) updateView();
viewControl.ValueChangedFcn = @(~,~) updateView();
updateView();

    function resetControls(~,~)
        lossControl.Value = baselineLossPercent;
        biasControl.Value = baselineSensorBiasLpm;
        viewControl.Value = 'Flow residual';
        updateView();
    end

    function updateView
        out = modelForThisModule(lossControl.Value/100,biasControl.Value);
        if strcmp(viewControl.Value,'Flow residual')
            drawFlowResidual(displayAxes,out);
        elseif strcmp(viewControl.Value,'Pressure residual')
            drawPressureResidual(displayAxes,out);
        elseif strcmp(viewControl.Value,'Residual signature')
            drawSignature(displayAxes,out);
        elseif strcmp(viewControl.Value,'Pump-loss coverage sweep')
            drawPumpSweep(displayAxes);
        else
            drawSensorSweep(displayAxes);
        end

        summary.Text = sprintf([ ...
            'Flow mean = %.3f L/min; pressure mean = %.3f kPa; ' ...
            'bias-consistency mean = %.3f kPa; signature = %s; raw exact ' ...
            'match = %s; applicable single-fault case = %d.'], ...
            out.postFaultMeanFlowResidualLpm, ...
            out.postFaultMeanPressureResidualKpa, ...
            out.postFaultMeanBiasConsistencyKpa,out.signatureCode, ...
            out.decodedCandidateLabel,out.singleFaultLibraryApplicable);
        mechanism.Text = [ ...
            'Mechanism: a pump loss moves both residual means; primary ' ...
            'flow-sensor bias moves only flow. ' out.diagnosisStatement ' ' ...
            'A weak pump can cross flow before pressure and be misisolated. ' ...
            'Both nonzero controls violate this single-fault library; P12 ' ...
            'will reason about uncertainty rather than turn a match into certainty.'];
    end

    function drawFlowResidual(axesHandle,out)
        cla(axesHandle,'reset');
        plot(axesHandle,out.timeSeconds,out.flowResidualLpm, ...
            'LineWidth',1.7,'DisplayName','Flow residual r_Q');
        hold(axesHandle,'on');
        plot(axesHandle,out.timeSeconds,out.p10SignedThresholdLpm,'--', ...
            'LineWidth',1.5,'DisplayName','P10 signed threshold');
        xline(axesHandle,out.faultTimeSeconds,':','Injection', ...
            'HandleVisibility','off');
        yline(axesHandle,0,'k:','Zero','HandleVisibility','off');
        hold(axesHandle,'off'); grid(axesHandle,'on');
        xlabel(axesHandle,'Time (s)');
        ylabel(axesHandle,'Flow residual r_Q (L/min)');
        title(axesHandle,'Flow detects a negative discrepancy, not its cause');
        legend(axesHandle,'Location','best');
        values = [out.flowResidualLpm;out.p10SignedThresholdLpm;0];
        span = max([0.2 max(values)-min(values)]);
        ylim(axesHandle,[min(values)-0.12*span max(values)+0.12*span]);
    end

    function drawPressureResidual(axesHandle,out)
        cla(axesHandle,'reset');
        plot(axesHandle,out.timeSeconds,out.pressureResidualKpa, ...
            'LineWidth',1.7,'DisplayName','Pressure residual r_P');
        hold(axesHandle,'on');
        plot(axesHandle,out.timeSeconds,out.pressureSignedThresholdKpa,'--', ...
            'LineWidth',1.5,'DisplayName','Pressure signed threshold');
        xline(axesHandle,out.faultTimeSeconds,':','Injection', ...
            'HandleVisibility','off');
        yline(axesHandle,0,'k:','Zero','HandleVisibility','off');
        hold(axesHandle,'off'); grid(axesHandle,'on');
        xlabel(axesHandle,'Time (s)');
        ylabel(axesHandle,'Discharge-pressure residual r_P (kPa)');
        title(axesHandle,'Pressure supplies the discriminating channel');
        legend(axesHandle,'Location','best');
        values = [out.pressureResidualKpa;out.pressureSignedThresholdKpa;0];
        span = max([1 max(values)-min(values)]);
        ylim(axesHandle,[min(values)-0.12*span max(values)+0.12*span]);
    end

    function drawSignature(axesHandle,out)
        cla(axesHandle,'reset');
        bar(axesHandle,[out.observedSignature; ...
            out.candidateSignatureMatrix],0.72);
        grid(axesHandle,'on');
        xticks(axesHandle,1:4);
        xticklabels(axesHandle,{'Observed','Healthy','Pump loss','Sensor bias'});
        ylabel(axesHandle,'Thresholded residual test (0 or 1)');
        title(axesHandle,'Observed evidence versus candidate signatures');
        legend(axesHandle,{'Flow mean test','Pressure mean test'}, ...
            'Location','best');
        ylim(axesHandle,[0 1.15]); yticks(axesHandle,[0 1]);
    end

    function drawPumpSweep(axesHandle)
        cla(axesHandle,'reset');
        values = [0 0.04 0.08 0.12 0.20];
        flowRatios = zeros(size(values));
        pressureRatios = zeros(size(values));
        for index = 1:numel(values)
            changed = modelForThisModule(values(index),0);
            flowRatios(index) = -changed.postFaultMeanFlowResidualLpm/ ...
                changed.flowThresholdMagnitudeLpm;
            pressureRatios(index) = ...
                -changed.postFaultMeanPressureResidualKpa/ ...
                changed.pressureThresholdMagnitudeKpa;
        end
        plot(axesHandle,100*values,flowRatios,'o-', ...
            'LineWidth',1.5,'DisplayName','Flow evidence / threshold');
        hold(axesHandle,'on');
        plot(axesHandle,100*values,pressureRatios,'s-', ...
            'LineWidth',1.5,'DisplayName','Pressure evidence / threshold');
        yline(axesHandle,1,':','Test boundary','HandleVisibility','off');
        hold(axesHandle,'off'); grid(axesHandle,'on');
        xlabel(axesHandle,'Conditional Pump-A effectiveness loss (%)');
        ylabel(axesHandle,'Signed evidence magnitude / threshold (dimensionless)');
        title(axesHandle,'Flow crosses before pressure at the coverage gap');
        legend(axesHandle,'Location','best');
    end

    function drawSensorSweep(axesHandle)
        cla(axesHandle,'reset');
        valuesLpm = [0 0.30 0.60 1.00 1.60];
        flowRatios = zeros(size(valuesLpm));
        pressureRatios = zeros(size(valuesLpm));
        for index = 1:numel(valuesLpm)
            changed = modelForThisModule(0,valuesLpm(index));
            flowRatios(index) = -changed.postFaultMeanFlowResidualLpm/ ...
                changed.flowThresholdMagnitudeLpm;
            pressureRatios(index) = ...
                -changed.postFaultMeanPressureResidualKpa/ ...
                changed.pressureThresholdMagnitudeKpa;
        end
        plot(axesHandle,valuesLpm,flowRatios,'o-', ...
            'LineWidth',1.5,'DisplayName','Flow evidence / threshold');
        hold(axesHandle,'on');
        plot(axesHandle,valuesLpm,pressureRatios,'s-', ...
            'LineWidth',1.5,'DisplayName','Pressure evidence / threshold');
        yline(axesHandle,1,':','Test boundary','HandleVisibility','off');
        hold(axesHandle,'off'); grid(axesHandle,'on');
        xlabel(axesHandle,'Negative flow-sensor bias magnitude (L/min)');
        ylabel(axesHandle,'Signed evidence magnitude / threshold (dimensionless)');
        title(axesHandle,'Sensor bias crosses only the flow test');
        legend(axesHandle,'Location','best');
    end
end
