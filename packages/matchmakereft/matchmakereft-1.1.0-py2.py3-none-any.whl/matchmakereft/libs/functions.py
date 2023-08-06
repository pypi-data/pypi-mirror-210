import os
import shutil, errno
from distutils.errors import DistutilsFileError
from distutils.dir_util import copy_tree
from pkg_resources import resource_filename
import subprocess
import sys
import requests
import tarfile
import readline
import select
import shlex
from colorama import Fore
from colorama import Style
from . import run_all
from pathlib import Path
from timeit import default_timer as timer
from subprocess import DEVNULL
import itertools
import glob
import re

class Error(Exception):
    """Base class for other exceptions"""
    pass


class BinaryNotFoundError(Error):
    """Raised when we don't find some binary file"""
    pass


def copy(src, dest):
    try:
        shutil.copytree(src, dest)
    except OSError as e:
        # If the error was caused because the source wasn't a directory
        if e.errno == errno.ENOTDIR:
            shutil.copy(src, dest)
        else:
            print('Directory not copied. Error: %s' % e)

def get_path(path):
    return os.path.abspath(resource_filename('matchmakereft', path))

def dress_directory(dirpath):
    return os.path.join(dirpath,"")

def undress_directory(dirpath):
    return os.path.normpath(dirpath)

def list_folder(path):
    """
    Lists folder contents
    """
    if path.startswith(os.path.sep):
        # absolute path
        basedir = os.path.dirname(path)
        contents = os.listdir(basedir)
        # add back the parent
        contents = [os.path.join(basedir, d) for d in contents]
        contents = [d + os.path.sep for d in contents if os.path.isdir(d)]

    else:
        # relative path
        contents = os.listdir(os.curdir)
        basedir = os.path.abspath(os.curdir)
        contents = [os.path.join(basedir, d) for d in contents]
        contents = [d + os.path.sep for d in contents if os.path.isdir(d)]
    return contents

def completer(text, state):
    """
    Our custom completer function
    """
    options = [x for x in list_folder(text) if x.startswith(text)]
    return options[state]


readline.set_completer(completer)

if sys.platform == 'darwin':
    # Apple uses libedit.
    readline.parse_and_bind("bind -e")
    readline.parse_and_bind("bind '\t' rl_complete")
else:
    # Some tweaks for linux
    readline.parse_and_bind('tab: complete')
    readline.set_completer_delims(' \t\n`~!@#$%^&*()=+[{]}\\|;:\'",<>?')


def rep_mysty(file):

    styp=get_path('core')+"/my.sty"
    ln=len(styp)
    mt=ln//2
    fr=styp[:mt]
    ls=styp[mt:ln]
    in_file=open(file, 'r')
    ot_file=open('aux.dat', 'w')
    for line in in_file:
        if 'my.sty' in line:
            ot_file.write(" style= "+ "'" + fr +"'" + "\n")
            ot_file.write("'"+ls +"'"+" ;" + "\n")
        else:
            ot_file.write(line)
    ot_file.close()
    in_file.close()
    shutil.copyfile('aux.dat', file)
    os.remove('aux.dat')


def rp(fname):
    corepre=get_path('core')+"/"
    filename=corepre+fname
    with open(filename) as f:
        s = f.read()
        if 'REPLACEPATH' not in s:
            return

    with open(filename, 'w') as f:
        s = s.replace('REPLACEPATH', dress_directory(get_path('')))
        f.write(s)


