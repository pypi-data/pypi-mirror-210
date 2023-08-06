#: Parentheses 2000
#: MaxTermSize 300000
#-
Off Statistics;
format Mathematica;
**** First we introduce the definitions that are general to all models
*** Trick to do gam(y,k+p,y)=gam(y,k,y)+gam(y,p,y)
Index itrick;
s sSS, FourPi, I, D, Dy, [MM.epsi], invepsilonbar, [MM.s1], [MM.s2], SIX, SEVEN, FIVE, ct1, ct2, iCPV;
s signo1,signo2,signo3;
v k1; 
CF DEN, ind, val, F, G;
f GAM, SPI;
Auto I mu=D;
F ALARM;
CF Evect, ubspin, uspin, vbspin, vspin, uspin1, vbspin1, ubspin1, vspin1;
CF Mom, dotp, gam, gam1, gam2, prop, invprop, eps, epsM(antisymmetric), deltaF, deltaFF, gi, Sqrt;
CF Log, den, ee, dd,tenredcountK,tenredfden0,tenredfden1,tenredtensorpart,tenredgg;
F INDSPIN, flipped, SPO;
set spins: uspin, vbspin;
s gap;
v p2;
s LAMBDA;
s dummylightmassneverused,tenredj;

*** Now model specific definitions
S NEW_SYMBOLS;
#define flFunc "NEW_FLAVOR_FUNCTIONS, ddF";
#define flmassFunc "NEW_FLAVOR_MASS_FUNCTIONS";
#define gFunc "NEW_GAUGE_FUNCTIONS, ee, ee2, dd";
CF `flFunc', `flmassFunc',`gFunc';
set flFunc:`flFunc';
set flmassFunc:`flmassFunc';
set gFunc:`gFunc';

set setlightmasses: dummylightmassneverused, LIGHTMASSESSET;
set setheavymasses: HEAVYMASSESSET;

*** define variable isnotEFT
#define isnotEFT "ISNOTEFT"

*** define variable LoopOrder
#define LoopOrder "LOOPORDER"

extrasymbols array EXTRA_SYMBOLS;

INDEX_DEFINITION

#procedure preparedeltas()
HF_DELTAS
id deltaF(?a)=d_(?a);
#endprocedure

#procedure identifydeltas()
id e_(mu1?,mu2?)=ee2(mu1,mu2);
ID_DELTAS
id ee(4,mu1?, ... , mu4?)=e_(mu1,...,mu4);
#endprocedure

#procedure calldummyindices()
DUMMY_INDICES
#endprocedure



*>>>>>>>>
CF samb,bracket1;
*<<<<<<<<
*#+
