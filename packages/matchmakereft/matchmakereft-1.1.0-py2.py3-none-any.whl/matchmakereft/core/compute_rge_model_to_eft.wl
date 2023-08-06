If[$ScriptCommandLine==={},
argv = Drop[$CommandLine,3],
argv = Drop[$ScriptCommandLine,1]];
modelF=ToString[argv[[-2]]];
modelE=ToString[argv[[-1]]];
thisdir = Directory[];
Get["matcher`"];
(*modelEdir = FileNameJoin[{thisdir,modelE}];
modelFdir = FileNameJoin[{thisdir,modelF}];*)
ComputeRGEModeltoEFT[modelF,modelE,Verbose->False]
