If[$ScriptCommandLine==={},
argv = Drop[$CommandLine,3],
argv = Drop[$ScriptCommandLine,1]];
modelF=ToString[argv[[-2]]];
modelE=ToString[argv[[-1]]];
Get["matcher`"];
MatchModeltoEFT[modelF,modelE,Verbose->False]
