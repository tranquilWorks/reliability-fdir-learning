function interactive
%INTERACTIVE Explore how a hazard history changes cumulative survival.
% Pin this module's implementation before the launcher removes its path.
modelForThisModule = @model;
fig = uifigure('Name','P02 Hazard Rate and Survival','Position',[100 100 1180 720]);
gridLayout = uigridlayout(fig,[4 4]);
gridLayout.RowHeight = {28,50,'1x',105};
gridLayout.ColumnWidth = {'1x','1x','1x','1x'};

hazardLabel = uilabel(gridLayout,'Text','Baseline hazard rate (failures/h)');
hazardLabel.Layout.Row = 1; hazardLabel.Layout.Column = 1;
multiplierLabel = uilabel(gridLayout,'Text','Post-change multiplier (dimensionless)');
multiplierLabel.Layout.Row = 1; multiplierLabel.Layout.Column = 2;
changeLabel = uilabel(gridLayout,'Text','Condition-change time (h)');
changeLabel.Layout.Row = 1; changeLabel.Layout.Column = 3;
missionLabel = uilabel(gridLayout,'Text','Mission duration (h)');
missionLabel.Layout.Row = 1; missionLabel.Layout.Column = 4;

hazardControl = uispinner(gridLayout,'Limits',[0 0.002],'Step',5e-5, ...
    'Value',2e-4,'ValueDisplayFormat','%.5f /h');
hazardControl.Layout.Row = 2; hazardControl.Layout.Column = 1;
multiplierControl = uispinner(gridLayout,'Limits',[0 8],'Step',0.25, ...
    'Value',1,'ValueDisplayFormat','%.2f x');
multiplierControl.Layout.Row = 2; multiplierControl.Layout.Column = 2;
changeControl = uispinner(gridLayout,'Limits',[0 6000],'Step',100, ...
    'Value',1000,'ValueDisplayFormat','%.0f h');
changeControl.Layout.Row = 2; changeControl.Layout.Column = 3;
missionControl = uispinner(gridLayout,'Limits',[100 6000],'Step',100, ...
    'Value',3000,'ValueDisplayFormat','%.0f h');
missionControl.Layout.Row = 2; missionControl.Layout.Column = 4;

hazardAxes = uiaxes(gridLayout);
hazardAxes.Layout.Row = 3; hazardAxes.Layout.Column = [1 2];
survivalAxes = uiaxes(gridLayout);
survivalAxes.Layout.Row = 3; survivalAxes.Layout.Column = [3 4];
summary = uilabel(gridLayout,'WordWrap','on');
summary.Layout.Row = 4; summary.Layout.Column = [1 4];

controls = [hazardControl multiplierControl changeControl missionControl];
for k = 1:numel(controls)
    controls(k).ValueChangedFcn = @(~,~) updatePlots();
end
updatePlots();

    function updatePlots
        if changeControl.Value > missionControl.Value
            changeControl.Value = missionControl.Value;
        end
        out = modelForThisModule(hazardControl.Value,multiplierControl.Value, ...
            changeControl.Value,missionControl.Value,601);

        cla(hazardAxes);
        stairs(hazardAxes,out.timeHours,out.hazardPerHour,'LineWidth',1.5);
        grid(hazardAxes,'on'); xlabel(hazardAxes,'Mission time (h)');
        ylabel(hazardAxes,'Hazard rate (failures/h)');
        title(hazardAxes,'Input: conditional failure rate among survivors');

        cla(survivalAxes);
        plot(survivalAxes,out.timeHours,out.survivalProbability,'LineWidth',1.5, ...
            'DisplayName','Survival S(t)'); hold(survivalAxes,'on');
        plot(survivalAxes,out.timeHours,out.failureProbability,'--','LineWidth',1.2, ...
            'DisplayName','Failure probability 1-S(t)'); hold(survivalAxes,'off');
        grid(survivalAxes,'on'); ylim(survivalAxes,[0 1.02]);
        xlabel(survivalAxes,'Mission time (h)'); ylabel(survivalAxes,'Probability');
        title(survivalAxes,'Output: exp(-accumulated hazard)');
        legend(survivalAxes,'Location','best');

        summary.Text = sprintf([ ...
            'H(T) = integral lambda(t)dt = %.4f; S(T) = exp(-H(T)) = %.6f; ' ...
            'expected survivors = %.1f per 1000. The multiplier changes only ' ...
            'the conditional rate after %.0f h; it does not rewrite the exposure ' ...
            'already accumulated before that time.'], ...
            out.missionCumulativeHazard,out.missionSurvival, ...
            out.expectedSurvivorsPerThousand,out.changeTimeHours);
    end
end
