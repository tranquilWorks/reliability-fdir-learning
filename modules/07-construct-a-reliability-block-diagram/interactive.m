function interactive
%INTERACTIVE Explore one RBD topology or reliability view at a time.
% Pin this module's model before the launcher removes its folder from PATH.
modelForThisModule = @model;
baselineReliabilities = [0.995 0.90 0.90];

fig = uifigure('Name','P07 Construct a Reliability Block Diagram', ...
    'Position',[80 80 1220 760]);
gridLayout = uigridlayout(fig,[6 3]);
gridLayout.RowHeight = {34,48,34,34,'1x',132};
gridLayout.ColumnWidth = {'1x','1x','1x'};

supplyLabel = uilabel(gridLayout, ...
    'Text','Shared-supply reliability per fixed 1000 h (dimensionless)');
supplyLabel.Layout.Row = 1; supplyLabel.Layout.Column = 1;
pumpALabel = uilabel(gridLayout, ...
    'Text','Pump-A reliability per fixed 1000 h (dimensionless)');
pumpALabel.Layout.Row = 1; pumpALabel.Layout.Column = 2;
pumpBLabel = uilabel(gridLayout, ...
    'Text','Pump-B reliability per fixed 1000 h (dimensionless)');
pumpBLabel.Layout.Row = 1; pumpBLabel.Layout.Column = 3;

supplyControl = uispinner(gridLayout,'Limits',[0 1],'Step',0.005, ...
    'Value',baselineReliabilities(1),'ValueDisplayFormat','%.3f');
supplyControl.Layout.Row = 2; supplyControl.Layout.Column = 1;
pumpAControl = uispinner(gridLayout,'Limits',[0 1],'Step',0.05, ...
    'Value',baselineReliabilities(2),'ValueDisplayFormat','%.3f');
pumpAControl.Layout.Row = 2; pumpAControl.Layout.Column = 2;
pumpBControl = uispinner(gridLayout,'Limits',[0 1],'Step',0.05, ...
    'Value',baselineReliabilities(3),'ValueDisplayFormat','%.3f');
pumpBControl.Layout.Row = 2; pumpBControl.Layout.Column = 3;

viewLabel = uilabel(gridLayout,'Text','Visible view (one at a time)');
viewLabel.Layout.Row = 3; viewLabel.Layout.Column = 1;
viewControl = uidropdown(gridLayout, ...
    'Items',{'RBD topology','Disjoint outcome ledger'}, ...
    'Value','RBD topology');
viewControl.Layout.Row = 3; viewControl.Layout.Column = [2 3];

boundaryLabel = uilabel(gridLayout,'WordWrap','on', ...
    'Text',['Boundary: fixed 1000 h, no repair; success is S AND (A OR B). ' ...
    'Quantification assumes independent S, A, and B block events.']);
boundaryLabel.Layout.Row = 4; boundaryLabel.Layout.Column = [1 2];
resetButton = uibutton(gridLayout,'push','Text','Reset baseline', ...
    'ButtonPushedFcn',@resetControls);
resetButton.Layout.Row = 4; resetButton.Layout.Column = 3;

displayAxes = uiaxes(gridLayout);
displayAxes.Layout.Row = 5; displayAxes.Layout.Column = [1 3];
summary = uilabel(gridLayout,'WordWrap','on');
summary.Layout.Row = 6; summary.Layout.Column = [1 3];

