function interactive
%INTERACTIVE Move probability and consequence levers one at a time.
% Pin this module's model before the launcher removes its folder from PATH.
modelForThisModule = @model;
baselineProbabilities = [0.005 0.10 0.10];
baselineConsequences = [120 100 8 12];

fig = uifigure('Name','P08 Prioritize Risk Quantitatively', ...
    'Position',[60 60 1280 800]);
gridLayout = uigridlayout(fig,[8 4]);
gridLayout.RowHeight = {34,48,34,48,52,'1x',82,70};
gridLayout.ColumnWidth = {'1x','1x','1x','1x'};

supplyProbabilityLabel = uilabel(gridLayout, ...
    'Text','q_S per fixed 1000 h mission (dimensionless)');
supplyProbabilityLabel.Layout.Row = 1;
supplyProbabilityLabel.Layout.Column = 1;
pumpAProbabilityLabel = uilabel(gridLayout, ...
    'Text','q_A per fixed 1000 h mission (dimensionless)');
pumpAProbabilityLabel.Layout.Row = 1;
pumpAProbabilityLabel.Layout.Column = 2;
pumpBProbabilityLabel = uilabel(gridLayout, ...
    'Text','q_B per fixed 1000 h mission (dimensionless)');
pumpBProbabilityLabel.Layout.Row = 1;
pumpBProbabilityLabel.Layout.Column = 3;
viewLabel = uilabel(gridLayout,'Text','Visible view (one at a time)');
viewLabel.Layout.Row = 1; viewLabel.Layout.Column = 4;

supplyProbabilityControl = uispinner(gridLayout,'Limits',[0 1], ...
    'Step',0.005,'Value',baselineProbabilities(1), ...
    'ValueDisplayFormat','%.3f');
supplyProbabilityControl.Layout.Row = 2;
supplyProbabilityControl.Layout.Column = 1;
pumpAProbabilityControl = uispinner(gridLayout,'Limits',[0 1], ...
    'Step',0.01,'Value',baselineProbabilities(2), ...
    'ValueDisplayFormat','%.3f');
pumpAProbabilityControl.Layout.Row = 2;
pumpAProbabilityControl.Layout.Column = 2;
pumpBProbabilityControl = uispinner(gridLayout,'Limits',[0 1], ...
    'Step',0.01,'Value',baselineProbabilities(3), ...
    'ValueDisplayFormat','%.3f');
pumpBProbabilityControl.Layout.Row = 2;
pumpBProbabilityControl.Layout.Column = 3;
viewControl = uidropdown(gridLayout, ...
    'Items',{'Expected-loss priority','Probability-consequence plane'}, ...
    'Value','Expected-loss priority');
viewControl.Layout.Row = 2; viewControl.Layout.Column = 4;

supplyConsequenceLabel = uilabel(gridLayout, ...
    'Text','S consequence (kUSD/scenario occurrence)');
supplyConsequenceLabel.Layout.Row = 3;
supplyConsequenceLabel.Layout.Column = 1;
dualPumpConsequenceLabel = uilabel(gridLayout, ...
    'Text','A&B consequence (kUSD/scenario occurrence)');
dualPumpConsequenceLabel.Layout.Row = 3;
dualPumpConsequenceLabel.Layout.Column = 2;
pumpBConsequenceLabel = uilabel(gridLayout, ...
    'Text','B-only consequence (kUSD/scenario occurrence)');
pumpBConsequenceLabel.Layout.Row = 3;
pumpBConsequenceLabel.Layout.Column = 3;
pumpAConsequenceLabel = uilabel(gridLayout, ...
    'Text','A-only consequence (kUSD/scenario occurrence)');
pumpAConsequenceLabel.Layout.Row = 3;
pumpAConsequenceLabel.Layout.Column = 4;

supplyConsequenceControl = uispinner(gridLayout,'Limits',[0 1e6], ...
    'Step',5,'Value',baselineConsequences(1), ...
    'ValueDisplayFormat','%.1f');
supplyConsequenceControl.Layout.Row = 4;
supplyConsequenceControl.Layout.Column = 1;
dualPumpConsequenceControl = uispinner(gridLayout,'Limits',[0 1e6], ...
    'Step',5,'Value',baselineConsequences(2), ...
    'ValueDisplayFormat','%.1f');
dualPumpConsequenceControl.Layout.Row = 4;
dualPumpConsequenceControl.Layout.Column = 2;
pumpBConsequenceControl = uispinner(gridLayout,'Limits',[0 1e6], ...
    'Step',1,'Value',baselineConsequences(3), ...
    'ValueDisplayFormat','%.1f');
pumpBConsequenceControl.Layout.Row = 4;
pumpBConsequenceControl.Layout.Column = 3;
pumpAConsequenceControl = uispinner(gridLayout,'Limits',[0 1e6], ...
    'Step',1,'Value',baselineConsequences(4), ...
    'ValueDisplayFormat','%.1f');
pumpAConsequenceControl.Layout.Row = 4;
pumpAConsequenceControl.Layout.Column = 4;

boundaryLabel = uilabel(gridLayout,'WordWrap','on', ...
    'Text',['Boundary: fixed 1000 h, no repair; P07 disjoint outcomes; ' ...
    'independent S/A/B basic events; synthetic comparable kUSD impacts.']);
boundaryLabel.Layout.Row = 5; boundaryLabel.Layout.Column = [1 3];
resetButton = uibutton(gridLayout,'push','Text','Reset baseline', ...
    'ButtonPushedFcn',@resetControls);
resetButton.Layout.Row = 5; resetButton.Layout.Column = 4;

