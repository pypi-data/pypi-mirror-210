import os
import cmd
import sys
import readline
import glob
import pickle
import configparser
import pkg_resources  
import shlex
from pathlib import Path
from . import functions

# this is a pointer to the module object instance itself.
this = sys.modules[__name__]

# we can explicitly make assignments on it 
this.mm_struct = None


def initialise_mm():
    if (this.mm_struct is None):
        # also in local function scope. no scope specifier like global is needed

        home = str(Path.home())
        config_folder = os.path.join(home, '.MatchMaker')
        os.makedirs(config_folder, exist_ok=True)
        settings_file = "settings.conf"
        full_config_file_path = os.path.join(config_folder, settings_file)
        config_object = configparser.ConfigParser()
        config_object["USERINFO"] = {"Feynrules Path": "", "Wolfram Script Command": ""}

        functions.create_config_file(full_config_file_path, config_object)
        config_object.read(full_config_file_path)

        try:
            functions.check_executable("form")
            functions.check_executable("qgraf")
            wolframcommand=functions.get_wolfram_command(full_config_file_path, config_object)
        except functions.BinaryNotFoundError:
            exit()


        functions.rp("matcher.m")
        feynrpath = functions.get_feynr_path(full_config_file_path, config_object)
        functions.fix_math_path(wolframcommand)

        this.mm_struct =  {
                "fr_path" : feynrpath,
                "wc" : wolframcommand,
                }

    return this.mm_struct