def get_feynr_path(file_path, config):
    #print("Checking the Feynrules path")
    # Read the corresponding entry in the config file
    resp = config["USERINFO"]["Feynrules Path"]
    # If this entry is empty, ask for the path and update the config file
    if resp=="" :
        resp = input('Please enter the absolute path to FeynRules: ')
        dir = dress_directory(resp)
        feynrules = os.path.join(dir, "FeynRules.m")
        while not os.path.isfile(feynrules):
            resp=input('FeynRules.m was not found in this path, please enter the absolute path to FeynRules: ')
            dir = dress_directory(resp)
            feynrules = os.path.join(dir, "FeynRules.m")
        
        config["USERINFO"]["Feynrules Path"] = dir
        with open(file_path, 'w') as conf:
            config.write(conf)
    else:
        # If the entry is not empty, check that it work. If it does not find FR there, ask again and update the config file
        dir = dress_directory(resp)
        feynrules = os.path.join(dir, "FeynRules.m")
        #print("Current Feynrules path is " + dir)
        while not os.path.isfile(feynrules):
            resp=input('FeynRules.m was not found in this path, please enter the absolute path to FeynRules: ')
            dir = dress_directory(resp)
            feynrules = os.path.join(dir, "FeynRules.m")
            config["USERINFO"]["Feynrules Path"] = dir
            with open(file_path, 'w') as conf:
                config.write(conf)

    # In any case, return a functioning feynrules path
    return(dir)


def rp_feynr(fname, file_path, config):
    corepre=get_path('core')+"/"
    filename=corepre+fname
    with open(filename) as f:
        s = f.read()
        if 'REPLACEPATH' not in s:
            return

    resp = config["USERINFO"]["Feynrules Path"]

    if resp=="" :
        resp = input('Please enter the absolute path to FeynRules: ')
        dir = dress_directory(resp)
        feynrules = os.path.join(dir, "FeynRules.m")
        while not os.path.isfile(feynrules):
            resp=input('FeynRules.m was not found in this path, please enter the absolute path to FeynRules: ')
            dir = dress_directory(resp)
            feynrules = os.path.join(dir, "FeynRules.m")

        config["USERINFO"]["Feynrules Path"] = dir
        with open(file_path, 'w') as conf:
            config.write(conf)

    dir = dress_directory(resp)
    feynrules = os.path.join(dir, "FeynRules.m")
    while not os.path.isfile(feynrules):
        resp=input('FeynRules.m was not found in this path, please enter the absolute path to FeynRules: ')
        dir = dress_directory(resp)
        feynrules = os.path.join(dir, "FeynRules.m")
        config["USERINFO"]["Feynrules Path"] = dir
        with open(file_path, 'w') as conf:
            config.write(conf)

    with open(filename, 'w') as f:
        s = s.replace('REPLACEPATH', dir)
        f.write(s)


def rp_model(model_name, filename):
    with open(filename) as f:
        s = f.read()
        if 'MODELPATH' not in s:
            return

    with open(filename, 'w') as f:
        s = s.replace('MODELPATH', dress_directory(model_name))
        f.write(s)


def copy_models(file_path):
    fullname=os.path.join(file_path,"MatchMakerEFT")
    if os.path.isdir(fullname):
        resp=input('Directory '+os.path.join(file_path,"MatchMakerEFT")+' already present, are you sure you want to overwrite the models? [y/N]')
        if (len(resp)==0 or (resp[0] != 'y' and resp[0] != 'Y')):
            return
    src_path=get_path("data")
    src_fullname=os.path.join(src_path,"models.tar.gz")
    os.makedirs(fullname, exist_ok=True)
    filename=os.path.join(fullname, "models.tar.gz")
    shutil.copy(src_fullname, filename)
    if os.path.isfile(filename):
        tar = tarfile.open(filename,"r:gz")
        tar.extractall(fullname)
        tar.close()
        os.remove(filename)
    if os.path.isdir(os.path.join(file_path,"MatchMakerEFT")):
        print("Model directory MatchMakerEFT/ copied to "+file_path)
    else:
        print("It seems like there was a problem copying the files")


def check_executable(code):
    try:
        subprocess.check_output(code)
        #print(code+" properly installed in the system")
    except OSError as e:
        print(code+" does not seem to be in your path, please install it before matching any model")
        raise BinaryNotFoundError


