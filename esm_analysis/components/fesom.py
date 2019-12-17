""" Analysis Class for FESOM """

import glob
import logging
import os

import pyfesom as pf
import xarray as xr


from ..esm_analysis import EsmAnalysis


class FesomAnalysis(EsmAnalysis):
    """
    Analysis of FESOM simulations

    Most of the methods default to the ones pre-defined in the base class, ``EsmAnalysis``.

    """

    NAME = "fesom"
    DOMAIN = "ocean"

    def __init__(self):
        super().__init__()

        self.ANALYSIS_DIR += self.NAME + "/"
        self.CONFIG_DIR += self.NAME + "/"
        self.FORCING_DIR += self.NAME + "/"
        self.INPUT_DIR += self.NAME + "/"
        self.OUTDATA_DIR += self.NAME + "/"
        self.RESTART_DIR += self.NAME + "/"

        self._variables = self.determine_variable_dict_from_outdata_contents()

        runscript_file = [f for f in os.listdir(self.SCRIPT_DIR) if f.endswith("run")][
            0
        ]
        with open(runscript_file) as runscript:
            mesh_dir = [l.strip() for l in runscript.readlines() if "MESH_DIR" in l][
                0
            ].split("=")[-1]
        self.MESH = pf.load_mesh(mesh_dir, usepickle=False)

    def determine_variable_dict_from_outdata_contents(self):
        all_outdata_variables = {
            f.replace(self.EXP_ID + "_", "").split("_fesom")[0]
            for f in os.listdir(self.OUTDATA_DIR)
        }
        variables = {}
        for file_stream in all_outdata_variables:
            # FIXME: File patterns are inconsistent, this is a bug in
            # esm-runscripts:fesom_post_processing.
            file_pattern = (
                self.OUTDATA_DIR
                + self.EXP_ID
                + "_"
                + file_stream
                + "_"
                + self.NAME
                + "*nc"
            )
            variables[file_pattern] = {}
            variables[file_pattern][file_stream] = {"short_name": file_stream}
        return variables
