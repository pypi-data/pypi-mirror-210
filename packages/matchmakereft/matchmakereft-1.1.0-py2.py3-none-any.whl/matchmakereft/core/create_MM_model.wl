If[$ScriptCommandLine==={},
argv = Drop[$CommandLine,3],
argv = Drop[$ScriptCommandLine,1]];
modellist=ToString/@Drop[argv,-1];
frpath=ToString[argv[[-1]]];
modelname=StringJoin[StringDrop[modellist[[-1]], -3], "_MM"]
Print["model=",modelname];
thisdir = Directory[];
$FeynRulesPath = 
  SetDirectory[frpath];
<< FeynRules`;
SetDirectory[thisdir];
FR$Loop = True;
PrependTo[$Path, "."];
LoadModel@@modellist;
<< FR2MM`;
Print[modelname];
wmod=WriteMM[Ltot,modelname,Interactive->False]
If[wmod=="1", Exit[1]]