def get_wolfram_command(file_path, config):
    wolframcommand=shlex.split(config["USERINFO"]["Wolfram Script Command"])
    if wolframcommand==[]:
        print("Checking location of Mathematica binaries")
        coredir=get_path("core")
        test_file=os.path.join(coredir,"test.wl")
        commandlist=['wolfram','wolframscript','Wolfram','WolframScrip']
        optionlist=['-file','-script']
        commands=[[a,b] for a in commandlist for b in optionlist]
        for com in commands:
            try:
                subprocess.run(com+[test_file], stdout=DEVNULL, stderr=DEVNULL, timeout=2.5, check=True)
                testout = subprocess.run(com+[test_file], stdout=subprocess.PIPE, stderr=DEVNULL, universal_newlines=True, check=True).stdout
                if testout == '4\n' :
                    wolframcommand=com
                    break
            except (subprocess.TimeoutExpired,FileNotFoundError) as e:
                pass

        # When successful, we add the wolframcommand to the config file
        if wolframcommand!=[]:
            config["USERINFO"]["Wolfram Script Command"]=" ".join(shlex.quote(s) for s in wolframcommand)
            with open(file_path, 'w') as conf:
                config.write(conf)
        # Otherwise, we raise an error
        else:
            print("We can't access the Wolfram Mathematica binaries. Please check that Mathematica is installed and that binaries are included in the user PATH.")
            raise BinaryNotFoundError

    return(wolframcommand)


def fix_math_path(wolframcommand):
    if wolframcommand!=[]:
        coredir=get_path("core")
        getmathpath=os.path.join(coredir,"getmathpath.wl")
        mathoutput=subprocess.run(wolframcommand+[getmathpath], stdout=subprocess.PIPE, universal_newlines=True).stdout
        dir=(mathoutput.split("\n")[0]).replace('"','')
        towrite='$Path = Join[{"'+coredir+'"}, $Path]\n'
        localdir='$Path = Join[{"."}, $Path]\n'
        with open(dir,"r") as f:
            all_lines=f.readlines()
        # we check if the correct path (called towrite) is in init.m
        # if it is remove it (no matter where it is)
        if towrite in all_lines: all_lines.remove(towrite)
        # same for local directory (localdir)
        if localdir in all_lines: all_lines.remove(localdir)
        # now add it to the end of the file
        all_lines.append(towrite)
        all_lines.append(localdir)
        #if coredir not in mathoutput:
        with open(dir.replace('"',''),"w") as myfile:
            for x in all_lines:
                myfile.write(x)#'$Path = Join[{"'+coredir+'"}, $Path]\n')


def create_config_file(file_path, config):
    if not os.path.exists(file_path) or os.stat(file_path).st_size == 0:
        with open(file_path, 'w') as configfile:
            config.write(configfile)


