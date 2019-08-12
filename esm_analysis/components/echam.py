""" Analysis Class for ECHAM """

import glob

from ..esm_analysis import EsmAnalysis

class EchamAnalysis(EsmAnalysis):

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