displayAxes = uiaxes(gridLayout);
displayAxes.Layout.Row = 6; displayAxes.Layout.Column = [1 4];
summary = uilabel(gridLayout,'WordWrap','on');
summary.Layout.Row = 7; summary.Layout.Column = [1 4];
mechanism = uilabel(gridLayout,'WordWrap','on');
mechanism.Layout.Row = 8; mechanism.Layout.Column = [1 4];

supplyProbabilityControl.ValueChangedFcn = @(~,~) updateView();
pumpAProbabilityControl.ValueChangedFcn = @(~,~) updateView();
pumpBProbabilityControl.ValueChangedFcn = @(~,~) updateView();
supplyConsequenceControl.ValueChangedFcn = @(~,~) updateView();
dualPumpConsequenceControl.ValueChangedFcn = @(~,~) updateView();
pumpBConsequenceControl.ValueChangedFcn = @(~,~) updateView();
pumpAConsequenceControl.ValueChangedFcn = @(~,~) updateView();
viewControl.ValueChangedFcn = @(~,~) updateView();
updateView();

    function resetControls(~,~)
        supplyProbabilityControl.Value = baselineProbabilities(1);
        pumpAProbabilityControl.Value = baselineProbabilities(2);
        pumpBProbabilityControl.Value = baselineProbabilities(3);
        supplyConsequenceControl.Value = baselineConsequences(1);
        dualPumpConsequenceControl.Value = baselineConsequences(2);
        pumpBConsequenceControl.Value = baselineConsequences(3);
        pumpAConsequenceControl.Value = baselineConsequences(4);
        viewControl.Value = 'Expected-loss priority';
        updateView();
    end

    function updateView
        probabilities = [supplyProbabilityControl.Value, ...
            pumpAProbabilityControl.Value,pumpBProbabilityControl.Value];
        consequences = [supplyConsequenceControl.Value, ...
            dualPumpConsequenceControl.Value,pumpBConsequenceControl.Value, ...
            pumpAConsequenceControl.Value];
        out = modelForThisModule(probabilities,consequences);

        if strcmp(viewControl.Value,'Expected-loss priority')
            drawPriority(displayAxes,out);
        else
            drawRiskPlane(displayAxes,out);
        end

        summary.Text = sprintf([ ...
            'Disjoint probabilities [S, A&B, B only, A only] = ' ...
            '[%.5f, %.5f, %.5f, %.5f]. Mission failure = %.5f; ' ...
            'mission success = %.5f. Expected losses = ' ...
            '[%.4f, %.4f, %.4f, %.4f] kUSD/mission; total = %.4f. ' ...
            'Current first priority: %s.'],out.scenarioProbabilities(1), ...
            out.scenarioProbabilities(2),out.scenarioProbabilities(3), ...
            out.scenarioProbabilities(4), ...
            out.systemFailureProbability,out.systemReliability, ...
            out.expectedLossKusdPerMission(1), ...
            out.expectedLossKusdPerMission(2), ...
            out.expectedLossKusdPerMission(3), ...
            out.expectedLossKusdPerMission(4), ...
            out.totalExpectedLossKusdPerMission, ...
            out.topPriorityScenarioId);
        mechanism.Text = [ ...
            'Move one control, then reset. A probability lever changes the ' ...
            'P07 outcome partition; a consequence lever leaves that partition ' ...
            'fixed and changes only its scenario loss. A single-pump loss is ' ...
            'degraded mission success, not system failure. This ranking ' ...
            'does not waive a safety constraint, prove input quality, or turn ' ...
            'P06 detection coverage into physical prevention.'];
    end

    function drawPriority(axesHandle,out)
        cla(axesHandle,'reset');
        bar(axesHandle,1:4,out.expectedLossKusdPerMission,0.68);
        grid(axesHandle,'on'); xticks(axesHandle,1:4);
        xticklabels(axesHandle,out.scenarioIds);
        ylabel(axesHandle, ...
            'Expected loss (kUSD/fixed 1000-hour mission)');
        title(axesHandle,'Priority uses a common-unit expected-loss contribution');
        upper = max([1 1.15*max(out.expectedLossKusdPerMission)]);
        ylim(axesHandle,[0 upper]);
        for index = 1:4
            text(axesHandle,index,out.expectedLossKusdPerMission(index), ...
                sprintf(' rank %d',out.priorityRanks(index)), ...
                'HorizontalAlignment','center','VerticalAlignment','bottom');
        end
    end

    function drawRiskPlane(axesHandle,out)
        cla(axesHandle,'reset');
        markerSizes = 90+520*out.riskShares;
        scatter(axesHandle,out.scenarioProbabilities, ...
            out.consequenceCostKusd,markerSizes,'filled');
        grid(axesHandle,'on');
        xlabel(axesHandle, ...
            ['Scenario occurrence probability per fixed 1000-hour mission ' ...
            '(dimensionless)']);
        ylabel(axesHandle,'Consequence cost (kUSD/scenario occurrence)');
        title(axesHandle,'Marker area grows with expected-loss share');
        xUpper = min(1,max([0.01 1.15*max(out.scenarioProbabilities)]));
        yUpper = max([1 1.15*max(out.consequenceCostKusd)]);
        xlim(axesHandle,[0 xUpper]); ylim(axesHandle,[0 yUpper]);
        for index = 1:4
            text(axesHandle,out.scenarioProbabilities(index), ...
                out.consequenceCostKusd(index), ...
                sprintf('  %s',out.scenarioIds{index}), ...
                'VerticalAlignment','bottom');
        end
    end
end
