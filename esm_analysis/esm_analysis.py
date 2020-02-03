# @Author: Paul Gierz <pgierz>
# @Date:   2020-02-01T10:07:07+01:00
# @Email:  pgierz@awi.de
# @Filename: esm_analysis.py
# @Last modified by:   pgierz
# @Last modified time: 2020-02-03T14:44:22+01:00


# -*- coding: utf-8 -*-

"""Main module."""

import glob
import importlib
import logging
import os
import re
import sys

import cdo
import yaml


def load_yaml(f):
    with open(f) as yml:
        return yaml.load(yml, Loader=yaml.SafeLoader)


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


################################################################################
# NOTES:
#
#   This needs to be refactored correctly. Actually, we need two big classes,
#   not just one.
#
#   The first needs to be for components, the second for the entire experiment.
#   Otherwise you inherit methods into the components that actually don't work,
#   since they rely on attributes for the entire setup.
################################################################################


class AnalysisComponent(object):
    pass


class EsmAnalysis(object):
    def __init__(self, exp_base=None, preferred_analysis_dir=None):
        """
        Base Class for Analysis, other component specific analysis classes
        should inherit from this one

        Sets up the following directories and attributes from anywhere within
        the experiment tree:
        + ``EXP_ID``
        + ``ANALYSIS_DIR``
        + ``CONFIG_DIR``
        + ``FORCING_DIR``
        + ``INPUT_DIR``
        + ``OUTDATA_DIR``
        + ``RESTART_DIR``
        + ``SCRIPT_DIR``

        Parameters
        ----------
        preferred_analysis_dir : str
            Where the analysis files should be stored, defaults to the current experiment.
        """
        # Figure out what the top of the experiment is by finding upwards a
        # file called .top_of_exp_tree
        if not exp_base:
            for bottom, _, files in walk_up(os.getcwd()):
                if ".top_of_exp_tree" in files:
                    self.EXP_BASE = bottom
                    break
            else:
                self.EXP_BASE = input(
                    "Enter the top-level directory of your experiment: "
                )
                basedir = os.path.dirname(self.EXP_BASE)
                if not os.path.exists(basedir):
                    print("Generating directories for %s" % basedir)
                    input("Press Enter to continue, Ctrl-C to canel...")
                    try:
                        os.makedirs(basedir)
                    except PermissionError:
                        print("Sorry, you don't have permission to write here!")
                print("Making marker file .top_of_exp_tree in %s" % basedir)
                input("Press Enter to continue, Ctrl-C to cancel...")
                try:
                    with open(self.EXP_BASE + "/.top_of_exp_tree", "w") as f:
                        os.utime(f, None)
                except PermissionError:
                    print("Sorry, you don't have permission to write here!")
        else:
            self.EXP_BASE = exp_base

        self.EXP_ID = os.path.basename(self.EXP_BASE)

        self._config = load_yaml(os.path.join(self.EXP_BASE, ".top_of_exp_tree"))

        logging.debug(self._config)

        self.ANALYSIS_DIR = self.EXP_BASE + "/analysis/"
        self.CONFIG_DIR = self.EXP_BASE + "/config/"
        self.FORCING_DIR = self.EXP_BASE + "/forcing/"
        self.INPUT_DIR = self.EXP_BASE + "/input/"
        self.OUTDATA_DIR = self.EXP_BASE + "/outdata/"
        self.RESTART_DIR = self.EXP_BASE + "/restart/"
        self.SCRIPT_DIR = self.EXP_BASE + "/scripts/"

        # Here's yer CDO:
        self.CDO = cdo.Cdo()

        # Ensure that the analysis directory exists for the top:
        logging.info("Before call: %s", self.ANALYSIS_DIR)
        self.create_analysis_dir(preferred_analysis_dir=preferred_analysis_dir)
        logging.info("After call: %s", self.ANALYSIS_DIR)

        # Make a list to hold the analysis components
        self._analysis_components = []

    def create_analysis_dir(self, preferred_analysis_dir=None):
        """
        Create the analysis directory and any intermediate directories if needed.

        Parameters
        ----------
        preferred_analysis_dir : str
            The location where analysis should be stored

        Notes
        -----
        If you give an argument to ``preferred_analysis_dir``, the attribute
        ``self.ANALYSIS_DIR`` is changed to this.
        """
        if preferred_analysis_dir is not None:
            logging.info("Modifying self.ANALYSIS_DIR:")
            self.ANALYSIS_DIR = preferred_analysis_dir
            logging.info(self.ANALYSIS_DIR)
        if not os.path.isdir(self.ANALYSIS_DIR):
            logging.info("Creating directory: %s", self.ANALYSIS_DIR)
            os.makedirs(self.ANALYSIS_DIR)

    def initialize_analysis_components(self, preferred_analysis_dir=None):
        """
        Creates analysis objects for each component found in the ``OUTDATA_DIR`` directory.

        It is assumed that the component analysis object can be initialized
        without any arguments. If no class has been defined yet, a warning is
        sent.
        """
        for component in os.listdir(self.OUTDATA_DIR):
            try:
                # TODO: I don't really like this, it'd be nicer with relative
                # imports (maybe? I am not sure...)
                logging.debug("Trying to import esm_analysis.components." + component)
                comp_module = importlib.import_module(
                    "esm_analysis.components." + component
                )
                logging.debug("Import worked!")
                comp_analyzer = getattr(
                    comp_module, component.capitalize() + "Analysis"
                )(exp_base=self.EXP_BASE, preferred_analysis_dir=preferred_analysis_dir)
                logging.debug("Init worked!")
                # PG: Not sure I like the next two lines, they already confuse
                # me 10 minutes after I wrote them...
                if preferred_analysis_dir:
                    component_analysis_dir = preferred_analysis_dir + "/" + component
                    comp_analyzer.create_analysis_dir(
                        preferred_analysis_dir=component_analysis_dir
                    )
                else:
                    comp_analyzer.create_analysis_dir()

                logging.debug("Finished setting up analysis dir for " + component)
                # Make it a object attribute for access interactively:
                setattr(self, comp_analyzer.NAME, comp_analyzer)
                logging.debug("Setting attributes for the big analyser")

                # Put it in the list for easy access from inside the class:
                self._analysis_components.append(comp_analyzer)
            except:
                logging.warning(
                    "Oops: Trouble initializing or no analysis class available for: %s"
                    % component
                )
                logging.error("Error was: %s", sys.exc_info()[0])
                if component == "fesom":
                    raise

    def determine_variable_dict_from_code_files(self):
        """
        A generic method to create a dictionary containing file patterns and
        variable information for each file pattern found in the ``OUTDATA_DIR``
        folder.

        Notes
        -----
        This is meant to be overloaded!! The default implementation works for
        ECHAM6 and JSBACH. Maybe it is better to completely move this to just
        those two classes, or a base class which both can build on.

        Returns
        -------
        A nested dictionary. The outermost key is a file pattern, with the
        value/inner key is the variable short name. The inner value is a
        dictionary of code_number, levels, short_name, long_name.
        """
        logging.debug("Starting to determine variable dict...")
        variables = {}
        # CLEANUP: This is a lot of duplicate code...
        all_code_files = glob.glob(
            self.OUTDATA_DIR + self.EXP_ID + "_" + self.NAME + "*.codes"
        )
        # Remove the file path:
        code_files = [
            code_file.replace(self.OUTDATA_DIR, "") for code_file in all_code_files
        ]
        code_streams = [
            code_file.replace(self.EXP_ID, "").replace(".codes", "")
            for code_file in code_files
        ]
        code_streams_no_digits = {
            "".join(r"\d" if c.isdigit() else c for c in code_file)
            for code_file in code_streams
        }
        code_streams_full = {
            self.OUTDATA_DIR + self.EXP_ID + stream + ".codes"
            for stream in code_streams_no_digits
        }
        code_regexes = {re.compile(stream) for stream in code_streams_full}
        deduped_streams = [
            list(filter(r.match, all_code_files))[0] for r in code_regexes
        ]

        for f in deduped_streams:
            logging.debug("Working on: %s", f)
            file_stream = (
                f.replace(self.OUTDATA_DIR, "")
                .replace(self.EXP_ID + "_" + self.NAME + "_", "")
                .replace(".codes", "")
            )
            file_stream = "".join(r"\d" if c.isdigit() else c for c in file_stream)
            # BUG: This depends on knowing that the file extension is GRIB. This might not always be the case...
            file_pattern = (
                self.OUTDATA_DIR
                + self.EXP_ID
                + "_"
                + self.NAME
                + "_"
                + file_stream
                + ".grb"
            )
            # Replace digits with regex-able expression:
            #
            # POTENTIAL BUG: if two streams are very similar, e.g.
            # EXP_ID_echam6_echam_stream123.grb and
            # EXP_ID_echam6_echam_stream456.grb, these will end up being the
            # same; and this fails...
            logging.debug("File pattern will be: %s", file_pattern)
            variables[file_pattern] = {}
            with open(f) as code_file:
                code_file_list = [" ".join(line.split()) for line in code_file]
                for entry in code_file_list:
                    code_number, levels, short_name, _, _, long_name = entry.split(
                        " ", 5
                    )
                    variables[file_pattern][short_name] = {
                        "code_number": code_number,
                        "levels": levels,
                        "short_name": short_name,
                        "long_name": long_name,
                    }
        logging.debug("Variable dict given back will be: %s", variables)
        return variables

    def _get_files_for_variable_short_name_single_component(self, varname):
        fpattern_list = []
        for (file_pattern, short_names_in_file_pattern) in self._variables.items():
            for short_name in short_names_in_file_pattern:
                logging.debug("Checking: %s = %s", short_name, varname)
                if short_name == varname:
                    fpattern_list.append(
                        sorted(
                            list(
                                filter(
                                    re.compile(file_pattern).match,
                                    [
                                        self.OUTDATA_DIR + f
                                        for f in os.listdir(self.OUTDATA_DIR)
                                    ],
                                )
                            )
                        )
                    )
                    # fpattern_list.append(sorted(glob.glob(file_pattern)))
        if len(fpattern_list) > 1:
            print("Multiple file patterns have requested variable %s" % varname)
            for index, fpattern in enumerate(fpattern_list):
                print("[%s] %s" % (index + 1, fpattern[0]))
            index_choice = int(input("Please choose a filepattern: ")) - 1
            return fpattern_list[index_choice]
        return fpattern_list[0]

    def get_component_for_variable_short_name(self, varname):
        """
        Checks all known component and gets a list of files that should be used
        for a specific variable name.

        There is currently an implicit assumption for the following to be true:
        1. Each ``component`` has a private attribute ``_variables``
        1. This attribute should be a dictionary
        1. The dictionary needs to have a "file_pattern" as a key, and all
           short names contained in this file pattern as values.

        Parameters
        ----------
        varname : str
            The short variable name which is being looked for

        Returns
        -------
        file_pattern_list, component : tuple
            A tuple of:
            1. A list for all files currently available with the varname. Note
               that sorting currently does not have a specific mechanism, so it
               **probably** sorts alphabetically/numerically.
            2. The component object for analysis with these files.
        """
        fpattern_list = []
        logging.debug(self._analysis_components)
        for component in self._analysis_components:
            for (
                file_pattern,
                short_names_in_file_pattern,
            ) in component._variables.items():
                for short_name in short_names_in_file_pattern:
                    logging.debug("Checking: %s = %s", short_name, varname)
                    if short_name == varname:
                        fpattern_list.append(
                            (
                                sorted(
                                    list(
                                        filter(
                                            re.compile(file_pattern).match,
                                            [
                                                component.OUTDATA_DIR + f
                                                for f in os.listdir(
                                                    component.OUTDATA_DIR
                                                )
                                            ],
                                        )
                                    )
                                ),
                                component,
                            )
                        )
                        # fpattern_list.append(
                        #     (sorted(glob.glob(file_pattern)), component)
                        # )
        multi_comps = []
        for index, (fpattern, component) in enumerate(fpattern_list):
            if component not in multi_comps:
                multi_comps.append(component)
        if len(multi_comps) > 1:
            print("Multiple components have requested variable %s" % varname)
            for index, component in enumerate(multi_comps):
                print("[%s] %s" % (index + 1, component.NAME))
            index_choice = int(input("Please choose a component: ")) - 1
            return multi_comps[index_choice]
        else:
            return multi_comps[0]

    # Some common operations. If a specific model needs to do this in a
    # different way, you can overload the methods (e.g. FESOM needs to do
    # weighting of the triangles to get correct fldmean)
    def fldmean(self, varname):
        """
        Generates a field mean over the entire model domain for a the specified varname.
        """
        component = self.get_component_for_variable_short_name(varname)
        return component.fldmean(varname)

    def ymonmean(self, varname):
        """
        Generates a ymonmean over the entire model domain for the specified varname.
        """
        component = self.get_component_for_variable_short_name(varname)
        return component.ymonmean(varname)

    def yseasmean(self, varname):
        """
        Generates a yseasmean over the entire model domain for the specified varname.
        """
        component = self.get_component_for_variable_short_name(varname)
        return component.yseasmean(varname)

    def newest_climatology(self, varname):
        component = self.get_component_for_variable_short_name(varname)
        return component.newest_climatology(varname)
