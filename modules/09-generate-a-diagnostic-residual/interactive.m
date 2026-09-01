function interactive
%INTERACTIVE Move residual-generation levers and inspect one view at a time.
% Pin this module's model before the launcher removes its folder from PATH.
modelForThisModule = @model;
baselineLossPercent = 20;
baselinePredictorGain = 10;
baselineRippleAmplitude = 0.10;

fig = uifigure('Name','P09 Generate a Diagnostic Residual', ...
    'Position',[60 60 1280 820]);
gridLayout = uigridlayout(fig,[8 3]);
gridLayout.RowHeight = {34,48,30,46,54,'1x',86,88};
gridLayout.ColumnWidth = {'1x','1x','1x'};

lossLabel = uilabel(gridLayout, ...
    'Text','Conditional effectiveness loss after 20 s (%)');
lossLabel.Layout.Row = 1; lossLabel.Layout.Column = 1;
gainLabel = uilabel(gridLayout, ...
    'Text','Predictor gain K-hat (L/min per normalized command)');
gainLabel.Layout.Row = 1; gainLabel.Layout.Column = 2;
rippleLabel = uilabel(gridLayout, ...
    'Text','Deterministic ripple amplitude (L/min)');
rippleLabel.Layout.Row = 1; rippleLabel.Layout.Column = 3;

lossControl = uispinner(gridLayout,'Limits',[0 100], ...
    'Step',5,'Value',baselineLossPercent,'ValueDisplayFormat','%.0f');
lossControl.Layout.Row = 2; lossControl.Layout.Column = 1;
gainControl = uispinner(gridLayout,'Limits',[0 20], ...
    'Step',0.5,'Value',baselinePredictorGain,'ValueDisplayFormat','%.1f');
gainControl.Layout.Row = 2; gainControl.Layout.Column = 2;
rippleControl = uispinner(gridLayout,'Limits',[0 1], ...
    'Step',0.05,'Value',baselineRippleAmplitude, ...
    'ValueDisplayFormat','%.2f');
rippleControl.Layout.Row = 2; rippleControl.Layout.Column = 3;

viewLabel = uilabel(gridLayout,'Text','Visible view (one at a time)');
viewLabel.Layout.Row = 3; viewLabel.Layout.Column = [1 2];
viewControl = uidropdown(gridLayout, ...
    'Items',{'Measured versus predicted flow','Diagnostic residual', ...
    'Residual decomposition'}, ...
    'Value','Diagnostic residual');
viewControl.Layout.Row = 4; viewControl.Layout.Column = [1 2];
resetButton = uibutton(gridLayout,'push','Text','Reset baseline', ...
    'ButtonPushedFcn',@resetControls);
resetButton.Layout.Row = 4; resetButton.Layout.Column = 3;

boundary = uilabel(gridLayout,'WordWrap','on','Text',[ ...
    'Boundary: synthetic Pump-A command and flow; r = y-y-hat(u) in L/min. ' ...
    'Loss is conditional magnitude, not occurrence probability. Residual ' ...
    'generation does not define an alarm threshold or prove a root cause.']);
boundary.Layout.Row = 5; boundary.Layout.Column = [1 3];

displayAxes = uiaxes(gridLayout);
displayAxes.Layout.Row = 6; displayAxes.Layout.Column = [1 3];
summary = uilabel(gridLayout,'WordWrap','on');
summary.Layout.Row = 7; summary.Layout.Column = [1 3];
mechanism = uilabel(gridLayout,'WordWrap','on');
mechanism.Layout.Row = 8; mechanism.Layout.Column = [1 3];

