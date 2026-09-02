function interactive
%INTERACTIVE Move threshold levers and inspect one decision view at a time.
% Pin this module's model before the launcher removes its folder from PATH.
modelForThisModule = @model;
baselineThresholdLpm = 0.50;
baselineLossPercent = 20;
baselineRippleAmplitudeLpm = 0.10;

fig = uifigure('Name','P10 Move a Fault Threshold', ...
    'Position',[60 60 1280 820]);
gridLayout = uigridlayout(fig,[8 3]);
gridLayout.RowHeight = {34,48,30,46,60,'1x',84,92};
gridLayout.ColumnWidth = {'1x','1x','1x'};

thresholdLabel = uilabel(gridLayout, ...
    'Text','Threshold magnitude T (L/min)');
thresholdLabel.Layout.Row = 1; thresholdLabel.Layout.Column = 1;
lossLabel = uilabel(gridLayout, ...
    'Text','Conditional effectiveness loss after 20 s (%)');
lossLabel.Layout.Row = 1; lossLabel.Layout.Column = 2;
rippleLabel = uilabel(gridLayout, ...
    'Text','Deterministic ripple amplitude (L/min)');
rippleLabel.Layout.Row = 1; rippleLabel.Layout.Column = 3;

thresholdControl = uispinner(gridLayout,'Limits',[0 3], ...
    'Step',0.05,'Value',baselineThresholdLpm,'ValueDisplayFormat','%.2f');
thresholdControl.Layout.Row = 2; thresholdControl.Layout.Column = 1;
lossControl = uispinner(gridLayout,'Limits',[0 100], ...
    'Step',2,'Value',baselineLossPercent,'ValueDisplayFormat','%.0f');
lossControl.Layout.Row = 2; lossControl.Layout.Column = 2;
rippleControl = uispinner(gridLayout,'Limits',[0 1], ...
    'Step',0.05,'Value',baselineRippleAmplitudeLpm, ...
    'ValueDisplayFormat','%.2f');
rippleControl.Layout.Row = 2; rippleControl.Layout.Column = 3;

viewLabel = uilabel(gridLayout,'Text','Visible view (one at a time)');
viewLabel.Layout.Row = 3; viewLabel.Layout.Column = [1 2];
viewControl = uidropdown(gridLayout, ...
    'Items',{'Residual and signed threshold','Alarm decision', ...
    'Threshold tradeoff','Fault-magnitude tradeoff'}, ...
    'Value','Residual and signed threshold');
viewControl.Layout.Row = 4; viewControl.Layout.Column = [1 2];
resetButton = uibutton(gridLayout,'push','Text','Reset baseline', ...
    'ButtonPushedFcn',@resetControls);
resetButton.Layout.Row = 4; resetButton.Layout.Column = 3;

boundary = uilabel(gridLayout,'WordWrap','on','Text',[ ...
    'Boundary: P09 uses r=y-y-hat in L/min; Pump-A loss is negative. ' ...
    'P10 alarms when r <= -T. Window fractions are deterministic sample ' ...
    'counts, not field probabilities. Detection is not isolation or recovery.']);
boundary.Layout.Row = 5; boundary.Layout.Column = [1 3];

displayAxes = uiaxes(gridLayout);
displayAxes.Layout.Row = 6; displayAxes.Layout.Column = [1 3];
summary = uilabel(gridLayout,'WordWrap','on');
summary.Layout.Row = 7; summary.Layout.Column = [1 3];
mechanism = uilabel(gridLayout,'WordWrap','on');
mechanism.Layout.Row = 8; mechanism.Layout.Column = [1 3];

