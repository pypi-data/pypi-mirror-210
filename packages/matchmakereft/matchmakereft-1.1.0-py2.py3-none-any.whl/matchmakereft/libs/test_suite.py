import shutil
import os
import subprocess
import datetime
import tarfile
from . import functions as func
from . import match_model


def ts_up(dest):
    #go one directory up (to the original working directory)
    os.chdir(os.path.dirname(os.getcwd()))
    # #once we are done we delete the temporary directory
    # if os.path.isdir(dest):
        # shutil.rmtree(dest)

def test_installation(wolframcommand, frpath):
    print ("Starting the tests at ",datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
    src_path=func.get_path("data")
    src_fullname=os.path.join(src_path,"test_suite.tar.gz")
    # dest="tempdir"+''.join(random.choice(string.ascii_lowercase) for i in range(5))
    dest=".test_suite"
    # Delete the temporary directory if it exists
    if os.path.isdir(dest):
        shutil.rmtree(dest)
    # Copy the source directory in the temporary one
    os.makedirs(dest, exist_ok=True)
    filename=os.path.join(dest, "test_suite.tar.gz")
    shutil.copy(src_fullname, filename)
    # and cd into it
    os.chdir(dest)
    if os.path.isfile("test_suite.tar.gz"):
        tar = tarfile.open("test_suite.tar.gz","r:gz")
        tar.extractall()
        tar.close()
        os.remove("test_suite.tar.gz")

    #now we do the different tests one by one

    #Let's do the ALP RGEs
    eftmodels="UnbrokenSM_BFM.fr ALP_EFT.fr"
    uvmodels="UnbrokenSM_BFM.fr ALP_UV.fr"
    mmmodels=uvmodels.split()[-1].replace(".fr","_MM")+" "+eftmodels.split()[-1].replace(".fr","_MM")
    mathematicascript=mmmodels.split()[0]+'.wl'
    try:
        func.create_model(eftmodels.split(), wolframcommand, frpath)
    except Exception:
        ts_up(dest)
        raise SystemExit('Exiting matchmaker-eft. Please check logs in directory .test_suite')
    try:
        func.create_model(uvmodels.split(), wolframcommand, frpath)
    except Exception:
        ts_up(dest)
        raise SystemExit('Exiting matchmaker-eft. Please check logs in directory .test_suite')
    try:
        match_model.match_model(*mmmodels.split(), False, 10000)
    except Exception:
        ts_up(dest)
        raise SystemExit('Exiting matchmaker-eft. Please check logs in directory .test_suite')
    try:
        func.compute_rge(*mmmodels.split(), wolframcommand)
    except Exception:
        ts_up(dest)
        raise SystemExit('Exiting matchmaker-eft. Please check logs in directory .test_suite')
    try:
        subprocess.run(wolframcommand+[mathematicascript], check=True)
    except subprocess.CalledProcessError:
        ts_up(dest)
        raise SystemExit('Exiting matchmaker-eft. Please check logs in directory .test_suite')

    #Let's do the matching of the Scalar Singlet on the SMEFT
    uvmodels="UnbrokenSM_BFM.fr Scalar_Singlet_BFM.fr"
    mmmodels="Scalar_Singlet_BFM_MM SMEFT_Green_Bpreserving_MM"
    mathematicascript=mmmodels.split()[0]+'.wl'
    try:
        func.create_model(uvmodels.split(), wolframcommand, frpath)
    except Exception:
        ts_up(dest)
        raise SystemExit('Exiting matchmaker-eft. Please check logs in directory .test_suite')
    try:
        match_model.match_model(*mmmodels.split(), False, 10000)
    except Exception:
        ts_up(dest)
        raise SystemExit('Exiting matchmaker-eft. Please check logs in directory .test_suite')
    try:
        func.compute_wilson_coefficients(*mmmodels.split(), wolframcommand)
    except Exception:
        ts_up(dest)
        raise SystemExit('Exiting matchmaker-eft. Please check logs in directory .test_suite')
    try:
        subprocess.run(wolframcommand+[mathematicascript], check=True)
    except subprocess.CalledProcessError:
        ts_up(dest)
        raise SystemExit('Exiting matchmaker-eft. Please check logs in directory .test_suite')

    #Let's do an example of basis change
    uvmodels="UnbrokenSM_BFM.fr newbasis.fr"
    mmmodels="newbasis_MM SMEFT_Green_Bpreserving_MM"
    mathematicascript=mmmodels.split()[0]+'.wl'
    try:
        func.create_model(uvmodels.split(), wolframcommand, frpath)
    except Exception:
        ts_up(dest)
        raise SystemExit('Exiting matchmaker-eft. Please check logs in directory .test_suite')
    try:
        match_model.match_model(*mmmodels.split(), False, 10000, True)
    except Exception:
        ts_up(dest)
        raise SystemExit('Exiting matchmaker-eft. Please check logs in directory .test_suite')
    try:
        func.compute_wilson_coefficients(*mmmodels.split(), wolframcommand)
    except Exception:
        ts_up(dest)
        raise SystemExit('Exiting matchmaker-eft. Please check logs in directory .test_suite')
    try:
        subprocess.run(wolframcommand+[mathematicascript], check=True)
    except subprocess.CalledProcessError:
        ts_up(dest)
        raise SystemExit('Exiting matchmaker-eft. Please check logs in directory .test_suite')


    # put here more tests following the structureabove

    ts_up(dest)
    print ("Tests finished at ",datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
