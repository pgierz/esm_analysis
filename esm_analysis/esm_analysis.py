# -*- coding: utf-8 -*-

"""Main module."""

import os


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

        self._analysis_components = []

    def create_analysis_dir(self):
        """ Create the analysis directory and any intermediate directories if needed """
        if not os.path.isdir(self.ANALYSIS_DIR):
            os.makedirs(self.ANALYSIS_DIR)

    def initialize_analysis_components(self):
        for component in os.listdir(self.OUTDATA_DIR):
            print(component)
