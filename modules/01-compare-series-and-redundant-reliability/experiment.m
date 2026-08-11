%% P01 - Compare Series and Redundant Reliability
close all; clc;
out=model(1e-4,6,1,0,1000);

figure('Name','P01 baseline');
plot(out.t,out.Rcomp,'--','LineWidth',1.1,'DisplayName','One component'); hold on;
plot(out.t,out.Rsystem,'LineWidth',1.4,'DisplayName','Six required functions');
grid on; xlabel('Mission time (h)'); ylabel('Reliability');
title('Series reliability compounds failure exposure'); legend('Location','best');

%% Sweep 1 - number of required functions
counts=[1 6 20];
figure('Name','P01 series sweep'); hold on; grid on;
for i=1:numel(counts)
    s=model(1e-4,counts(i),1,0,1000);
    plot(s.t,s.Rsystem,'LineWidth',1.2,'DisplayName',sprintf('%d series functions',counts(i)));
end
xlabel('Time (h)'); ylabel('System reliability'); title('Every required function creates another failure path');
legend('Location','best');

%% Sweep 2 - redundancy
reds=[1 2 3];
figure('Name','P01 redundancy sweep'); hold on; grid on;
for i=1:numel(reds)
    s=model(1e-4,6,reds(i),0,1000);
    plot(s.t,s.Rsystem,'LineWidth',1.2,'DisplayName',sprintf('%d channels/function',reds(i)));
end
xlabel('Time (h)'); ylabel('System reliability'); title('Independent redundancy raises reliability');
legend('Location','best');

%% Broken case - assume redundant channels are independent
ideal=model(1e-4,6,3,0,1000);
shared=model(1e-4,6,3,0.02,1000);
figure('Name','P01 broken case');
plot(ideal.t,ideal.Rsystem,'LineWidth',1.3,'DisplayName','Assumed independent'); hold on;
plot(shared.t,shared.Rsystem,'--','LineWidth',1.3,'DisplayName','2% common-cause loss/function');
grid on; xlabel('Time (h)'); ylabel('System reliability');
title('Broken: shared causes defeat nominal redundancy'); legend('Location','best');

assert(out.missionReliability<=out.componentReliability+eps,'Series system cannot exceed one component.');
