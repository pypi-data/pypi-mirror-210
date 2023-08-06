from . import file as jsf
import os
import subprocess
import sys
import glob
from colorama import Fore
from colorama import Style
from . import functions as func


def write_one_point_function(partlist,dirname):
    # QGRAF does not do tree-level one point functions (tadpoles) so we do them ourselves
    # partlist is a list of length 1 with the name of the particle involved
    # we only do it at tree level if there is an entry in v1list
    resp="diags:=[\nNULL]:";
    if os.path.isfile(dirname+'QGRAF/model_data/v1list'):
        with open(dirname+'QGRAF/model_data/v1list','r') as the_file:
            lines = the_file.read().strip().splitlines()
        v1parts=[[li.split()[0]] for li in lines]
        if (partlist in v1parts):
            resp="diags:=[\n\n(+1)\n cpol("+partlist[0]+"(-1,p1))*\n\n v1("+partlist[0]+"(-1,p1)),\nNULL]:"
    return resp
    
def write_two_point_function(partlist,dirname):
    # QGRAF does not do tree-level two point functions so we do them ourselves
    # partlist is a list of length 2 with the names of the two particles involved
    # we only do it for the effective theory, that is for models with no heavy particles
    # as for models with heavy particles there is no tree level contribution that involves
    # heavy particles

    #get the sign
    # we go through the propagators and get the sign
    with open(dirname+'QGRAF/model','r') as the_file:
        lines = the_file.read().strip().splitlines()
    thelines=[li.strip().replace('[','').replace(']','').split(',') for li in lines if '+' in li or '-' in li]
    signo=''

    #get the sign
    # we go through the propagators and get the sign
    with open(dirname+'QGRAF/model_data/listlightfermions','r') as the_file:
        fermionlines = the_file.read().strip().replace(' ','').split(',')
    with open(dirname+'QGRAF/model_data/listlight','r') as the_file:
        lines = the_file.read().strip().replace(' ','').split(',')
    if partlist[0] in fermionlines or partlist[1] in fermionlines:
        signo='(-1)*'
    elif partlist[0] in lines or partlist[1] in lines:
        signo='(+1)*'

    with open(dirname+"QGRAF/model_data/listheavy","r") as the_file:
        # check if there are heavy particles
        # noheavy=True if there are no heavy particles in the spectrum
        lines = the_file.read().strip().splitlines()
        noheavy=len(lines)==0

    if len(signo)>1:
        # we only proceed if the sign has been computed properly
        # we now check the order of the 2-point vertex
        # read two-point vertices
        with open(dirname+'QGRAF/model_data/v2list','r') as the_file:
            lines = the_file.read().strip().splitlines()
        v2parts=[(li.split())[:2] for li in lines]

        #if (partlist in v2parts) and noheavy:
        if (partlist in v2parts):
            #correct order
            return "diags:=[\n\n"+signo+"\n cpol("+partlist[0]+"(-1,p1))*\n cpol("+partlist[1]+"(-3,p2))*\n\n v2("+partlist[0]+"(-1,p1),"+partlist[1]+"(-3,p2)),\nNULL]:"
        elif (list(reversed(partlist)) in v2parts):
            #opposite order
            if '-' in signo:
                # sign is -*-=+ if in reverse order 
                signo='(+1)*'
            return "diags:=[\n\n"+signo+"\n cpol("+partlist[0]+"(-1,p1))*\n cpol("+partlist[1]+"(-3,p2))*\n\n v2("+partlist[1]+"(-3,p2),"+partlist[0]+"(-1,p1)),\nNULL]:"
        else:
            return "diags:=[\nNull]:"
    else:
        return signo

def run_qgraf(listofparticles,dirname0,isEFT):
    if os.path.isdir(dirname0):
        if os.path.isfile(listofparticles):
            dirname=jsf.proper_dir_path(dirname0)
            if isEFT:
                filelist=glob.glob(dirname+"QGRAF/qgraf.skeleton.0loop.dat")
            else:
                filelist=glob.glob(dirname+"QGRAF/qgraf.skeleton.*loop.dat")                
            with open(listofparticles) as f:
                lines = f.read().strip().splitlines()
            for li in lines:
                outfile=" ".join(li.split()).replace(" ","_").replace("[","").replace("]","")
                partlist=','.join(li.split())
                for fil in filelist:
                    outputdirname=dirname+"QGRAF/proc_"+fil.split('/')[-1].split('.')[-2]+"/"
                    if not os.path.isdir(outputdirname):
                        subprocess.run(("mkdir "+outputdirname).split())
                    outputfilename=dirname+"QGRAF/proc_"+fil.split('/')[-1].split('.')[-2]+"/"+outfile+".qgf"
                    
                    if not os.path.isfile(outputfilename) and "0" in fil.split('.')[-2] and len(li.split()) == 2:
                        # qgraf does not do tree level two point functions, we do it ourselves
                        twop=write_two_point_function(li.split(),dirname)
                        if len(twop)>1:
                            with open(outputfilename,'w') as the_file:
                                the_file.write(twop)
                    elif not os.path.isfile(outputfilename) and "0" in fil.split('.')[-2] and len(li.split()) == 1:
                        # qgraf does not do tree level one point functions, we do it ourselves
                        onep=write_one_point_function(li.split(),dirname)
                        if len(onep)>1:
                            with open(outputfilename,'w') as the_file:
                                the_file.write(onep)
                    elif not os.path.isfile(outputfilename):
                        themodel=dirname+"QGRAF/model"
                        subprocess.run(("cp "+themodel+" ./model").split())
                        myrepl=("LISTOFPARTICLES",partlist),("THEMODEL",'model')
                        jsf.dress_skeleton(myrepl,fil,'qgraf.dat')
                        func.rep_mysty('qgraf.dat')
                        if os.path.isfile('OUTPUTFILE'):
                            subprocess.run(("rm OUTPUTFILE").split())
                        p=subprocess.run(("qgraf").split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                        logfile=outputfilename[:-3]+'log'
                        f = open(logfile, "w") 
                        f.write(p.stdout.decode())
                        f.close()
                        if p.stdout.decode().find('error') > 0:
                            subprocess.run(("rm model").split())
                            subprocess.run(("rm qgraf.dat").split())
                            level=fil.split('/')[-1].split('.')[-2]
                            raise Exception("\n"+ Fore.RED +"There was an error with QGRAF computing the amplitude "+outputfilename.split('/')[-1][:-4].replace('_',' ')+" at "+level+". See the log file "+logfile+Style.RESET_ALL+"\n")
                        else: 
                            subprocess.run(("mv OUTPUTFILE "+outputfilename).split())
                            subprocess.run(("rm model").split())
                            subprocess.run(("rm qgraf.dat").split())
        else:
            print("not a valid list of particles")
    else:
        print("not a valid directory")


