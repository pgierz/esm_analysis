""" Analysis Class for ECHAM """

import glob
import logging
import os


from ..esm_analysis import EsmAnalysis


class EchamAnalysis(EsmAnalysis):
    """
    Analysis of ECHAM6 simulations

    Most of the methods default to the ones pre-defined in the base class, ``EsmAnalysis``.

    """

    NAME = "echam6"
    DOMAIN = "atmosphere"

    def __init__(self):
        super().__init__()

        self.ANALYSIS_DIR += "echam/"
        self.CONFIG_DIR += "echam/"
        self.FORCING_DIR += "echam/"
        self.INPUT_DIR += "echam/"
        self.OUTDATA_DIR += "echam/"
        self.RESTART_DIR += "echam/"

        self._variables = self.determine_variable_dict_from_code_files()

    ################################################################################
    # Special Analyses
    def newest_yearly_climatology(self, varname, number_of_years=30):
        # TODO
        pass

    ################################################################################
    # Spatial Averages:
    def fldmean(self, varname, file_list):
        if not os.path.isfile(
            self.ANALYSIS_DIR
            + "/"
            + self.EXP_ID
            + "_"
            + self.NAME
            + "_"
            + varname
            + "_fldmean.nc"
        ):
            tmp = self.CDO.select(
                "name=" + varname, options="-f nc -t echam6", input=file_list
            )
            logging.info("Finished with generation of 'tmp' file for fldmean")
            self.CDO.fldmean(
                input=tmp,
                output=self.ANALYSIS_DIR
                + "/"
                + self.EXP_ID
                + "_"
                + self.NAME
                + "_"
                + varname
                + "_fldmean.nc",
            )
        return (
            self.ANALYSIS_DIR
            + "/"
            + self.EXP_ID
            + "_"
            + self.NAME
            + "_"
            + varname
            + "_fldmean.nc"
        )

    ################################################################################
    # Temporal Averages
    def yearmean(self, varname, file_list):
        if not os.path.isfile(
            self.ANALYSIS_DIR
            + "/"
            + self.EXP_ID
            + "_"
            + self.NAME
            + "_"
            + varname
            + "_yearmean.nc"
        ):
            tmp = self.CDO.select(
                "name=" + varname, options="-f nc -t echam6", input=file_list
            )
            logging.info("Finished with generation of 'tmp' file for yearmean")
            self.CDO.yearmean(
                input=tmp,
                output=self.ANALYSIS_DIR
                + "/"
                + self.EXP_ID
                + "_"
                + self.NAME
                + "_"
                + varname
                + "_yearmean.nc",
            )
        return (
            self.ANALYSIS_DIR
            + "/"
            + self.EXP_ID
            + "_"
            + self.NAME
            + "_"
            + varname
            + "_yearmean.nc"
        )

    def ymonmean(self, varname, file_list):
        if not os.path.isfile(
            self.ANALYSIS_DIR
            + "/"
            + self.EXP_ID
            + "_"
            + self.NAME
            + "_"
            + varname
            + "_ymonmean.nc"
        ):
            tmp = self.CDO.select(
                "name=" + varname, options="-f nc -t echam6", input=file_list
            )
            logging.info("Finished with generation of 'tmp' file for ymonmean")
            self.CDO.ymonmean(
                input=tmp,
                output=self.ANALYSIS_DIR
                + "/"
                + self.EXP_ID
                + "_"
                + self.NAME
                + "_"
                + varname
                + "_ymonmean.nc",
            )
        return (
            self.ANALYSIS_DIR
            + "/"
            + self.EXP_ID
            + "_"
            + self.NAME
            + "_"
            + varname
            + "_ymonmean.nc"
        )

    def timmean(self, varname, file_list):
        if not os.path.isfile(
            self.ANALYSIS_DIR
            + "/"
            + self.EXP_ID
            + "_"
            + self.NAME
            + "_"
            + varname
            + "_timmean.nc"
        ):
            tmp = self.CDO.select(
                "name=" + varname, options="-f nc -t echam6", input=file_list
            )
            logging.info("Finished with generation of 'tmp' file for timmean")
            self.CDO.timmean(
                input=tmp,
                output=self.ANALYSIS_DIR
                + "/"
                + self.EXP_ID
                + "_"
                + self.NAME
                + "_"
                + varname
                + "_timmean.nc",
            )
        return (
            self.ANALYSIS_DIR
            + "/"
            + self.EXP_ID
            + "_"
            + self.NAME
            + "_"
            + varname
            + "_timmean.nc"
        )
