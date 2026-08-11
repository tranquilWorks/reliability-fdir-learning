function run_checks
one=model(1e-4,1,1,0,1000);
series=model(1e-4,6,1,0,1000);
assert(series.missionReliability<one.missionReliability,'Series count should reduce reliability.');
red=model(1e-4,6,2,0,1000);
assert(red.missionReliability>series.missionReliability,'Independent redundancy should improve reliability.');
cc=model(1e-4,6,2,0.05,1000);
assert(cc.missionReliability<red.missionReliability,'Common cause should reduce redundancy benefit.');
disp('P01 checks passed.');
end
