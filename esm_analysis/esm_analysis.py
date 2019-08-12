# -*- coding: utf-8 -*-

"""Main module."""

import glob
import importlib
import logging
import os

import cdo

def walk_up(bottom):
    """
    mimic os.walk, but walk 'up' instead of down the directory tree

    Parameters
    ----------
    bottom: str
        Where to start walking up from

    Yields
    ------
    Tuple of (bottom, dirs, nondirs)
    """
    bottom = os.path.realpath(bottom)

    # Get files in current dir
    try:
        names = os.listdir(bottom)
    except Exception as e:
        print(e)
        return

    dirs, nondirs = [], []
    for name in names:
        if os.path.isdir(os.path.join(bottom, name)):
            dirs.append(name)
        else:
            nondirs.append(name)
    yield bottom, dirs, nondirs

    new_path = os.path.realpath(os.path.join(bottom, ".."))

    # See if we are at the top
    if new_path == bottom:
        return

    for x in walk_up(new_path):
        yield x


class EsmAnalysis(object):
    def __init__(self):
        """ Base Class for Analysis, other component specific analysis classes should inherit from this one

        Sets up the following directories and attributes from anywhere within the experiment tree:
        + ``EXP_ID``
        + ``ANALYSIS_DIR``
        + ``CONFIG_DIR``
        + ``FORCING_DIR``
        + ``INPUT_DIR``
        + ``OUTDATA_DIR``
        + ``RESTART_DIR``
        + ``SCRIPT_DIR``
        """
        # Figure out what the top of the experiment is by finding upwards a
        # file called .top_of_exp_tree
        for bottom, dirs, files in walk_up(os.getcwd()):
            if ".top_of_exp_tree" in files:
                self.EXP_BASE = bottom
                break

        self.EXP_ID = os.path.basename(self.EXP_BASE)

        self.ANALYSIS_DIR = self.EXP_BASE + "/analysis/"
        self.CONFIG_DIR = self.EXP_BASE + "/config/"
        self.FORCING_DIR = self.EXP_BASE + "/forcing/"
        self.INPUT_DIR = self.EXP_BASE + "/input/"
        self.OUTDATA_DIR = self.EXP_BASE + "/outdata/"
        self.RESTART_DIR = self.EXP_BASE + "/restart/"
        self.SCRIPT_DIR = self.EXP_BASE + "/scripts/"

        # Here's yer CDO:
        self.CDO = cdo.Cdo()

        self._analysis_components = []
        # Putting this here leads to a recursion???
        # Duh, of course it does -- you call the super init from the
        # subcomponents, dumbass...
        #
        #self.initialize_analysis_components()

    def create_analysis_dir(self):
        """ Create the analysis directory and any intermediate directories if needed """
        if not os.path.isdir(self.ANALYSIS_DIR):
            os.makedirs(self.ANALYSIS_DIR)

    def initialize_analysis_components(self):
        for component in os.listdir(self.OUTDATA_DIR):
            try:
                # XXX: I don't really like this, it'd be nicer with relative
                # imports (maybe? I am not sure...)
                comp_module = importlib.import_module("esm_analysis.components."+component)
                self._analysis_components.append(getattr(comp_module, component.capitalize()+"Analysis")())
            except:
                logging.warning("Oops: no analysis class available for: %s" % component)

    def determine_variable_dict_from_code_files(self):
        variables = {}
        for f in glob.glob(self.OUTDATA_DIR+self.EXP_ID+"_"+self.NAME+"*.codes"):
            file_stream = f.replace(self.OUTDATA_DIR, "").replace(self.EXP_ID+"_"+self.NAME+"_", "").replace(".codes", "")
            # BUG: This depends on knowing that the file extension is GRIB. This might not always be the case...
            file_pattern = self.OUTDATA_DIR+self.EXP_ID+"_"+self.NAME+"_"+file_stream+"*grb"
            variables[file_pattern] = {}
            with open(f) as code_file:
                code_file_list = [" ".join(line.split()) for line in code_file]
                for entry in code_file_list:
                    code_number, levels, short_name, _, _, long_name = entry.split(" ", 5)
                    variables[file_pattern][short_name] = {
                        'code_number': code_number,
                        'levels': levels,
                        'short_name': short_name,
                        'long_name': long_name,
                        }
        return variables

    def get_files_for_variable_short_name(self, varname):
        for component in self._analysis_components:
            for file_pattern, short_names_in_file_pattern in component._variables.items():
                for short_name in short_names_in_file_pattern:
                    logging.debug("Checking: %s = %s" % (short_name, varname))
                    if short_name == varname:
                        return sorted(glob.glob(file_pattern)), component

    # Some common operations. If a specific model needs to do this in a
    # different way, you can overload the methods (e.g. FESOM needs to do
    # weighting of the triangles to get correct fldmean)
    def fldmean(self, varname):
        needed_files, component = self.get_files_for_variable_short_name(varname)
        comp_name, output_dir = component.NAME, component.ANALYSIS_DIR
        self.CDO.fldmean.select('name='+varname, input=needed_files, output=output_dir+self.EXP_ID+"_"+comp_name+"_"+varname+"_fldmean".nc)
