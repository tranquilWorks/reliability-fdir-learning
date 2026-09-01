function interactive
%INTERACTIVE Explore one FMEA effect chain and occurrence partition at a time.
% Pin this module's implementation before the launcher removes its path.
modelForThisModule = @model;
baselineOccurrence = [0.005 0.10 0.10];
baselineCoverage = [0.98 0.70 0.90];
failureModeOccurrence = baselineOccurrence;
detectionCoverage = baselineCoverage;
modeChoices = {'S - Shared supply','A - Pump A','B - Pump B'};

fig = uifigure('Name','P06 Run an FMEA','Position',[80 80 1220 760]);
gridLayout = uigridlayout(fig,[6 3]);
gridLayout.RowHeight = {28,48,34,34,'1x',138};
gridLayout.ColumnWidth = {'1x','1x','1x'};

modeLabel = uilabel(gridLayout,'Text','FMEA row to inspect');
modeLabel.Layout.Row = 1; modeLabel.Layout.Column = 1;
occurrenceLabel = uilabel(gridLayout, ...
    'Text','Occurrence probability per fixed 1000 h (dimensionless)');
occurrenceLabel.Layout.Row = 1; occurrenceLabel.Layout.Column = 2;
coverageLabel = uilabel(gridLayout, ...
    'Text','Detection coverage P(annunciates | mode) (dimensionless)');
coverageLabel.Layout.Row = 1; coverageLabel.Layout.Column = 3;

modeControl = uidropdown(gridLayout,'Items',modeChoices, ...
    'Value',modeChoices{2});
modeControl.Layout.Row = 2; modeControl.Layout.Column = 1;
occurrenceControl = uispinner(gridLayout,'Limits',[0 1],'Step',0.01, ...
    'Value',baselineOccurrence(2),'ValueDisplayFormat','%.3f');
occurrenceControl.Layout.Row = 2; occurrenceControl.Layout.Column = 2;
coverageControl = uispinner(gridLayout,'Limits',[0 1],'Step',0.05, ...
    'Value',baselineCoverage(2),'ValueDisplayFormat','%.2f');
coverageControl.Layout.Row = 2; coverageControl.Layout.Column = 3;

viewLabel = uilabel(gridLayout,'Text','Visible view (one at a time)');
viewLabel.Layout.Row = 3; viewLabel.Layout.Column = 1;
viewControl = uidropdown(gridLayout, ...
    'Items',{'Effect chain','Occurrence partition'}, ...
    'Value','Effect chain');
viewControl.Layout.Row = 3; viewControl.Layout.Column = [2 3];

missionLabel = uilabel(gridLayout, ...
    'Text',['Effects: row mode alone, companion items available; ' ...
    'occurrence rows may co-occur']);
missionLabel.Layout.Row = 4; missionLabel.Layout.Column = [1 2];
resetButton = uibutton(gridLayout,'push','Text','Reset baseline', ...
    'ButtonPushedFcn',@resetControls);
resetButton.Layout.Row = 4; resetButton.Layout.Column = 3;

displayAxes = uiaxes(gridLayout);
displayAxes.Layout.Row = 5; displayAxes.Layout.Column = [1 3];
summary = uilabel(gridLayout,'WordWrap','on');
summary.Layout.Row = 6; summary.Layout.Column = [1 3];