supplyControl.ValueChangedFcn = @(~,~) updateView();
pumpAControl.ValueChangedFcn = @(~,~) updateView();
pumpBControl.ValueChangedFcn = @(~,~) updateView();
viewControl.ValueChangedFcn = @(~,~) updateView();
updateView();

    function resetControls(~,~)
        supplyControl.Value = baselineReliabilities(1);
        pumpAControl.Value = baselineReliabilities(2);
        pumpBControl.Value = baselineReliabilities(3);
        viewControl.Value = 'RBD topology';
        updateView();
    end

    function updateView
        out = modelForThisModule(supplyControl.Value,pumpAControl.Value, ...
            pumpBControl.Value);
        if strcmp(viewControl.Value,'RBD topology')
            drawCorrectRbd(displayAxes,out);
        else
            cla(displayAxes,'reset');
            bar(displayAxes,1:5,out.outcomeProbabilities,0.68);
            grid(displayAxes,'on'); xticks(displayAxes,1:5);
            xticklabels(displayAxes,{'S fails','S works; A+B fail', ...
                'S + only A','S + only B','S + A + B'});
            ylabel(displayAxes, ...
                ['Outcome probability per fixed 1000-hour mission ' ...
                '(dimensionless)']);
            title(displayAxes,'Disjoint outcomes: two failures, three successes');
            ylim(displayAxes,[0 1]);
        end

        summary.Text = sprintf([ ...
            'R_S = %.3f, R_A = %.3f, and R_B = %.3f give ' ...
            'R_pumps = R_A + (1-R_A)R_B = %.5f and ' ...
            'R_system = R_S*R_pumps = %.5f; Q_system = %.5f. ' ...
            'The shared supply appears once before the split because every ' ...
            'valid success path requires it. P06 detection coverage is ' ...
            'evidence about a failure mode; it does not change this physical ' ...
            'success probability without a modeled detection-and-recovery action.'], ...
            out.blockReliabilities(1),out.blockReliabilities(2), ...
            out.blockReliabilities(3),out.pumpGroupReliability, ...
            out.systemReliability,out.systemFailureProbability);
    end

    function drawCorrectRbd(axesHandle,out)
        cla(axesHandle,'reset'); hold(axesHandle,'on');
        plot(axesHandle,[0.5 1.2],[0 0],'k-','LineWidth',1.5);
        drawBlock(axesHandle,1.2,-0.55,1.8,1.1, ...
            sprintf('S: supply works\nR_S = %.3f', ...
            out.blockReliabilities(1)),[0.86 0.92 1.00]);
        plot(axesHandle,[3.0 4.0],[0 0],'k-','LineWidth',1.5);
        plot(axesHandle,[4.0 4.0],[-1.5 1.5],'k-','LineWidth',1.5);
        plot(axesHandle,[4.0 4.8],[1.5 1.5],'k-','LineWidth',1.5);
        plot(axesHandle,[4.0 4.8],[-1.5 -1.5],'k-','LineWidth',1.5);
        drawBlock(axesHandle,4.8,0.95,1.8,1.1, ...
            sprintf('A: Pump A works\nR_A = %.3f', ...
            out.blockReliabilities(2)),[0.90 0.96 0.86]);
        drawBlock(axesHandle,4.8,-2.05,1.8,1.1, ...
            sprintf('B: Pump B works\nR_B = %.3f', ...
            out.blockReliabilities(3)),[0.90 0.96 0.86]);
        plot(axesHandle,[6.6 7.5],[1.5 1.5],'k-','LineWidth',1.5);
        plot(axesHandle,[6.6 7.5],[-1.5 -1.5],'k-','LineWidth',1.5);
        plot(axesHandle,[7.5 7.5],[-1.5 1.5],'k-','LineWidth',1.5);
        plot(axesHandle,[7.5 8.7],[0 0],'k-','LineWidth',1.5);
        text(axesHandle,0.45,0,'SOURCE','HorizontalAlignment','right');
        text(axesHandle,8.75,0,'COOLING','HorizontalAlignment','left');
        text(axesHandle,4.0,2.25,'split: either pump may succeed', ...
            'HorizontalAlignment','center');
        text(axesHandle,4.9,-2.65,sprintf( ...
            'R_{system} = R_S[R_A + (1-R_A)R_B] = %.5f', ...
            out.systemReliability),'HorizontalAlignment','center', ...
            'Interpreter','tex','FontWeight','bold');
        axis(axesHandle,[0 9.6 -3 3]); axis(axesHandle,'off');
        title(axesHandle,'Functional success topology: S AND (A OR B)');
        hold(axesHandle,'off');
    end

    function drawBlock(axesHandle,x,y,width,height,label,color)
        rectangle('Parent',axesHandle,'Position',[x y width height], ...
            'FaceColor',color,'EdgeColor',[0.15 0.15 0.15], ...
            'LineWidth',1.3);
        text(axesHandle,x+width/2,y+height/2,label, ...
            'HorizontalAlignment','center','VerticalAlignment','middle', ...
            'Interpreter','tex');
    end
end
