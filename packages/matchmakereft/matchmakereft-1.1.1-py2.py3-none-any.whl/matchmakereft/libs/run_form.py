from itertools import zip_longest
import subprocess
import glob
import sys
import os
import re
import math
from colorama import Fore
from colorama import Style
import tqdm
#from tqdm.auto import tqdm, trange
from time import sleep
from . import file as jsf
import multiprocessing as mp
from . import functions as func


# The two functions below are used to split a long text file into smaller files with a maximum number of lines
def grouper(n, iterable, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx
    args = [iter(iterable)] * n
    return zip_longest(fillvalue=fillvalue, *args)

def py_split(big_file,num_lines):
    nlibf = sum(1 for line in open(big_file))
    zfilli=len(str(math.ceil(nlibf/num_lines)))
    filelist=[]
    with open(big_file) as f:
        for i, g in enumerate(grouper(num_lines, f, fillvalue=''), 1):
            #filelist.append(big_file.replace('.aux','')+'.parts.'+str(i).zfill(zfilli)+'.aux')
            filelist.append(big_file.replace('.aux','')+'.parts.'+str(i)+'.aux')
            with open(filelist[-1], 'w') as fout:
                fout.writelines(g)
    return(filelist)

# This function is used to get the first, last, number of file and total number of diagrams in an .aux file
def get_diagram_indices(fi):
    with open(fi,'r') as f:
        all_lines = f.readlines()
    dia = [x.split()[1].replace('diags','') for x in all_lines if 'diag' in x]
    return (dia[0],dia[-1],fi.split('.')[-2],str(1+int(dia[-1])-int(dia[0])))


# This function takes an .aux file called bif and split it in smaller files with
# a maximum of diagchunk diagrams
# If the number of diagrams is larger than diagchunk the splitting is performed
# and the corresponding process.parts.x.aux and process.parts.x.frm are created
# also a file called process.frm.reunite is created to be run latter to collect the terms.
def split_large_process(bif,diagchunk):
    corepre=func.get_path('core')+"/"
    tot_num_diags=get_diagram_indices(bif)[-1]
    if diagchunk >= int(tot_num_diags):
        return
    #split aux file
    nli=diagchunk*2
    processunderscore=bif.replace('.aux','')
    processnounderscore=processunderscore.replace('_','')
    partfil=py_split(bif,nli)
    #now split form file
    for fi in partfil:
        first_diag,last_diag,fi_name,num_diags_fi=get_diagram_indices(fi)
        offset=str(int(first_diag)-1)
        repl=(('#define NumDiags "'+tot_num_diags+'"','#define NumDiags "'+num_diags_fi+'"'),("diags'i'","diags{"+offset+"+'i'}"),(bif,fi),("ampl"+bif.replace("_","").replace(".aux",""),"ampl"+bif.replace("_","").replace(".aux","")+"parts"+fi_name),(bif.replace(".aux",".out"),bif.replace(".aux",".parts."+fi_name+".out")),('#call collectterms','G amp'+fi_name+'='+"ampl"+bif.replace("_","").replace(".aux","")+"parts"+fi_name+';\n.store\nsave '+processunderscore+'.parts.'+fi_name+'.sav amp'+fi_name+';\n#call collectterms'))
        jsf.dress_skeleton(repl,bif.replace("aux","frm"),fi.replace(".aux","")+".frm")
    #rename the original .frm file so that we don't run it
    os.rename(bif.replace("aux","frm"),bif.replace("aux","frm.original"))
    #create a file to collect the output of the split calculation
    repl2=(('NUMBEROFFILES',str(len(partfil))),('COREPRE', corepre),("PROCESSNOU",processnounderscore),("PROCESSYESU",processunderscore))
    jsf.dress_skeleton(repl2,corepre+'skeleton_frm_reunite',processunderscore+".frm.reunite")

# This function goes through all the .aux files in the current directory and
# splits them in chunkdiagsh files if needed
def split_aux(chunkdiagsh):
    aux_file_list=glob.glob("*.aux")
    #print("aux_file_list=",aux_file_list)
    for bif in aux_file_list:
        #print("doing file ",bif)
        numlines=sum(1 for line in open(bif))
        #print("number of lines",numlines)
        #split files with more than chunkdiags
        if numlines >0:
            split_large_process(bif,chunkdiagsh)

# This function checks if some of the processes have been split
# and collect the results
def collect_parts(currentdir,newindices,dirname,lo):
    #print("directory=",os.getcwd())
    #run the reunite files 
    reun_files=glob.glob("*frm.reunite")
    #rename them
    for fi in reun_files:
        os.rename(fi,fi.replace("frm.reunite","frm"))
    newreun_files=[fi.replace("frm.reunite","frm") for fi in reun_files]
    #print("reun files=",newreun_files)
    ### ESTA PARTE TENEMOS QUE ARREGLARLA!!!!
    for fil in newreun_files:
        run_form_file(fil,currentdir,newindices,dirname,lo)
    #run_parallel_form(newreun_files)
    #recover the original .frm files
    original_files=glob.glob("*frm.original")
    for fi in original_files:
        os.rename(fi,fi.replace(".original",""))
    #clean up at the end
    #print("tete=",glob.glob("*"))
    filestodelete=glob.glob("*parts*")
    #print(filestodelete)
    for fi in filestodelete:
        os.remove(fi)

        
def better_log(file,indexlist):
    if not os.path.isfile(file+".mat"):
        with open(file) as f:
            lines = f.read().splitlines()
            i0=0
            i1=0
            for i,li in enumerate(lines):
                if "ampl" in li:
                    i0=i;
                if ";" in li:
                    i1=i;
        lin=''.join([x.strip() for x in  lines[i0:i1+1]])
        for i in range(20):
            lin=lin.replace("f"+str(i+1),"fl"+str(i+1))
        lin=lin.replace("e_","ee")
        lin=lin.replace("[MM.epsi]","epsilonbar")
        lin=re.sub(r'd_\(([0-9a-zA-Z]*),([0-9a-zA-Z]*)\)', r'dd[\1,\2]', lin)
        lin=re.sub(r'esfull\(([0-9]*)\)', r'esfull[\1]', lin)
        lin=re.sub(r'eseft\(([0-9]*)\)', r'eseft[\1]', lin)
        lin=lin.replace("=","->")
        lin=lin.replace(";",",")
        lin="{"+lin+"}"
        lin=lin.replace(",}","}")
        with open(file+".mat","w") as ff:
            ff.write(lin)

def read_new_indices(dirname):
    # define new parameters
    with open(dirname+'QGRAF/model_data/newindices','r') as f:
        all_lines = f.readlines()
    return ', '.join([x.split("=")[0] for x in all_lines])


def run_form_file(fil,currentdir,newindices,dirname,lo):
    
    # we check for the .out file because the .log is created even if form doesnt run smoothly
    if not os.path.isfile(fil[:-4]+".out"):
        try:
            p=subprocess.run(("form -F "+fil).split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        except subprocess.CalledProcessError as E:
            # there was a problem, return the exception that will be handled by the calling function
            return Exception("\n"+ Fore.RED + "There was an error when running "+' '.join(E.args[1])+" in "+dirname+"FORM/proc_"+lo+"loop/, please check!"+Style.RESET_ALL+"\n")
        # If everything goes well do the better logs
        if os.path.isfile(fil[:-4]+".log"):
            better_log(fil[:-4]+".log",newindices)
        if os.path.isfile(fil[:-4]+".out"):
            better_log(fil[:-4]+".out",newindices)


def run_form(dirname0,isEFT,parallel,chunksize):
    if os.path.isdir(dirname0):
        dirname=jsf.proper_dir_path(dirname0)
        newindices=read_new_indices(dirname)
        currentdir=os.getcwd()
        for (lo, bo,mes) in [("0",False,"tree-level"),("1",isEFT,"one-loop")]:
            if os.path.isdir(dirname+"FORM/proc_"+lo+"loop/") and not bo:
                os.chdir(dirname+"FORM/proc_"+lo+"loop/")
                #split the aux (and form) diagrams
                split_aux(chunksize)
                aux = glob.glob("*frm")
                nam = str(math.ceil(math.log10(len(aux)+1)))
                frm = "{n_fmt:"+nam+"}/{total_fmt:"+nam+"} amplitudes | {percentage:3.0f}% |{bar:20}| {desc}" 
                arglist=[[fi,currentdir,newindices,dirname,lo] for fi in aux]
                print("Computing the "+mes+" amplitudes for model "+dirname[:-1])
                with tqdm.tqdm(total=len(arglist), bar_format=frm) as pbar:
                    if parallel:
                        with mp.Pool() as pool:
                            def callback(*args):
                                #callback
                                pbar.update()
                                return
                            results =[ pool.apply_async(run_form_file, args=ar, callback=callback) for ar in arglist]
                            results = [r.get() for r in results]

                    else:
                        results=[]
                        for ar in arglist:
                            results.append(run_form_file(*ar))
                            pbar.update()
                        #results =[ run_form_file(*ar) for ar in arglist]
                        #results =[ print(*ar) for ar in arglist]



                    for r in results:
                        if isinstance(r,Exception):
                            collect_parts(currentdir,newindices,dirname,lo)
                            os.chdir(currentdir)
                            raise(r)
                    #os.chdir(currentdir)
                #print("collecting split parts")
                collect_parts(currentdir,newindices,dirname,lo)
                # not sure if we need this chdir here
                os.chdir(currentdir)
    else:
        print("not a valid directory")