modeControl.ValueChangedFcn = @changeMode;
occurrenceControl.ValueChangedFcn = @changeOccurrence;
coverageControl.ValueChangedFcn = @changeCoverage;
viewControl.ValueChangedFcn = @(~,~) updateView();
updateView();

    function index = selectedIndex
        index = find(strcmp(modeControl.Value,modeChoices),1);
    end

    function changeMode(~,~)
        index = selectedIndex();
        occurrenceControl.Value = failureModeOccurrence(index);
        coverageControl.Value = detectionCoverage(index);
        updateView();
    end

    function changeOccurrence(~,~)
        index = selectedIndex();
        failureModeOccurrence(index) = occurrenceControl.Value;
        updateView();
    end

    function changeCoverage(~,~)
        index = selectedIndex();
        detectionCoverage(index) = coverageControl.Value;
        updateView();
    end

    function resetControls(~,~)
        failureModeOccurrence = baselineOccurrence;
        detectionCoverage = baselineCoverage;
        modeControl.Value = modeChoices{2};
        occurrenceControl.Value = baselineOccurrence(2);
        coverageControl.Value = baselineCoverage(2);
        viewControl.Value = 'Effect chain';
        updateView();
    end

    function updateView
        index = selectedIndex();
        out = modelForThisModule(failureModeOccurrence,detectionCoverage);
        if strcmp(viewControl.Value,'Effect chain')
            drawEffectChain(displayAxes,out,index);
        else
            cla(displayAxes,'reset');
            bar(displayAxes,1:3,[out.failureModeOccurrence(index), ...
                out.detectedOccurrence(index),out.latentOccurrence(index)], ...
                0.62);
            grid(displayAxes,'on'); xticks(displayAxes,1:3);
            xticklabels(displayAxes,{'Physical occurrence q', ...
                'Detected q*c','Latent q*(1-c)'});
            ylabel(displayAxes, ...
                'Probability per fixed 1000-hour mission (dimensionless)');
            title(displayAxes,sprintf( ...
                'Mode %s: occurrence partitions by conditional coverage', ...
                out.modeIds{index}));
            upperLimit = max(0.02,1.18*out.failureModeOccurrence(index));
            ylim(displayAxes,[0 min(1,upperLimit)]);
        end

        summary.Text = sprintf([ ...
            'Mode %s: %s. q = %.4f per mission and c = %.2f give ' ...
            'detected %.4f plus latent %.4f = physical occurrence %.4f. ' ...
            'End effect under the row-only premise: %s. Prevention ' ...
            'control: %s. Detection control: %s. Across all rows, ' ...
            'expected listed occurrences = %.4f per mission; this is a ' ...
            'count, not a union probability or risk-priority score. ' ...
            'P05 combined events top-down; P06 follows each mode bottom-up.'], ...
            out.modeIds{index},out.failureModes{index}, ...
            out.failureModeOccurrence(index),out.detectionCoverage(index), ...
            out.detectedOccurrence(index),out.latentOccurrence(index), ...
            out.failureModeOccurrence(index),out.endEffects{index}, ...
            out.preventionControls{index},out.detectionControls{index}, ...
            out.expectedModeCount);
    end

    function drawEffectChain(axesHandle,out,index)
        cla(axesHandle,'reset'); hold(axesHandle,'on');
        plot(axesHandle,[1.5 2.5],[6 6],'k-','LineWidth',1.4);
        plot(axesHandle,[3.5 4.5],[6 6],'k-','LineWidth',1.4);
        plot(axesHandle,[5.5 6.5],[6 6],'k-','LineWidth',1.4);
        plot(axesHandle,[7.5 8.5],[6 6],'k-','LineWidth',1.4);
        text(axesHandle,1,6,sprintf('ITEM / FUNCTION\n%s', ...
            out.itemFunctions{index}),'HorizontalAlignment','center', ...
            'BackgroundColor',[0.86 0.92 1.00],'Margin',7);
        text(axesHandle,3,6,sprintf('FAILURE MODE\n%s', ...
            out.failureModes{index}),'HorizontalAlignment','center', ...
            'BackgroundColor',[1.00 0.90 0.82],'Margin',7);
        text(axesHandle,5,6,sprintf('LOCAL EFFECT\n%s', ...
            out.localEffects{index}),'HorizontalAlignment','center', ...
            'BackgroundColor',[0.94 0.94 0.94],'Margin',7);
        text(axesHandle,7,6,sprintf('NEXT-HIGHER EFFECT\n%s', ...
            out.nextHigherEffects{index}),'HorizontalAlignment','center', ...
            'BackgroundColor',[0.92 0.96 0.88],'Margin',7);
        text(axesHandle,9,6,sprintf('END EFFECT\n%s', ...
            out.endEffects{index}),'HorizontalAlignment','center', ...
            'BackgroundColor',[1.00 0.86 0.82],'Margin',7);
        text(axesHandle,3,2.4,sprintf(['Example cause\n%s\n' ...
            'Prevention control: %s'],out.exampleCauses{index}, ...
            out.preventionControls{index}),'HorizontalAlignment','center', ...
            'BackgroundColor',[0.96 0.96 0.96],'Margin',6);
        text(axesHandle,6.4,2.4,sprintf(['Observable effect\n%s\n' ...
            'Detection control: %s'],out.observableEffects{index}, ...
            out.detectionControls{index}),'HorizontalAlignment','center', ...
            'BackgroundColor',[0.86 0.96 0.96],'Margin',6);
        text(axesHandle,9,2.4,sprintf('Consequence class\n%s', ...
            out.consequenceClasses{index}),'HorizontalAlignment','center', ...
            'BackgroundColor',[0.96 0.90 0.96],'Margin',6);
        hold(axesHandle,'off'); axis(axesHandle,[0 10 1.2 7.4]);
        axis(axesHandle,'off');
        title(axesHandle,sprintf( ...
            ['FMEA row %s: one mode present, companion items available; ' ...
            'trace forward'], ...
            out.modeIds{index}));
    end
end
