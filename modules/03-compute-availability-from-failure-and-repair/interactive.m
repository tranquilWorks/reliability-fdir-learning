function interactive
%INTERACTIVE Explore failure, repair, and two-state point availability.
% Pin this module's implementation before the launcher removes its path.
modelForThisModule = @model;
fig = uifigure('Name','P03 Failure, Repair, and Availability', ...
    'Position',[100 100 1180 720]);
gridLayout = uigridlayout(fig,[5 4]);
gridLayout.RowHeight = {28,50,32,'1x',115};
gridLayout.ColumnWidth = {'1x','1x','1x','1x'};

failureLabel = uilabel(gridLayout,'Text','Failure rate lambda (failures/h)');
failureLabel.Layout.Row = 1; failureLabel.Layout.Column = 1;
repairLabel = uilabel(gridLayout,'Text','Mean time to repair, MTTR (h)');
repairLabel.Layout.Row = 1; repairLabel.Layout.Column = 2;
missionLabel = uilabel(gridLayout,'Text','Observation horizon (h)');
missionLabel.Layout.Row = 1; missionLabel.Layout.Column = 3;
initialLabel = uilabel(gridLayout,'Text','Initial state');
initialLabel.Layout.Row = 1; initialLabel.Layout.Column = 4;

failureControl = uispinner(gridLayout,'Limits',[0 0.01],'Step',1e-4, ...
    'Value',1e-3,'ValueDisplayFormat','%.4f /h');
failureControl.Layout.Row = 2; failureControl.Layout.Column = 1;
repairControl = uispinner(gridLayout,'Limits',[0.1 200],'Step',1, ...
    'Value',10,'ValueDisplayFormat','%.1f h');
repairControl.Layout.Row = 2; repairControl.Layout.Column = 2;
missionControl = uispinner(gridLayout,'Limits',[10 5000],'Step',10, ...
    'Value',100,'ValueDisplayFormat','%.0f h');
missionControl.Layout.Row = 2; missionControl.Layout.Column = 3;
initialControl = uidropdown(gridLayout,'Items',{'Up','Down'},'Value','Up');
initialControl.Layout.Row = 2; initialControl.Layout.Column = 4;

viewLabel = uilabel(gridLayout,'Text','Visible view (one at a time)');
viewLabel.Layout.Row = 3; viewLabel.Layout.Column = 1;
viewControl = uidropdown(gridLayout, ...
    'Items',{'State occupancy','Transition flow'},'Value','State occupancy');
viewControl.Layout.Row = 3; viewControl.Layout.Column = [2 3];

displayAxes = uiaxes(gridLayout);
displayAxes.Layout.Row = 4; displayAxes.Layout.Column = [1 4];
summary = uilabel(gridLayout,'WordWrap','on');
summary.Layout.Row = 5; summary.Layout.Column = [1 4];

failureControl.ValueChangedFcn = @(~,~) updatePlots();
repairControl.ValueChangedFcn = @(~,~) updatePlots();
missionControl.ValueChangedFcn = @(~,~) updatePlots();
initialControl.ValueChangedFcn = @(~,~) updatePlots();
viewControl.ValueChangedFcn = @(~,~) updatePlots();
updatePlots();

    function updatePlots
        startsUp = double(strcmp(initialControl.Value,'Up'));
        out = modelForThisModule(failureControl.Value,repairControl.Value, ...
            missionControl.Value,601,startsUp);

        cla(displayAxes,'reset');
        if strcmp(viewControl.Value,'State occupancy')
            plot(displayAxes,out.timeHours,out.availabilityProbability, ...
                'LineWidth',1.5,'DisplayName','Available A(t)');
            hold(displayAxes,'on');
            plot(displayAxes,out.timeHours,out.unavailabilityProbability,'--', ...
                'LineWidth',1.2,'DisplayName','Unavailable 1-A(t)');
            hold(displayAxes,'off'); ylim(displayAxes,[0 1.02]);
            ylabel(displayAxes,'State probability');
            title(displayAxes,'Observable state occupancy');
        else
            plot(displayAxes,out.timeHours,out.failureTransitionFlowPerHour, ...
                'LineWidth',1.5,'DisplayName','Failure flow lambda A');
            hold(displayAxes,'on');
            plot(displayAxes,out.timeHours,out.repairTransitionFlowPerHour,'--', ...
                'LineWidth',1.5,'DisplayName','Repair flow mu(1-A)');
            hold(displayAxes,'off');
            ylabel(displayAxes,'Expected transitions per hour');
            title(displayAxes,'Mechanism: probability flow between states');
        end
        grid(displayAxes,'on');
        xlabel(displayAxes,'Time since observation starts (h)');
        legend(displayAxes,'Location','best');

        summary.Text = sprintf([ ...
            'mu = 1/MTTR = %.4g /h. A_inf = mu/(lambda+mu) = %.6f, ' ...
            'so steady expected downtime is %.2f h/year. At T = %.0f h, ' ...
            'A(T) = %.6f. Failure and repair flows become equal at the ' ...
            'steady balance; the initial state changes the transient, not A_inf.'], ...
            out.repairRatePerHour,out.steadyAvailability, ...
            out.steadyExpectedDowntimeHoursPerYear,out.missionHours, ...
            out.endpointAvailability);
    end
end