lossControl.ValueChangedFcn = @(~,~) updateView();
gainControl.ValueChangedFcn = @(~,~) updateView();
rippleControl.ValueChangedFcn = @(~,~) updateView();
viewControl.ValueChangedFcn = @(~,~) updateView();
updateView();

    function resetControls(~,~)
        lossControl.Value = baselineLossPercent;
        gainControl.Value = baselinePredictorGain;
        rippleControl.Value = baselineRippleAmplitude;
        viewControl.Value = 'Diagnostic residual';
        updateView();
    end

    function updateView
        out = modelForThisModule(lossControl.Value/100, ...
            gainControl.Value,rippleControl.Value);
        if strcmp(viewControl.Value,'Measured versus predicted flow')
            drawFlow(displayAxes,out);
        elseif strcmp(viewControl.Value,'Diagnostic residual')
            drawResidual(displayAxes,out);
        else
            drawDecomposition(displayAxes,out);
        end

        summary.Text = sprintf([ ...
            'Healthy high-command mean = %.3f L/min; post-fault mean = ' ...
            '%.3f L/min; fault-induced shift = %.3f L/min; command-step ' ...
            'change = %.3f L/min; decomposition error = %.3g L/min.'], ...
            out.highCommandHealthyMeanResidualLpm, ...
            out.postFaultMeanResidualLpm,out.faultResidualChangeLpm, ...
            out.commandStepResidualChangeLpm, ...
            out.maxAbsResidualDecompositionErrorLpm);
        mechanism.Text = [ ...
            'Move one control, then reset. Effectiveness loss changes only ' ...
            'the physical post-injection flow. Predictor gain changes only ' ...
            'the expectation and can create a healthy residual or cancel a ' ...
            'fault mean at one command. Ripple changes a bounded nuisance ' ...
            'component. Negative r means measured flow is below prediction; ' ...
            'nonzero r is a discrepancy, not a threshold decision or unique diagnosis.'];
    end

    function drawFlow(axesHandle,out)
        cla(axesHandle,'reset');
        plot(axesHandle,out.timeSeconds,out.measuredFlowLpm, ...
            'LineWidth',1.5,'DisplayName','Measured flow y');
        hold(axesHandle,'on');
        plot(axesHandle,out.timeSeconds,out.predictedFlowLpm,'--', ...
            'LineWidth',1.6,'DisplayName','Predicted flow y-hat(u)');
        xline(axesHandle,out.commandStepTimeSeconds,':', ...
            'Command change','HandleVisibility','off');
        xline(axesHandle,out.faultTimeSeconds,':','Loss injection', ...
            'HandleVisibility','off');
        hold(axesHandle,'off'); grid(axesHandle,'on');
        xlabel(axesHandle,'Time (s)');
        ylabel(axesHandle,'Pump-A cooling flow (L/min)');
        title(axesHandle,'Measured flow versus command-conditioned prediction');
        legend(axesHandle,'Location','best');
        flowValues = [out.measuredFlowLpm;out.predictedFlowLpm];
        lower = min(flowValues); upper = max(flowValues);
        span = max([1 upper-lower]);
        ylim(axesHandle,[min(0,lower-0.08*span) ...
            max(1,upper+0.08*span)]);
    end

    function drawResidual(axesHandle,out)
        cla(axesHandle,'reset');
        plot(axesHandle,out.timeSeconds,out.residualLpm, ...
            'LineWidth',1.6,'DisplayName','r = y-y-hat(u)');
        hold(axesHandle,'on');
        yline(axesHandle,0,'k:','Zero discrepancy','HandleVisibility','off');
        xline(axesHandle,out.commandStepTimeSeconds,':', ...
            'Command change','HandleVisibility','off');
        xline(axesHandle,out.faultTimeSeconds,':','Loss injection', ...
            'HandleVisibility','off');
        hold(axesHandle,'off'); grid(axesHandle,'on');
        xlabel(axesHandle,'Time (s)');
        ylabel(axesHandle,'Diagnostic residual r = y-y-hat (L/min)');
        title(axesHandle,'Signed command-conditioned discrepancy');
        legend(axesHandle,'Location','best');
        residualWithReference = [out.residualLpm;0];
        lower = min(residualWithReference); upper = max(residualWithReference);
        span = max([0.2 upper-lower]);
        ylim(axesHandle,[lower-0.15*span upper+0.15*span]);
    end

    function drawDecomposition(axesHandle,out)
        cla(axesHandle,'reset');
        plot(axesHandle,out.timeSeconds,out.modelMismatchResidualLpm, ...
            'LineWidth',1.3,'DisplayName','Model mismatch');
        hold(axesHandle,'on');
        plot(axesHandle,out.timeSeconds,out.faultResidualLpm, ...
            'LineWidth',1.3,'DisplayName','Effectiveness loss');
        plot(axesHandle,out.timeSeconds,out.deterministicRippleLpm, ...
            'LineWidth',1.3,'DisplayName','Deterministic ripple');
        plot(axesHandle,out.timeSeconds,out.residualLpm,'k--', ...
            'LineWidth',1.6,'DisplayName','Sum = residual');
        hold(axesHandle,'off'); grid(axesHandle,'on');
        xlabel(axesHandle,'Time (s)');
        ylabel(axesHandle,'Residual contribution (L/min)');
        title(axesHandle,'Transparent residual decomposition');
        legend(axesHandle,'Location','best');
    end
end
