% Shell Process Control 
G0=[4.05,1.77,5.88,1.2,1.44; ...
    5.39,5.72,6.9,1.52,1.83;...
    3.66,1.65,5.53,1.16,1.27;...
    5.92,2.54,8.1,1.73,1.79;...
    4.13,2.38,6.23,1.31,1.26;
    4.06,4.18,6.53,1.19,1.17;
    4.38,4.42,7.20,1.14,1.26];
T={50,60,50,45,40;...
   50,60,40,25,20;...
   9,30,40,11,6;
   12,27,20,5,19;
   8,19,10,2,22;
   13,33,9,19,24;
   33,44,19,27,32};
for ct=1:size(T,1)*size(T,2)
   T{ct}=[T{ct},1];
end
tau=[27,28,27,27,27;...
    18,14,15,15,15;
    2,20,2,0,0;
    11,12,2,0,0;
    5,7,2,0,0;
    8,4,1,0,0;
    20,22,0,0,0];
G=tf(num2cell(G0),T,'IODelay',tau);

sys_continuous = ss(G);
Ts = 2; 
sys_discrete = c2d(sys_continuous, Ts);
sys_discrete = setmpcsignals(sys_discrete, 'MV', [1 2 3], 'MD', [4 5]);
P = 90; 
M = 10;
mpcobj = mpc(sys_discrete, Ts, P, M);
mpcobj.MV(1).Min = -0.5;
mpcobj.MV(1).Max = 0.5;
mpcobj.MV(1).RateMin = -0.05;
mpcobj.MV(1).RateMax = 0.05;
mpcobj.MV(2).Min = -0.5;
mpcobj.MV(2).Max = 0.5;
mpcobj.MV(2).RateMin = -0.05;
mpcobj.MV(2).RateMax = 0.05;
mpcobj.MV(3).Min = -0.5;
mpcobj.MV(3).Max = 0.5;
mpcobj.MV(3).RateMin = -0.05;
mpcobj.MV(3).RateMax = 0.05;

mpcobj.Weights.OutputVariables = [1 1 1 0 0 0 0]; 
mpcobj.Weights.ManipulatedVariablesRate = [0.5 0.5 0.5]; 

   