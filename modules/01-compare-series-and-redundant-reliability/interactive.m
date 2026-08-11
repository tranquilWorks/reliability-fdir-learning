function interactive
fig=uifigure('Name','P01 Reliability Architecture','Position',[100 100 1120 720]);
g=uigridlayout(fig,[3 5]); g.RowHeight={'1x','1x',100};
axR=uiaxes(g); axR.Layout.Row=1; axR.Layout.Column=[1 5];
axMission=uiaxes(g); axMission.Layout.Row=2; axMission.Layout.Column=[1 4];
summary=uilabel(g,'WordWrap','on'); summary.Layout.Row=2; summary.Layout.Column=5;

lam=uislider(g,'Limits',[1e-6 1e-3],'Value',1e-4,'MajorTicks',[1e-6 1e-5 1e-4 5e-4 1e-3]);
lam.Layout.Row=3; lam.Layout.Column=1;
n=uislider(g,'Limits',[1 30],'Value',6,'MajorTicks',[1 5 10 20 30]);
n.Layout.Row=3; n.Layout.Column=2;
r=uislider(g,'Limits',[1 4],'Value',1,'MajorTicks',[1 2 3 4]);
r.Layout.Row=3; r.Layout.Column=3;
cc=uislider(g,'Limits',[0 0.1],'Value',0,'MajorTicks',[0 0.01 0.02 0.05 0.1]);
cc.Layout.Row=3; cc.Layout.Column=4;
h=uislider(g,'Limits',[10 10000],'Value',1000,'MajorTicks',[10 100 1000 5000 10000]);
h.Layout.Row=3; h.Layout.Column=5;
controls=[lam n r cc h];
for i=1:numel(controls)
    controls(i).ValueChangingFcn=@(~,~) updatePlots();
    controls(i).ValueChangedFcn=@(~,~) updatePlots();
end
updatePlots();

    function updatePlots
        out=model(lam.Value,round(n.Value),round(r.Value),cc.Value,h.Value);
        cla(axR); plot(axR,out.t,out.Rcomp,'--','LineWidth',1.1); hold(axR,'on');
        plot(axR,out.t,out.Rsystem,'LineWidth',1.4); hold(axR,'off');
        grid(axR,'on'); ylim(axR,[0 1.02]); xlabel(axR,'Mission time (h)');
        ylabel(axR,'Reliability'); title(axR,'Component versus system reliability');

        alternatives=zeros(1,4);
        for q=1:4
            tmp=model(lam.Value,round(n.Value),q,cc.Value,h.Value);
            alternatives(q)=tmp.missionReliability;
        end
        cla(axMission); bar(axMission,1:4,alternatives);
        xticks(axMission,1:4); xlabel(axMission,'Channels per function'); ylabel(axMission,'Mission reliability');
        ylim(axMission,[0 1.02]); grid(axMission,'on'); title(axMission,'Redundancy trade');

        summary.Text=sprintf(['lambda %.2g /h\nseries functions %d\nredundancy %d\n' ...
            'common cause %.2f%%\nmission reliability %.6f'], ...
            lam.Value,round(n.Value),round(r.Value),100*cc.Value,out.missionReliability);
    end
end
