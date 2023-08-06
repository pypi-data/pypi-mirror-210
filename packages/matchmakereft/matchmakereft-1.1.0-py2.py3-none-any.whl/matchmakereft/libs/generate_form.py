import re
from . import file as jsf
import subprocess
import glob
import os
import sys
import itertools
from . import functions as func
from functools import reduce

# This takes a .out file called fi and checks the maximum power of momenta in the amplitude
def get_pnmax_file(fi):
    teo=subprocess.run("grep -E -o 'sSS\^.|sSS' "+fi, shell=True, capture_output=True)
    ou=str(teo.stdout,'utf-8').split('\n')
    return max([0]+[int(x.replace("sSS^","").replace("sSS","1")) for x in ou if len(x)>0])


# This takes a QGRAF model file and extract the list of bosonic particles
def get_bosons(filename):
    with open(filename) as f:
        lines = f.read().splitlines()
    bolist=[]
    for x in lines:
        if ("+]" in x):
            bolist.append(x.split(',')[0].strip().replace("[",""))
            if (x.split(',')[0].strip().replace("[","")!=x.split(',')[1].strip().replace("[","")):
                bolist.append(x.split(',')[1].strip().replace("[",""))
    return bolist


# This takes a MM model called model and checks the maximum dimension of
# the amplitudes computed in that model. It should be used on the EFT model
# after having run run_all on it
def get_maxdim(model):
    modeldir=os.path.join(model,"FORM","proc_0loop")
    bosons=get_bosons(os.path.join(model,'QGRAF','model'))
        

    filelist=glob.glob(os.path.join(modeldir,"*.out"))
    maxdim=0;
    for fi in filelist:
        process=fi.split('/')[-1][:-4]
        particles=process.split('_')
        bparticles=[x for x in particles if x in bosons]
        dim=int((3*len(particles)-len(bparticles))//2)
        nmom=get_pnmax_file(fi)
        maxdim=max(maxdim,dim+nmom)
    print("Maximum dimension for model ",model," is ",maxdim)
    return(maxdim)


# This splits an expression exp that is a sum of monomials into a list of monomials
def split_expression_in_monomials(exp):
    return exp.replace('+','MATCHMAKERMATCHMAKER').replace('-','MATCHMAKERMATCHMAKER').split('MATCHMAKERMATCHMAKER')


# This gets the wilson coefficient and the power of momenta present in monomial exp
def get_wc_momentum_power_monomial(exp):
    alphalist=re.findall(r'\balpha\w*\b',exp)
    if len(alphalist)==1:
        return [alphalist[0],len(re.findall(r'\bpp\d\b',exp))]
    else:
        return['',0]

def get_dimension_wc(model):
    dict={}
    problems=0
    bosons=get_bosons(os.path.join(model,'QGRAF','model'))
    filelist=glob.glob(os.path.join(model,'QGRAF','model_data','v*list'))
    for fi in filelist:
        with open(fi) as f:
            lines = f.read().splitlines()
        for xx in lines:
            particles=xx.split()[:-1]
            bparticles=[x for x in particles if x in bosons]
            dimparts=int((3*len(particles)-len(bparticles))//2)
            fr=split_expression_in_monomials(xx.split()[-1])
            for fri in fr:
                [wc,po]=get_wc_momentum_power_monomial(fri)
                dimwc=4-po-dimparts
                if len(wc)>0:
                    if not wc in dict:
                        dict[wc]=[dimwc]
                    else:
                        if dimwc != dict[wc][-1]:
                            dict[wc].append(dimwc)
                            problems=1
    if problems==0:
        return ['id '+x+' = '+x+'*LAMBDA^('+str(dict[x][0])+');' for x in dict.keys()]
    else:
        return "problem"


def write_wc_dimension(model):
    modeltowrite=[os.path.join(model,'FORM','proc_0loop','wcdimension.dat'),os.path.join(model,'FORM','proc_1loop','wcdimension.dat')]
    for m2w in modeltowrite:
        if not os.path.isfile(m2w):
            fi = open(m2w,'w')
            fi.write('\n'.join(get_dimension_wc(model)))
            fi.close()
    
# This will be used to replace the correct spatial indices
# The indices we are replacing are always inside parenthesis so they are
# either right after [ or right after ,
# by forcing a [ or , before we ensure that no replacement in variable names
# happens
# since we first replace [ with ( we use ( everywhere
def JSP_replace(st,ilist,plist,indexlist,dummyrepl):
    repl=[('[','('),(']',')')]
    for x in dummyrepl:
        repl.extend([x])
    for x in indexlist.replace(" ","").replace("\n","").split(","):
        repl.extend([('('+x+x+str(i+1),'('+x+str(t)) for (i,t) in enumerate(ilist)])
        repl.extend([(','+x+x+str(i+1),','+x+str(t)) for (i,t) in enumerate(ilist)])
    repl.extend([('(pp'+str(i+1),'('+t) for (i,t) in enumerate(plist)])
    repl.extend([(',pp'+str(i+1),','+t) for (i,t) in enumerate(plist)])
    return  reduce(lambda a, kv: a.replace(*kv), repl, st)


def allpos(i):
    res=int(i)
    if res<0:
        res += 100
    return str(res)


def feynman_rules(dirname):
    # This is a dictionary of dictionaries encoding all the Feynman rules
    alldicts={}
    templist=glob.glob(dirname+"QGRAF/model_data/*list")
    allkeys=[x.split('/')[-1][:-4] for x in templist]
    for key in allkeys:
        filename=dirname+"QGRAF/model_data/"+key+"list"
        tempdict={}
        for line in open(filename):
            tempdict[" ".join(line.split()[:-1])]=line.split()[-1]
        alldicts[key]=tempdict
    return alldicts


def read_new_params(dirname):
    # define new parameters
    with open(dirname+'QGRAF/model_data/listparam','r') as f:
        all_lines = f.readlines()
    return ', '.join([x.replace('\n','') for x in all_lines])


def read_new_functions(dirname):
    # define new parameters
    with open(dirname+'QGRAF/model_data/newfunctions','r') as f:
        all_lines = f.readlines()
    return ', '.join([x.replace('\n','') for x in all_lines])


def read_new_gauge_functions(dirname):
    # define new parameters
    with open(dirname+'QGRAF/model_data/newgaugefunctions','r') as f:
        all_lines = f.readlines()
    return ', '.join([x.replace('\n','') for x in all_lines])


def read_new_flavor_functions(dirname):
    # define new parameters
    with open(dirname+'QGRAF/model_data/newflavorfunctions','r') as f:
        all_lines = f.readlines()
    return ', '.join([x.replace('\n','') for x in all_lines])


def read_new_flavor_mass_functions(dirname):
    # define new parameters
    with open(dirname+'QGRAF/model_data/newflavormassfunctions','r') as f:
        all_lines = f.readlines()
    return ', '.join([x.replace('\n','') for x in all_lines])


def read_new_symbols(dirname):
    # define new parameters
    with open(dirname+'QGRAF/model_data/newsymbols','r') as f:
        all_lines = f.readlines()
    return ', '.join([x.replace('\n','') for x in all_lines])


def read_new_indices(dirname):
    # define new parameters
    with open(dirname+'QGRAF/model_data/newindices','r') as f:
        all_lines = f.readlines()
    return ', '.join([x.replace("\n","").split("=")[0] for x in all_lines])


def read_new_heavy_flavor_indices(dirname):
    # define new parameters
    with open(dirname+'QGRAF/model_data/newheavyflavorindices','r') as f:
        all_lines = f.readlines()
    return [x.replace("\n","").split("=")[0] for x in all_lines]


def read_new_indices_with_dims(dirname):
    # define new parameters
    with open(dirname+'QGRAF/model_data/newindices','r') as f:
        all_lines = f.readlines()
    return ', '.join([x.replace('\n','') for x in all_lines])


def read_new_gauge_indices_with_dims(dirname):
    # define new parameters
    with open(dirname+'QGRAF/model_data/newgaugeindices','r') as f:
        all_lines = f.readlines()
    return ', '.join([x.replace('\n','').replace('\t','=') for x in all_lines])


def read_light_masses(dirname):
    # define light masses
    with open(dirname+'QGRAF/model_data/listlightmass','r') as f:
        all_lines = f.readlines()
    answer=""
    if len(all_lines)>0:
        answer=', '.join(all_lines[0].split())
    return answer


def read_heavy_masses(dirname):
    # define heavy masses
    with open(dirname+'QGRAF/model_data/listheavymass','r') as f:
        all_lines = f.readlines()
    answer=""
    if len(all_lines)>0:
        answer=', '.join(all_lines[0].split())
    return answer


def write_aux_files(dirname,filename,alldicts,maxdim):
    process=filename.split('/')[-1][:-4]
    particles=process.split('_')
    bosons=get_bosons(dirname+'QGRAF/model')
    bparticles=[x for x in particles if x in bosons]
    dim=int((3*len(particles)-len(bparticles))//2)
    thenmax=maxdim-dim
    looporder=filename.split('/')[-2]
    formdir=dirname+'FORM/'+looporder+'/'
    if not os.path.isdir(formdir):
        subprocess.call("mkdir "+formdir,shell=True)

    newindices=read_new_indices(dirname)
    listnewindices=[x for x in newindices.replace(" ","").split(',')]
    diagnum=1
    lastline=0
    outputline=''

    outputfilename=formdir+process+'.aux' # one diagram at a time

    if not os.path.isfile(outputfilename):
        of = open(outputfilename,"w")
        dummyi=0
        dummymumu=0
        dummies={x:0 for x in listnewindices}

        for line in open(filename):
            dummyi+=1
            datalinetemp=line.rstrip().replace('(',',').replace(')','').replace('*','').split(',')
            if datalinetemp[-1]=='' and len(datalinetemp)>1:
                # last line of the current diagram
                lastline=1
                dataline=datalinetemp[:-1]
            else:
                dataline=datalinetemp

            # Now we start with the proper replacements
            if dataline[0]=='' and len(dataline)>1:
                # numerical factor
                outputline += "("+dataline[1].replace("+","")+")"
            elif len(dataline)>1:
                [op,fields,indices0,ppi]=dataline[0].strip(),dataline[1::3],dataline[2::3],dataline[3::3]
                indices = [allpos(ii) for ii in indices0]
                dummyrepl=[]
                for xx in listnewindices:
                    if (xx+xx+"minus" in alldicts[op][" ".join(fields)]):
                        maxhere=max([x for x in re.findall(r"[\w']+",alldicts[op][" ".join(fields)].replace("mumumu","mumu")) if xx+xx+"minus" in x]).replace(xx+xx+"minus","")
                        for i in range(int(maxhere)):
                            dummyrepl.append((xx+xx+"minus"+str(i+1),xx+"minus"+str(i+1+dummies[xx])))
                        dummies[xx]=dummies[xx]+int(maxhere)

                outputline += "*("+JSP_replace(alldicts[op][" ".join(fields)],indices,ppi,newindices,dummyrepl)+")"

            if lastline==1:
                of.write("id diags"+str(diagnum)+" = "+outputline+";\n\n")
                diagnum += 1
                outputline=''
                lastline = 0
                dummyi=0
                dummymumu=0
                dummies={x:0 for x in listnewindices}


        of.close()
    return diagnum,process,thenmax,formdir


def generate_index_definition(newindices,newgaugeindices,form_directory):

    data=""
    filelist=glob.glob(os.path.join(form_directory,"*aux"))
    for filename in filelist:
        with open(filename) as fi:
            data+=fi.read()
    theindices=[x.split("=") for x in newindices.replace(" ","").split(',')]
    theindices.sort()
    theshortindices=list(theindices for theindices,_ in itertools.groupby(theindices))

    thegaugeindices=[]
    if len(newgaugeindices) >0:
        thegaugeindices=[x.split("=") for x in newgaugeindices.replace(" ","").split(',')] 
    
    stri="i <THEINDEX1=INDEXDIM>, ... , <THEINDEX100=INDEXDIM>, <THEINDEXminus1=INDEXDIM>, ... , <THEINDEXminus100=INDEXDIM>THEEXTRAINDICES;\nset THEINDEXi: THEINDEX1, ... , THEINDEX100, THEINDEXminus1, ... , THEINDEXminus100THE2EXTRAINDICES;\n\n"
    defs=""
    for x in theshortindices:
        te=re.findall(r'[^a-zA-Z]'+x[0]+x[0]+r'[^(inus)][a-zA-Z]*\d+',data)
        if len(te)>0:
            finalte=list(set([re.sub(r'\W+','',xx) for xx in te]))
            finaltee=[xx+'='+x[1] for xx in finalte]
            finaltee2=', '.join(finalte)
            if len(finaltee)>0:
                requete=', '.join(finaltee)
                THEEXTRAINDICESSUS=', '+requete
                THE2EXTRAINDICESSUS=', '+finaltee2
            else:
                THEEXTRAINDICESSUS=''
                THE2EXTRAINDICESSUS=''
        else:
            THEEXTRAINDICESSUS=''
            THE2EXTRAINDICESSUS=''
        defs +=stri.replace("THEINDEX",x[0]).replace("INDEXDIM",x[1]).replace("THEEXTRAINDICES",THEEXTRAINDICESSUS).replace("THE2EXTRAINDICES",THE2EXTRAINDICESSUS)
    for x in [x for x  in thegaugeindices if x not in theindices]:
        te=re.findall(r'[^a-zA-Z]'+x[0]+x[0]+r'[^(inus)][a-zA-Z]*\d+',data)
        if len(te)>0:
            finalte=list(set([re.sub(r'\W+','',xx) for xx in te]))
            finaltee=[xx+'='+x[1] for xx in finalte]
            finaltee2=', '.join(finalte)
            if len(finaltee)>0:
                requete=', '.join(finaltee)
                THEEXTRAINDICESSUS=', '+requete
                THE2EXTRAINDICESSUS=', '+finaltee2
            else:
                THEEXTRAINDICESSUS=''
                THE2EXTRAINDICESSUS=''
        else:
            THEEXTRAINDICESSUS=''
            THE2EXTRAINDICESSUS=''
        defs +=stri.replace("THEINDEX",x[0]).replace("INDEXDIM",x[1]).replace("THEEXTRAINDICES",THEEXTRAINDICESSUS).replace("THE2EXTRAINDICES",THE2EXTRAINDICESSUS)


    return(defs)


def generate_heavy_flavor_deltas(newheavyflavorindices):
    strif="id deltaF(mu1?THEINDEXi,mu2?THEINDEXi)=deltaFF(mu1,mu2);\n"
    defs=""
    for x in newheavyflavorindices:
        defs +=strif.replace("THEINDEX",x)
    return(defs)


def generate_id_deltas(newindices,newgaugeindices):
    theindices=[x.split("=") for x in newindices.replace(" ","").split(',')]
    thegaugeindices=[]
    if len(newgaugeindices) >0:
        thegaugeindices=[x.split("=") for x in newgaugeindices.replace(" ","").split(',')] 
    theflavorindices=[x for x in theindices if x not in thegaugeindices]
    stri="id d_(mu1?THEINDEXi,mu2?THEINDEXi)=dd(INDEXDIM,mu1,mu2);\n"
    strif="id d_(mu1?THEINDEXi,mu2?THEINDEXi)=ddF(INDEXDIM,mu1,mu2);\n"
    defs=""
    gaugedims=sorted(list(set([int(x[1]) for x in thegaugeindices])))
    for x in thegaugeindices:
        defs +=stri.replace("THEINDEX",x[0]).replace("INDEXDIM",x[1])
    for x in theflavorindices:
        defs +=strif.replace("THEINDEX",x[0]).replace("INDEXDIM",x[1])
    for j in gaugedims:
        defs +="id e_(mu1?,...,mu"+str(j)+"?)=ee("+str(j)+",mu1,...,mu"+str(j)+");\n"
    return(defs)


def generate_call_dummy_indices(newindices):
    theindices=[x.split("=") for x in newindices.replace(" ","").split(',')]
    stri="#call dummyindices(THEINDEXi,THEINDEX)\n"
    defs=""
    for x in theindices:
        defs +=stri.replace("THEINDEX",x[0])
    return(defs)


def generate_form(dirname0,isEFT,maxdim):
    corepre=func.get_path('core')+"/"
    if os.path.isdir(dirname0):
        dirname=jsf.proper_dir_path(dirname0)
        write_wc_dimension(dirname)


        alldicts=feynman_rules(dirname)
        # Go through all the QGRAF files
        if isEFT:
            # EFT do only tree level
            filelist=glob.glob(dirname+"QGRAF/proc_0loop/*qgf")
        else:
            filelist=glob.glob(dirname+"QGRAF/proc_*loop/*qgf")
        for filename in filelist:
            diagnum,process,thenmax,formdir=write_aux_files(dirname,filename,alldicts,maxdim)
            numparticles=len(process.split("_"))
            # check if form file is there, if it is do not do anything
            if not os.path.isfile(formdir+process+'.frm'):
                ## Let's now write the form skeleton program
                myrepl= ("THELAMBDAINVERSEMAX",str(3-int(maxdim))),('COREPRE',corepre),('MM_NUMBER_OF_PARTICLES',str(numparticles)),('MM_NUMBER_OF_DIAGRAMS',str(diagnum-1)),("THENMAX",str(thenmax)),("FILE_WITH_DIAGRAMS",process),("PROCESS",process.replace("_","").replace("[","").replace("]",""))
                jsf.dress_skeleton(myrepl, corepre+'skeleton_parallel_new.frm',formdir+process+'.frm')

        newgaugefunctions=read_new_gauge_functions(dirname)
        newflavorfunctions=read_new_flavor_functions(dirname)
        newflavormassfunctions=read_new_flavor_mass_functions(dirname)
        newfunctions=read_new_functions(dirname)
        newmassfunctions=list(set(newfunctions.replace(" ","").split(","))-set(newflavorfunctions.replace(" ","").split(","))-set(newgaugefunctions.replace(" ","").split(",")))
        newsymbols=read_new_symbols(dirname)
        if len(newmassfunctions)>0:
            newsymbols=newsymbols+";\nCF "+", ".join(newmassfunctions)
        newindices=read_new_indices_with_dims(dirname)
        newheavyflavorindices=read_new_heavy_flavor_indices(dirname)
        newgaugeindices=read_new_gauge_indices_with_dims(dirname)
        heavy_flavor_deltas=generate_heavy_flavor_deltas(newheavyflavorindices)
        id_deltas=generate_id_deltas(newindices,newgaugeindices)
        call_dummy_indices=generate_call_dummy_indices(newindices)
        lightmasses=read_light_masses(dirname)
        heavymasses=read_heavy_masses(dirname)
        # isnoteft is 0  (false) if there are no heavy masses (and therefore is an eft)
        # and different from 0 (true) if there are heavy masses (and therefore is not an eft)
        # note that on RGEMaker mode for the 1 loop calculation
        # isEFT will be False but isnoteft should be also false (0)
        # If isnoteft='0' then 4D properties of the gamma matrices are used
        # this should be used only in RGEMaker mode
        # we set it to a non-zero value and then, if we have to do one-loop calculations
        # we fix it to its real value (0 for RGEMaker mode and something different from 0 for MatchMaker mode)
        isnoteft='1'
        # all the aux files have been written already, we can get the extra indices used now
        if isEFT:
            # EFT, do only tree level
            formdirlist=glob.glob(dirname+"FORM/proc_0*")
        else:
            formdirlist=glob.glob(dirname+"FORM/proc_*")
            isnoteft=str(len(heavymasses))
        if (len(formdirlist) == 2):
            extrasymbol="esfull"
        else:
            extrasymbol="eseft"
        for fdir in formdirlist:
            loopord=fdir.split('_')[-1].replace('loop','')
            indexdefinition=generate_index_definition(newindices,newgaugeindices,fdir)
            myrepl= ('DUMMY_INDICES',call_dummy_indices),('ID_DELTAS',id_deltas),('HF_DELTAS',heavy_flavor_deltas),('NEW_SYMBOLS',newsymbols),('NEW_GAUGE_FUNCTIONS',newgaugefunctions),('NEW_FLAVOR_FUNCTIONS',newflavorfunctions),('NEW_FLAVOR_MASS_FUNCTIONS',newflavormassfunctions),("INDEX_DEFINITION",indexdefinition),('EXTRA_SYMBOLS',extrasymbol),('LIGHTMASSESSET',lightmasses),('HEAVYMASSESSET',heavymasses),('ISNOTEFT',isnoteft),('LOOPORDER',loopord)
            #print(fdir+'/generaldefs.h')
            jsf.dress_skeleton(myrepl, corepre+'generaldefs_skeleton.h',fdir+'/generaldefs.h')
    else:
        print("not a valid directory")
