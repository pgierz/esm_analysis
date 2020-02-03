# @Author: Paul Gierz <pgierz>
# @Date:   2020-01-23T13:06:50+01:00
# @Email:  pgierz@awi.de
# @Filename: fesom.py
# @Last modified by:   pgierz
# @Last modified time: 2020-02-03T09:53:34+01:00


""" Analysis Class for FESOM """

import logging
import os

import pyfesom as pf
import xarray as xr


from ..esm_analysis import EsmAnalysis
from ..scripts.analysis_scripts.fesom import ANALYSIS_fesom_sfc_timmean

twodim_fesom_analysis = ANALYSIS_fesom_sfc_timmean.MainProgram


class FesomAnalysis(EsmAnalysis):
    """
    Analysis of FESOM simulations

    Most of the methods default to the ones pre-defined in the base class, ``EsmAnalysis``.

    """

    NAME = "fesom"
    DOMAIN = "ocean"

    def test_meth(self):
        print(ANALYSIS_fesom_sfc_timmean)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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
        with open(self.SCRIPT_DIR + "/" + runscript_file) as runscript:
            mesh_dir = [l.strip() for l in runscript.readlines() if "MESH_DIR" in l][
                0
            ].split("=")[-1]
        self.MESH = pf.load_mesh(mesh_dir, usepickle=False)

    def determine_variable_dict_from_outdata_contents(self):
        # FIXME: File patterns are inconsistent, this is a "bad feature" in
        # esm-runscripts:fesom_post_processing.
        #
        # IDEA: We can embed this information in the top-of-exp-tree file
        # and ask for it if not there.
        all_outdata_variables = [
            f.replace(self.EXP_ID + "_", "").split("fesom_")[1].replace(".nc", "")
            for f in os.listdir(self.OUTDATA_DIR)
            if f.startswith(self.EXP_ID)
        ]

        ret_variables = {}
        variables = {
            "".join(r"\d" if c.isdigit() else c for c in file_stream)
            for file_stream in all_outdata_variables
        }
        just_variables = {
            "".join("" if c.isdigit() else c for c in file_stream)[:-1]
            for file_stream in all_outdata_variables
        }

        for just_variable, variable_pattern in zip(just_variables, variables):
            file_pattern = (
                self.OUTDATA_DIR
                + self.EXP_ID
                + "_"
                + self.NAME
                + "_"
                + variable_pattern
                + ".*nc"
            )
            ret_variables[file_pattern] = {}
            ret_variables[file_pattern][just_variable] = {"short_name": just_variable}
        return ret_variables

    def newest_climatology(self, varname):
        logging.debug("This method is trying to work on: %s", varname)
        try:
            p = twodim_fesom_analysis(
                varname,
                self.OUTDATA_DIR,
                output_file=self.ANALYSIS_DIR
                + "/"
                + self.EXP_ID
                + "_"
                + self.NAME
                + "_"
                + varname
                + "_climmean.nc",
            )
            p()
        except:
            logging.error("Something went wrong with the analysis!")
            raise
        return xr.open_dataset(
            self.ANALYSIS_DIR
            + "/"
            + self.EXP_ID
            + "_"
            + self.NAME
            + "_"
            + varname
            + "_climmean.nc"
        )