def create_model(model_file, wolframcommand, frpath):
    # model_file is a list ["mod1.fr","mod2.fr",...] with the FeynRules files for the model
    # we will take the name of the last file to name the model
    #os.path.normpath ensures the separators agree with os.sep for any system
    model_file_name=os.path.normpath(model_file[-1][:-3])
    #if model_file_name has the structure "dir/dir1/.../model" model_file_name_local is just "model"
    model_file_name_local=model_file_name.split(os.sep)[-1]
    if wolframcommand!=[]:
        coredir=get_path("core")
        createscript=os.path.join(coredir,"create_MM_model.wl")
        print("Creating model "+model_file_name+"_MM. This might take some time depending on the complexity of the model")
        start = timer()
        try:
            p=subprocess.run(wolframcommand+[createscript]+model_file+[frpath], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            logfile=model_file_name+".log"
            #logfile=os.path.join(model_file_name+"_MM", model_file_name_local+".log")
            f = open(logfile, "w") 
            f.write(p.stdout.decode())
            f.close()
        except subprocess.CalledProcessError:
            print("\n"+ Fore.RED + "There is a problem with the model, not all particles are defined as light or heavy using FullName->\"light\" or FullName->\"heavy\". Please make sure you define all particles properly and then create the model."+Style.RESET_ALL+"\n")
            raise Exception
        end = timer()
        # check if there is a file called model_file_name.symm
        if os.path.isfile(model_file_name+".symm"):
            shutil.copy(model_file_name+".symm",os.path.join(model_file_name+"_MM","QGRAF","model_data"))
            os.rename(os.path.join(model_file_name+"_MM","QGRAF","model_data",model_file_name_local+".symm"),os.path.join(model_file_name+"_MM","QGRAF","model_data","listareplacesymmetry"))
        # check if there is a file called model_file_name.gauge
        if os.path.isfile(model_file_name+".gauge"):
            shutil.copy(model_file_name+".gauge",os.path.join(model_file_name+"_MM","QGRAF","model_data"))
            os.rename(os.path.join(model_file_name+"_MM","QGRAF","model_data",model_file_name_local+".gauge"),os.path.join(model_file_name+"_MM","QGRAF","model_data","replacegaugedata"))
        # check if there is a file called model_file_name.herm
        if os.path.isfile(model_file_name+".herm"):
            shutil.copy(model_file_name+".herm",os.path.join(model_file_name+"_MM","QGRAF","model_data"))
            os.rename(os.path.join(model_file_name+"_MM","QGRAF","model_data",model_file_name_local+".herm"),os.path.join(model_file_name+"_MM","QGRAF","model_data","listahermiticity"))
        # check if there is a file called model_file_name.red
        if os.path.isfile(model_file_name+".red"):
            shutil.copy(model_file_name+".red",os.path.join(model_file_name+"_MM","QGRAF","model_data"))
            os.rename(os.path.join(model_file_name+"_MM","QGRAF","model_data",model_file_name_local+".red"),os.path.join(model_file_name+"_MM","QGRAF","model_data","redundancies.dat"))
        print("Model "+model_file_name+"_MM created")
        print("It took "+str(int(round(end-start)))+" seconds to create it.")
    else:
        print("can't do it!")


def get_wc(dirname):
    with open(os.path.join(dirname,"newfunctions")) as f:
        s1= f.read().splitlines()
    with open(os.path.join(dirname,"newsymbols")) as f:
        s2= f.read().splitlines()
    return([x for x in s1+s2 if "alpha" in x])

def find_index_ordering(wc,stri):
    if re.search(r'\b'+wc+r'\[\b',stri):
        return ' '.join(re.findall(r'\d',re.search(r'\b'+wc+r'\[(.*?)\]',stri).group(1)))
    else:
        return ' '

def get_vertices(dirnamex):
    dirname=dress_directory(dirnamex)
    # we use reverse sorting so that alphabar comes before alpha and then it is also used.
    wclist=sorted(get_wc(dirname),reverse=True)
    #get list of external particles
    with open(dirname+'/listexternal','r') as the_file:
        externalfields = the_file.read().strip().replace(' ','').split(',')
    midi={i:[] for i in wclist}
    templist=glob.glob(dirname+"v*list")
    for fi in templist:
        with open(fi) as f:
            s=f.read().splitlines()
            for xx in s:
                xxx=xx.split()
                areexternal=[x in externalfields for x in xxx[:-1]]
                for cc in wclist:
                    # if cc is of the form alphaXxx we want to avoid finding
                    # instances of alphaXxxbar so we remove them
                    # also we add them only if all particles are external (as given by the second condition)
                    # the original one with "in" allowed partial match, for instance alphal was found where alphall existed
                    # the new one should get only the correct matches
                    #if cc in xxx[-1].replace(cc+"bar","") and sum(areexternal)==len(areexternal):
                    if re.search(r'\b'+cc+r'\b',xxx[-1].replace(cc+"bar","")) and sum(areexternal)==len(areexternal):
                        midi[cc].append(xxx[:-1]+[find_index_ordering(cc,xxx[-1].replace(cc+"bar",""))])
    return midi


def generate_amplitudes(dirnamex):
    dirname=dress_directory(dirnamex)
    vertices=get_vertices(os.path.join(dirname,"QGRAF","model_data"))
    amplitudelist=[]
    newvertices=[];
    for ke in vertices.keys():
        if len(vertices[ke])>0:
            amplitudelist.append((min(vertices[ke], key=len))[:-1])
            newvertices.append(ke+'  '+(' '.join(min(vertices[ke], key=len)))+'\n')
    amplitudelist.sort()
    finalamplitudelist=sorted(list(amplitudelist for amplitudelist,_ in itertools.groupby(amplitudelist)),key=len)
    f=open(os.path.join(dirname,"QGRAF","model_data","amplitudes.txt"),"w+")
    for am in finalamplitudelist:
        f.write(' '.join(am)+'\n')
    f.close()
    f=open(os.path.join(dirname,"QGRAF","model_data","wc2fields.txt"),"w+")
    for am in newvertices:
        f.write(am)
    f.close()


def generate_allamplitudes(dirnamex):
    dirname=dress_directory(dirnamex)
    vertices=get_vertices(os.path.join(dirname,"QGRAF","model_data"))
    amplitudelist=[]
    newvertices=[];
    for ke in vertices.keys():
        if len(vertices[ke])>0:
            amplitudelist.extend(vertices[ke])
    amplitudelist.sort()
    finalamplitudelist=sorted(list(amplitudelist for amplitudelist,_ in itertools.groupby(amplitudelist)),key=len)
    f=open(os.path.join(dirname,"QGRAF","model_data","allamplitudes.txt"),"w+")
    for am in finalamplitudelist:
        f.write(' '.join(am)+'\n')
    f.close()


def compute_wilson_coefficients(model_file,eft_file, wolframcommand):
    if model_file[-1]=="/":
        mymodel_file=model_file[:-1]
    else:
        mymodel_file=model_file
    if eft_file[-1]=="/":
        myeft_file=eft_file[:-1]
    else:
        myeft_file=eft_file
    if wolframcommand!=[]:
        coredir=get_path("core")
        createscript=os.path.join(coredir,"compute_wilson_coefficients.wl")
        print("Computing Wilson Coefficients for model "+mymodel_file +" matched onto EFT "+myeft_file+". This might take a few minutes depending on the complexity of the model") 
        start = timer()
        subprocess.run(wolframcommand+[createscript, model_file, eft_file])
        end = timer()
        print("Wilson coefficients for Model "+mymodel_file+ " stored in "+mymodel_file+"/MatchingResult.dat")
        print("It took "+str(int(round(end-start)))+" seconds to compute them.")
        # if os.path.isfile(os.path.join(mymodel_file,"WCoutput.txt")):
        #     print("There was a problem with the matching, check details in ",os.path.join(mymodel_file,"WCoutput.txt"))
        # else:
        #     print("The matching was successful")

    else:
        print("can't do it!")



def compute_rge(model_file,eft_file, wolframcommand):
    if model_file[-1]=="/":
        mymodel_file=model_file[:-1]
    else:
        mymodel_file=model_file
    if eft_file[-1]=="/":
        myeft_file=eft_file[:-1]
    else:
        myeft_file=eft_file
    if wolframcommand!=[]:
        coredir=get_path("core")
        createscript=os.path.join(coredir,"compute_rge_model_to_eft.wl")
        print("Computing the RGEs for UV EFT "+mymodel_file +" onto EFT "+myeft_file+". This might take a few minutes depending on the complexity of the model") 
        start = timer()
        subprocess.run(wolframcommand+[createscript, model_file, eft_file])
        end = timer()
        print("It took "+str(int(round(end-start)))+" seconds to compute them.")
        # if os.path.isfile(os.path.join(mymodel_file,"WCoutput.txt")):
        #     print("There was a problem with the matching, check details in ",os.path.join(mymodel_file,"WCoutput.txt"))
        # else:
        #     print("The matching was successful")

    else:
        print("can't do it!")



