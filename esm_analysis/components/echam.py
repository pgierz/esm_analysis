""" Analysis Class for ECHAM """

import glob
import logging
import os


from ..esm_analysis import EsmAnalysis

# FIXME: move this somewhere else:
def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

class EchamAnalysis(EsmAnalysis):
    """
    Analysis of ECHAM6 simulations

    Most of the methods default to the ones pre-defined in the base class, ``EsmAnalysis``.

    """

    NAME = "echam6"
    DOMAIN = "atmosphere"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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
            if len(file_list) > 1000:
                print("Processing chunks...")
                tmp_list = []
                for files in chunks(file_list, 1000):
                    print("These files are next:")
                    for f in files:
                        print(f)
                    tmp_chunk = self.CDO.select(
                            "name="+varname, options="-f nc -t echam6", input=files
                            )
                    tmp_list.append(tmp_chunk)
                tmp = self.CDO.cat(input=" ".join(tmp_list))
            else:
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
            if len(file_list) > 1000:
                print("Processing chunks...")
                tmp_list = []
                for files in chunks(file_list, 1000):
                    print("These files are next:")
                    for f in files:
                        print(f)
                    tmp_chunk = self.CDO.select(
                            "name="+varname, options="-f nc -t echam6", input=files
                            )
                    tmp_list.append(tmp_chunk)
                tmp = self.CDO.cat(input=" ".join(tmp_list))
            else:
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
