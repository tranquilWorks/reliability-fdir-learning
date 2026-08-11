function out = model(lambdaPerHour,seriesCount,redundancy,commonCause,missionHours)
%MODEL Series functions with parallel redundant channels and common-cause loss.
arguments
    lambdaPerHour (1,1) double {mustBeNonnegative} = 1e-4
    seriesCount (1,1) double {mustBeInteger,mustBePositive} = 6
    redundancy (1,1) double {mustBeInteger,mustBePositive} = 1
    commonCause (1,1) double {mustBeGreaterThanOrEqual(commonCause,0),mustBeLessThanOrEqual(commonCause,1)} = 0
    missionHours (1,1) double {mustBePositive} = 1000
end
t=linspace(0,missionHours,600);
Rcomp=exp(-lambdaPerHour*t);
Rparallel=1-(1-Rcomp).^redundancy;
Rfunction=(1-commonCause).*Rparallel;
Rsystem=Rfunction.^seriesCount;
out=struct('t',t,'Rcomp',Rcomp,'Rparallel',Rparallel,'Rsystem',Rsystem, ...
    'missionReliability',Rsystem(end),'componentReliability',Rcomp(end), ...
    'seriesCount',seriesCount,'redundancy',redundancy,'commonCause',commonCause);
end