thresholdControl.ValueChangedFcn = @(~,~) updateView();
lossControl.ValueChangedFcn = @(~,~) updateView();
rippleControl.ValueChangedFcn = @(~,~) updateView();
viewControl.ValueChangedFcn = @(~,~) updateView();
updateView();

    function resetControls(~,~)
        thresholdControl.Value = baselineThresholdLpm;
        lossControl.Value = baselineLossPercent;
        rippleControl.Value = baselineRippleAmplitudeLpm;
        viewControl.Value = 'Residual and signed threshold';
        updateView();
    end

    function updateView
        out = modelForThisModule(thresholdControl.Value, ...
            lossControl.Value/100,rippleControl.Value);
        if strcmp(viewControl.Value,'Residual and signed threshold')
            drawResidual(displayAxes,out);
        elseif strcmp(viewControl.Value,'Alarm decision')
            drawAlarm(displayAxes,out);
        elseif strcmp(viewControl.Value,'Threshold tradeoff')
            drawThresholdTradeoff(displayAxes,out);
        else
            drawLossTradeoff(displayAxes,out);
        end

        summary.Text = sprintf([ ...
            'T = %.2f L/min; healthy mean = %.3f L/min; post-fault mean = ' ...
            '%.3f L/min; TN/FP/detected/missed = %d/%d/%d/%d; ' ...
            'false-alarm fraction = %.2f; detection fraction = %.2f.'], ...
            out.thresholdMagnitudeLpm,out.healthyMeanResidualLpm, ...
            out.postFaultMeanResidualLpm,out.trueNegativeCount, ...
            out.falseAlarmCount,out.detectionCount, ...
            out.missedDetectionCount,out.falseAlarmSampleFraction, ...
            out.detectionSampleFraction);
        mechanism.Text = [ ...
            'Move one control, then reset. Raising T moves -T downward: ' ...
            'fewer nuisance samples cross, but small fault signatures can ' ...
            'also be missed. Increasing conditional loss moves only the ' ...
            'post-injection residual. Preserve the sign before tuning the ' ...
            'magnitude; r <= +T is a comparator defect, not a tradeoff.'];
    end

    function drawResidual(axesHandle,out)
        cla(axesHandle,'reset');
        plot(axesHandle,out.timeSeconds,out.residualLpm, ...
            'LineWidth',1.5,'DisplayName','Residual r');
        hold(axesHandle,'on');
        plot(axesHandle,out.timeSeconds,out.signedThresholdLpm,'--', ...
            'LineWidth',1.6,'DisplayName','Signed threshold -T');
        yline(axesHandle,0,'k:','Zero residual','HandleVisibility','off');
        xline(axesHandle,out.faultTimeSeconds,':','Loss injection', ...
            'HandleVisibility','off');
        hold(axesHandle,'off'); grid(axesHandle,'on');
        xlabel(axesHandle,'Time (s)');
        ylabel(axesHandle,'Diagnostic residual and threshold (L/min)');
        title(axesHandle,'Alarm when the residual crosses below -T');
        legend(axesHandle,'Location','best');
        values = [out.residualLpm;out.signedThresholdLpm;0];
        lower = min(values); upper = max(values);
        span = max([0.2 upper-lower]);
        ylim(axesHandle,[lower-0.12*span upper+0.12*span]);
    end

    function drawAlarm(axesHandle,out)
        cla(axesHandle,'reset');
        stairs(axesHandle,out.timeSeconds,double(out.alarm), ...
            'LineWidth',1.6,'DisplayName','Alarm state');
        hold(axesHandle,'on');
        xline(axesHandle,out.faultTimeSeconds,':','Loss injection', ...
            'HandleVisibility','off');
        hold(axesHandle,'off'); grid(axesHandle,'on');
        xlabel(axesHandle,'Time (s)'); ylabel(axesHandle,'Alarm state (0 or 1)');
        title(axesHandle,'Deterministic threshold decision');
        ylim(axesHandle,[-0.1 1.1]); yticks(axesHandle,[0 1]);
        yticklabels(axesHandle,{'clear','alarm'});
    end

    function drawThresholdTradeoff(axesHandle,out)
        cla(axesHandle,'reset');
        valuesLpm = [0.06 0.12 0.50 1.49 1.56 1.72];
        falseFractions = zeros(size(valuesLpm));
        detectionFractions = zeros(size(valuesLpm));
        for index = 1:numel(valuesLpm)
            changed = modelForThisModule(valuesLpm(index), ...
                out.effectivenessLossFraction,out.rippleAmplitudeLpm);
            falseFractions(index) = changed.falseAlarmSampleFraction;
            detectionFractions(index) = changed.detectionSampleFraction;
        end
        plot(axesHandle,valuesLpm,falseFractions,'o-', ...
            'LineWidth',1.5,'DisplayName','Healthy false-alarm fraction');
        hold(axesHandle,'on');
        plot(axesHandle,valuesLpm,detectionFractions,'s-', ...
            'LineWidth',1.5,'DisplayName','Fault detection fraction');
        hold(axesHandle,'off'); grid(axesHandle,'on');
        xlabel(axesHandle,'Threshold magnitude T (L/min)');
        ylabel(axesHandle,'Alarmed reference-window sample fraction (0 to 1)');
        title(axesHandle,'Move only T for the current residual');
        legend(axesHandle,'Location','best'); ylim(axesHandle,[-0.05 1.05]);
    end

    function drawLossTradeoff(axesHandle,out)
        cla(axesHandle,'reset');
        lossValues = [0 0.04 0.06 0.08 0.20];
        detectionFractions = zeros(size(lossValues));
        for index = 1:numel(lossValues)
            changed = modelForThisModule(out.thresholdMagnitudeLpm, ...
                lossValues(index),out.rippleAmplitudeLpm);
            detectionFractions(index) = changed.detectionSampleFraction;
        end
        plot(axesHandle,100*lossValues,detectionFractions,'o-', ...
            'LineWidth',1.6,'MarkerFaceColor',[0.1 0.45 0.8]);
        grid(axesHandle,'on');
        xlabel(axesHandle,'Conditional Pump-A effectiveness loss (%)');
        ylabel(axesHandle,'Fault-window detection fraction (0 to 1)');
        title(axesHandle,'Move only fault magnitude at the current T');
        ylim(axesHandle,[-0.05 1.05]);
    end
end
