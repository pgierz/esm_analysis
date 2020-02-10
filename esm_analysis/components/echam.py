# @Author: Paul Gierz <pgierz>
# @Date:   2020-01-31T19:03:13+01:00
# @Email:  pgierz@awi.de
# @Filename: echam.py
# @Last modified by:   pgierz
# @Last modified time: 2020-02-10T10:46:48+01:00


""" Analysis Class for ECHAM """

import logging
import os

import xarray as xr

from ..esm_analysis import EsmAnalysis

# FIXME: move this somewhere else:
def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


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
    def newest_climatology(self, varname, number_of_years=30):
        """
        Generates a climatological average (time mean) for a specific variable
        name, default length of 30 years.

        Parameters
        ----------
        varname : str
            The variable name to use
        number_of_years : int
            The number of years to use to generate the climatology

        Warning
        -------
        Currently, it is assumed that ECHAM6 outputs 1 file for each month, so
        the newest ``number_of_years*12`` files are named. Newest is determined
        based upon alphabetical sorting, since the modification timestamps
        might be messed up due to something like ``touch``
        """
        logging.debug("Constructing filelist")
        flist = self._get_files_for_variable_short_name_single_component(varname)
        required_files = flist[-number_of_years * 12 :]
        for f in required_files:
            logging.debug("- %s", f)
        logging.debug("Starting CDO")
        return self.CDO.timmean(
            options="-v -f nc -t echam6",
            input="-select,name=" + varname + " " + " ".join(required_files),
            output=self.ANALYSIS_DIR
            + "/"
            + self.EXP_ID
            + "_"
            + self.NAME
            + "_"
            + varname
            + "_climmean.nc",
            returnXDataset=True,
        )

    def _process_chunk_files(self, file_list, varname):
        logging.debug("Processing chunks...")
        tmp_list = []
        for files in chunks(file_list, 1000):
            logging.debug("These files are next:")
            for f in files:
                logging.debug(f)
            tmp_chunk = self.CDO.select(
                "name=" + varname, options="-f nc -t echam6", input=files
            )
            tmp_list.append(tmp_chunk)
        tmp = self.CDO.cat(input=" ".join(tmp_list))
        return tmp

    ################################################################################
    # Spatial Averages:
    def fldmean(self, varname):
        file_list = self._get_files_for_variable_short_name_single_component(varname)
        oname = (
            self.ANALYSIS_DIR
            + "/"
            + self.EXP_ID
            + "_"
            + self.NAME
            + "_"
            + varname
            + "_fldmean.nc"
        )
        if not os.path.isfile(oname):
            if len(file_list) > 1000:
                tmp = self._process_chunk_files(file_list, varname)
            else:
                tmp = self.CDO.select(
                    "name=" + varname, options="-f nc -t echam6", input=file_list
                )
            logging.info("Finished with generation of 'tmp' file for fldmean")
            return self.CDO.fldmean(input=tmp, output=oname, returnXDataset=True)
        return xr.open_dataset(oname)

    ################################################################################
    # Temporal Averages
    def yearmean(self, varname):
        file_list = self._get_files_for_variable_short_name_single_component(varname)
        oname = (
            self.ANALYSIS_DIR
            + "/"
            + self.EXP_ID
            + "_"
            + self.NAME
            + "_"
            + varname
            + "_yearmean.nc"
        )
        if not os.path.isfile(oname):
            if len(file_list) > 1000:
                tmp = self._process_chunk_files(file_list, varname)
            else:
                tmp = self.CDO.select(
                    "name=" + varname, options="-f nc -t echam6", input=file_list
                )
            logging.info("Finished with generation of 'tmp' file for yearmean")
            return self.CDO.yearmean(input=tmp, output=oname, returnXDataset=True)
        return xr.open_dataset(oname)

    def ymonmean(self, varname):
        file_list = self._get_files_for_variable_short_name_single_component(varname)
        oname = (
            self.ANALYSIS_DIR
            + "/"
            + self.EXP_ID
            + "_"
            + self.NAME
            + "_"
            + varname
            + "_ymonmean.nc"
        )
        if not os.path.isfile(oname):
            tmp = self.CDO.select(
                "name=" + varname, options="-f nc -t echam6", input=file_list
            )
            logging.info("Finished with generation of 'tmp' file for ymonmean")
            return self.CDO.ymonmean(input=tmp, output=oname, returnXDataset=True)
        return xr.open_dataset(oname)

    def timmean(self, varname):
        file_list = self._get_files_for_variable_short_name_single_component(varname)
        oname = (
            self.ANALYSIS_DIR
            + "/"
            + self.EXP_ID
            + "_"
            + self.NAME
            + "_"
            + varname
            + "_timmean.nc"
        )
        if not os.path.isfile(oname):
            tmp = self.CDO.select(
                "name=" + varname, options="-f nc -t echam6", input=file_list
            )
            logging.info("Finished with generation of 'tmp' file for timmean")
            return self.CDO.timmean(input=tmp, output=oname, returnXDataset=True)
        return xr.open_dataset(oname)

    def yseasmean(self, varname):
        file_list = self._get_files_for_variable_short_name_single_component(varname)
        oname = (
            self.ANALYSIS_DIR
            + "/"
            + self.EXP_ID
            + "_"
            + self.NAME
            + "_"
            + varname
            + "_yseasmean.nc"
        )
        if not os.path.isfile(oname):
            if len(file_list) > 1000:
                tmp = self._process_chunk_files(file_list, varname)
            else:
                tmp = self.CDO.select(
                    "name=" + varname, options="-f nc -t echam6", input=file_list
                )
            logging.info("Finished with generation of 'tmp' file for yseasmean")
            return self.CDO.yseasmean(input=tmp, output=oname, returnXDataset=True)
        return xr.open_dataset(oname)
