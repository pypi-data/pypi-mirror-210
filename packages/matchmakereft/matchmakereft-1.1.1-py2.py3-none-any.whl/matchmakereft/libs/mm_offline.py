import os
import cmd
import sys
import readline
import glob
import pickle
import configparser
import inspect
import pkg_resources  
import shlex
from pathlib import Path
from . import functions
from . import match_model
from . import test_suite
from . import init_mm




__init_data = init_mm.initialise_mm()


def create_model(args=""):
    """Generates the matchmaker-eft model from a FeynRules one"""
    if len(args) == 0:
        print("We need the address of the new physics model that you want to match")
    else:
        try:
            functions.create_model(args.split(),__init_data["wc"],__init_data["fr_path"])
        except Exception as E:
            raise(E)

def clean_model(args=""):
    """Removes all calculations from previously matched model so that it can be matched again"""
    if len(args) == 0:
        print("We need the address of the new physics model that you want to clean")
    else:
        for fi in glob.glob(os.path.join(args,"*","proc*","*")):
            os.remove(fi)
        for fi in ['MatchingResult.dat','MatchingProblems.dat','RGEResult.dat']:
            if os.path.isfile(os.path.join(args,fi)):
                os.remove((os.path.join(args,fi)))
        for fi in ['amplitudes.txt','canonicalnormalization.dat','classicaldimension.dat','EFTMatching.dat','wc2fields.txt']:
            if os.path.isfile(os.path.join(args,"QGRAF","model_data",fi)):
                os.remove(os.path.join(args,"QGRAF","model_data",fi))

def copy_models(args=""):
    """Downloads the file MatchMaker.tar.gz with sample FeynRules models and a Mathematica notebook to create MatchMaker models"""
    if os.path.isdir(args):
        functions.copy_models(args)
    else:
        print("We need the path of the directory where you want the models to be copied")

def test_installation(args=""):
    """Check matchmakereft installation"""
    test_suite.test_installation(__init_data["wc"], __init_data["fr_path"])


def check_linear_dependence(args=""):
    """Checks linear independence of the operators defined in an EFT."""
    if len(args) == 0:
        print("We need the address of the new physics model that you want to match")
    else:
        try:
            match_model.check_linear_depencence_amplitudes(args, __init_data["wc"])
        except Exception as E:
            print(E)

def match_model_to_eft_amplitudes(args=""):
    """Provides the complete one-loop matching between any matchmaker-eft UV model onto any matchmaker-eft eft."""
    if len(args) == 0:
        print("We need the address of the new physics model that you want to match")
    else:
        try:
            match_model.match_model(*args.split())
        except Exception as E:
            # inspect.stack()[1].function is the function that calls match_model_to_eft_amplitudes
            # we raise an exception only when it is called from that function
            callingfunction=inspect.stack()[1].function
            if callingfunction in ["match_model_to_eft","compute_rge_model_to_eft"]:
                print(E)
                raise(E)
            print(E)


def match_model_to_eft_amplitudes_onlytree(args=""):
    """Provides the complete one-loop matching between any matchmaker-eft UV model onto any matchmaker-eft eft."""
    if len(args) == 0:
        print("We need the address of the new physics model that you want to match")
    else:
        try:
            match_model.match_model(*args.split(),True)
        except Exception as E:
            # inspect.stack()[1].function is the function that calls match_model_to_eft_amplitudes
            # we raise an exception only when it is called from that function
            if inspect.stack()[1].function == "match_model_to_eft_onlytree":
                print(E)
                raise(E)
            print(E)


def compute_wilson_coefficients(args=""):
    """Computes the Wilson coefficients for an already matched MatchMaker model"""
    if len(args) == 0:
        print("We need the address of the new physics model that you want to match")
    else:
        functions.compute_wilson_coefficients(*args.split(), __init_data["wc"])

def compute_rge_model_to_eft(args=""):
    """Computes the Wilson coefficients for an already matched MatchMaker model"""
    if len(args) == 0:
        print("We need the address of the new physics model that you want to match")
    else:
        try:
            match_model_to_eft_amplitudes(args)
            functions.compute_rge(*args.split(), __init_data["wc"])
        except Exception as E:
            raise(E)


def match_model_to_eft(args=""):
    """Provides the complete one-loop matching between any matchmaker-eft UV model onto any matchmaker-eft eft."""
    try:
        match_model_to_eft_amplitudes(args)
        compute_wilson_coefficients(args)
    except Exception as E:
        pass



def match_model_to_eft_onlytree(args=""):
    """Provides the complete one-loop matching between any matchmaker-eft UV model onto any matchmaker-eft eft."""
    try:
        match_model_to_eft_amplitudes_onlytree(args)
        compute_wilson_coefficients(args)
    except Exception as E:
        pass

