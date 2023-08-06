If[$ScriptCommandLine==={},
argv = Drop[$CommandLine,3],
argv = Drop[$ScriptCommandLine,1]];
modelE=ToString[argv[[-1]]];
Get["matcher`"];
CheckLinearDependence[modelE]
