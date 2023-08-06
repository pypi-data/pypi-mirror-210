import sys
import os
import subprocess
import argparse
from . import file as jsf
from . import run_all
from . import generate_form
from . import functions as func
from timeit import default_timer as timer


def Model_is_EFT(model):
    # checks if model/QGRAF/model_data/listheavy is empty
    # if it is the model is an EFT (no heavy particles)
    # if it isn't the model is a UV model (with heavy particles)
    # it returns True or False
    with open(os.path.join(model,"QGRAF","model_data","listheavy")) as fi:
        s = fi.read()
    return(len(s)==0)


def check_linear_depencence_amplitudes(EFTmodel,wolframcommand):
    EFTmodeldir=jsf.proper_dir_path(EFTmodel)
    # first we check that we are using an EFT
    if Model_is_EFT(EFTmodel):
        # Amplitudes needed to match onto the EFT
        inputfile=os.path.join(EFTmodel,"QGRAF","model_data","allamplitudes.txt")
        # Check if inputfile exists otherwise create it
        if not os.path.isfile(inputfile):
            func.generate_allamplitudes(EFTmodel)
        #check we are dealing with an eft model
        if Model_is_EFT(EFTmodel):
            start=timer()
            print("Computing amplitudes to check linear independence of operators in "+EFTmodel+". This might take some time depending on the complexity of the model.")
            # we only do EFT at tree level with very large maxdim
            try:
                run_all.run_all(inputfile,EFTmodeldir,True,20,parallel)
            except Exception as E:
                raise Exception(E)

            if wolframcommand!=[]:
                coredir=func.get_path("core")
                createscript=os.path.join(coredir,"check_linear_dependence.wl")
                print("Checking linear independence of the operators in EFT model "+EFTmodel+". This might take some time depending on the complexity of the model") 
                start = timer()
                subprocess.run(wolframcommand+[createscript, EFTmodel])
                end = timer()
                print("Check finished. It took "+str(int(round(end-start)))+" seconds to compute them.")


        else:
            print("The model needs to be an EFT")

    else:
        print("The argument of this functions has to be an EFT")    
        
def match_model(NPmodel,EFTmodel,parallel,chunksize,onlytree=False):
    NPmodeldir=jsf.proper_dir_path(NPmodel)
    EFTmodeldir=jsf.proper_dir_path(EFTmodel)
    # first we check NPmodel has heavy particles
    # and EFTmodel has no heavy particles
    if Model_is_EFT(EFTmodel):
        # Amplitudes needed to match onto the EFT
        inputfile=os.path.join(EFTmodel,"QGRAF","model_data","amplitudes.txt")
        # Check if inputfile exists otherwise create it
        if not os.path.isfile(inputfile):
            func.generate_amplitudes(EFTmodel)
        if Model_is_EFT(NPmodel):
            # UV model is also an EFT
            # we allow now a different EFT for generation and matching
            # so that we can do just partial EFT integration
            if True: #NPmodel==EFTmodel:
                # RGE
                print("Running in RGEMaker mode")

                start=timer()
                print("Computing amplitudes to match the UV poles of "+EFTmodel+" onto "+NPmodel+". This might take some time depending on the complexity of the model.")
                # we start with the EFT at tree level and maxdim very large
                try:
                    run_all.run_all(inputfile,EFTmodeldir,True,20,parallel,chunksize)
                except Exception as E:
                    raise Exception(E)
                maxdim=generate_form.get_maxdim(EFTmodeldir)
                # we now do the do again the EFT, with maxdim fixed both tree level and one loop
                # we could do it directly at one loop but it does not repeat the tree level amplitudes
                # already computed
                # note that isEFT is set to false but isnoteft internally will be also set to false (0)
                if onlytree:
                    try:
                        run_all.run_all(inputfile,NPmodeldir,True,maxdim,parallel,chunksize)
                    except Exception as E:
                        raise Exception(E)

                else:
                    try:
                        run_all.run_all(inputfile,NPmodeldir,False,maxdim,parallel,chunksize)
                    except Exception as E:
                        raise Exception(E)
                end = timer()
                print("Amplitudes to match model "+NPmodel+" onto EFT "+EFTmodel+" computed.")
                print ("time taken "+str(int(round(end-start)))+" seconds ")
                
                
            else:
                print("We cannot match an EFT to a different EFT")
                return()
        else:
            # Matching a UV model to an EFT
            start=timer()
            print("Computing amplitudes to match model "+NPmodel+" onto EFT "+EFTmodel+". This might take some time depending on the complexity of the model.")
            # we start with the EFT, we only do tree level and maxdim very large
            try:
                run_all.run_all(inputfile,EFTmodeldir,True,20,parallel,chunksize)
            except Exception as E:
                raise Exception(E)
            maxdim=generate_form.get_maxdim(EFTmodeldir)
            # we now do the UV model, if onlytree=True we do only tree level
            if onlytree:
                try:
                    run_all.run_all(inputfile,NPmodeldir,True,maxdim,parallel,chunksize)
                except Exception as E:
                    raise Exception(E)
            # we now do the UV model, if onlytree=False we do both tree level and one loop
            else:
                try:
                    run_all.run_all(inputfile,NPmodeldir,False,maxdim,parallel,chunksize)
                except Exception as E:
                    raise Exception(E)
            end = timer()
            print("Amplitudes to match model "+NPmodel+" onto EFT "+EFTmodel+" computed.")
            print ("time taken "+str(int(round(end-start)))+" seconds ")
            
    else:
        print("The second model has to be an EFT")
        return()
    
