function interactive
%INTERACTIVE Explore shared hazard and one-out-of-n mission reliability.
% Pin this module's implementation before the launcher removes its path.
modelForThisModule = @model;
fig = uifigure('Name','P04 Common-Cause Failure', ...
    'Position',[100 100 1180 720]);
gridLayout = uigridlayout(fig,[5 4]);
gridLayout.RowHeight = {28,50,32,'1x',125};
gridLayout.ColumnWidth = {'1x','1x','1x','1x'};

rateLabel = uilabel(gridLayout,'Text','Channel hazard lambda (failures/h)');
rateLabel.Layout.Row = 1; rateLabel.Layout.Column = 1;
betaLabel = uilabel(gridLayout, ...
    'Text','Common-cause fraction beta (dimensionless)');
betaLabel.Layout.Row = 1; betaLabel.Layout.Column = 2;
channelLabel = uilabel(gridLayout,'Text','Channels in one-out-of-n group');
channelLabel.Layout.Row = 1; channelLabel.Layout.Column = 3;
missionLabel = uilabel(gridLayout,'Text','Mission duration (h)');
missionLabel.Layout.Row = 1; missionLabel.Layout.Column = 4;

rateControl = uispinner(gridLayout,'Limits',[0 0.002],'Step',1e-5, ...
    'Value',1e-4,'ValueDisplayFormat','%.5f /h');
rateControl.Layout.Row = 2; rateControl.Layout.Column = 1;
betaControl = uispinner(gridLayout,'Limits',[0 1],'Step',0.01, ...
    'Value',0.05,'ValueDisplayFormat','%.2f');
betaControl.Layout.Row = 2; betaControl.Layout.Column = 2;
channelControl = uispinner(gridLayout,'Limits',[1 12],'Step',1,'Value',2, ...
    'ValueDisplayFormat','%.0f');
channelControl.Layout.Row = 2; channelControl.Layout.Column = 3;
missionControl = uispinner(gridLayout,'Limits',[10 10000],'Step',10, ...
    'Value',1000,'ValueDisplayFormat','%.0f h');
missionControl.Layout.Row = 2; missionControl.Layout.Column = 4;

viewLabel = uilabel(gridLayout,'Text','Visible view (one at a time)');
viewLabel.Layout.Row = 3; viewLabel.Layout.Column = 1;
viewControl = uidropdown(gridLayout, ...
    'Items',{'Reliability comparison','Failure-mode decomposition'}, ...
    'Value','Reliability comparison');
viewControl.Layout.Row = 3; viewControl.Layout.Column = [2 3];

displayAxes = uiaxes(gridLayout);
displayAxes.Layout.Row = 4; displayAxes.Layout.Column = [1 4];
summary = uilabel(gridLayout,'WordWrap','on');
summary.Layout.Row = 5; summary.Layout.Column = [1 4];

rateControl.ValueChangedFcn = @(~,~) updatePlots();
betaControl.ValueChangedFcn = @(~,~) updatePlots();
channelControl.ValueChangedFcn = @(~,~) updatePlots();
missionControl.ValueChangedFcn = @(~,~) updatePlots();
viewControl.ValueChangedFcn = @(~,~) updatePlots();
updatePlots();

    function updatePlots
        channels = round(channelControl.Value);
        channelControl.Value = channels;
        out = modelForThisModule(rateControl.Value,betaControl.Value, ...
            channels,missionControl.Value,601);

        cla(displayAxes,'reset');
        if strcmp(viewControl.Value,'Reliability comparison')
            plot(displayAxes,out.timeHours,out.systemReliability, ...
                'LineWidth',1.5,'DisplayName','Correct shared-hazard model');
            hold(displayAxes,'on');
            plot(displayAxes,out.timeHours, ...
                out.assumedIndependentSystemReliability,'--','LineWidth',1.4, ...
                'DisplayName','Assumed independent');
            plot(displayAxes,out.timeHours, ...
                out.marginalChannelSurvivalProbability,':','LineWidth',1.4, ...
                'DisplayName','One marginal channel');
            hold(displayAxes,'off'); ylim(displayAxes,[0 1.02]);
            ylabel(displayAxes,'Reliability probability');
            title(displayAxes,'Observable: actual versus assumed joint reliability');
        else
            plot(displayAxes,out.timeHours,out.systemFailureProbability, ...
                'LineWidth',1.5,'DisplayName','Total system failure Q');
            hold(displayAxes,'on');
            plot(displayAxes,out.timeHours,out.commonCauseEventProbability,'--', ...
                'LineWidth',1.4,'DisplayName','Shared event occurred');
            plot(displayAxes,out.timeHours,out.independentExhaustionProbability, ...
                ':','LineWidth',1.5, ...
                'DisplayName','No shared event; all independent modes failed');
            hold(displayAxes,'off');
            ylabel(displayAxes,'System failure probability');
            title(displayAxes,'Mechanism: mutually exclusive failure terms');
        end
        grid(displayAxes,'on'); xlabel(displayAxes,'Mission time (h)');
        legend(displayAxes,'Location','best');

        summary.Text = sprintf([ ...
            'lambda_c = beta*lambda = %.4g /h and lambda_i = ' ...
            '(1-beta)*lambda = %.4g /h. At T = %.0f h, R = %.8f, ' ...
            'Q_common = %.8g, Q_independent = %.8g, and an independence ' ...
            'claim gives Q = %.8g. Beta allocates marginal hazard to one ' ...
            'shared all-channel event; it is not a correlation coefficient.'], ...
            out.commonCauseRatePerHour,out.independentFailureRatePerHour, ...
            out.missionHours,out.endpointSystemReliability, ...
            out.endpointCommonCauseEventProbability, ...
            out.endpointIndependentExhaustionProbability, ...
            out.endpointAssumedIndependentFailureProbability);
    end
end
