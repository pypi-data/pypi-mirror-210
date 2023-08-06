import sys
import os
import subprocess

from . import file as jsf
from . import run_qgraf 
from . import generate_form 
from . import run_form 
from . import functions as func



def run_all(inputfile,modeldir0,isEFT,maxdim,parallel,chunksize):
    modeldir=jsf.proper_dir_path(modeldir0)
    if os.path.isfile(inputfile):
        if os.path.isdir(modeldir):
            # Run QGRAF
            try:
                run_qgraf.run_qgraf(inputfile,modeldir,isEFT)
            except Exception as E:
                raise Exception(E)
            # Generate Form
            generate_form.generate_form(modeldir,isEFT,maxdim)
            # Run Form
            try:
                run_form.run_form(modeldir,isEFT,parallel,chunksize)
            except Exception as E:
                raise Exception(E)
        else:
            print("Model directory "+modeldir+" does not exist")
    else:
        print("Input file "+inputfile+" does not exist")
