#!/usr/bin/env python3
# @Author: Paul Gierz <pgierz>
# @Date:   2020-01-23T13:06:50+01:00
# @Email:  pgierz@awi.de
# @Filename: fesom.py
# @Last modified by:   pgierz
# @Last modified time: 2020-02-18T07:27:50+01:00
"""
Analysis Class for FESOM

This object, ``FesomAnalysis`` provides an easy interface to ``FESOM 1.4`` and
``FESOM 2.0`` analyses. Notable features:

* Automatic processing with dask: Parallel computing on multiple CPUs when possible.
* Automatic loading of mesh information
* Creates and re-uses interpolate weights
"""
# Python Standard Library:
import logging
import os
import re

# Third-Party Imports
from dask.diagnostics import ProgressBar
from dask.distributed import Client
from regex_engine import generator
import f90nml
import numpy as np
import pyfesom as pf
import xarray as xr

# Local Imports:
from ..esm_analysis import EsmAnalysis
from ..esm_analysis.utils import sizeof_fmt, full_size_of_filelist


class FesomAnalysis(EsmAnalysis):
    """
    Analysis of FESOM simulations. Same methods you know from ``ECHAM6`` but for
    ``FESOM``. The module overview gives a good idea of the features of this
    class. See the documentation of public methods for more info.


    Building a ``FesomAnalysis`` Object
    -----------------------------------
    The trickiest thing about using this class is correctly instanciating the
    ``FesomAnalysis`` class. There currently are **only** optional arguments.



    """

    NAME = "fesom"
    DOMAIN = "ocean"

    ############################################################################
    # INITILIZATION
    ############################################################################
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.ANALYSIS_DIR += self.NAME + "/"
        self.CONFIG_DIR += self.NAME + "/"
        self.FORCING_DIR += self.NAME + "/"
        self.INPUT_DIR += self.NAME + "/"
        self.OUTDATA_DIR += self.NAME + "/"
        self.RESTART_DIR += self.NAME + "/"

        self._config = self._config.get("fesom", {})

        runscript_file = [f for f in os.listdir(self.SCRIPT_DIR) if f.endswith("run")][
            0
        ]
        with open(self.SCRIPT_DIR + "/" + runscript_file) as runscript:
            mesh_dir = [l.strip() for l in runscript.readlines() if "MESH_DIR" in l][
                0
            ].split("=")[-1]

        namelist_config = f90nml.read(self.CONFIG_DIR + "/namelist.config")
        # FIXME: Should be user specifiable:
        self.LEVELWISE_OUTPUT = namelist_config["inout"]["levelwise_output"]
        # FIXME: Should be user specifiable:
        self.MESH_ROTATED = self._config.get("mesh_rotated", False)
        # FIXME: Should be user specifiable:
        self.NAMING_CONVENTION = self._config.get("naming_convention", "esm_new")

        self._variables = self.determine_variable_dict_from_outdata_contents()
        abg = [0, 0, 0] if self.MESH_ROTATED else [50, 15, -90]
        self.MESH = pf.load_mesh(mesh_dir, usepickle=False, get3d=False, abg=abg)
        self._interpolation_file = os.path.join(
            self.ANALYSIS_DIR,
            "_".join([self.EXP_ID, self.NAME, "interpolation_weights"]),
        )

        self.client = Client()

        print(40 * "- ")
        print(f"Mesh information for {self.EXP_ID}")
        print(self.MESH.__repr__())

        print(40 * "- ")
        print(f"Dask dashboard information {self.client}")

    def _var_dict_esm_new(self):
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
        # FIXME: This is probably wrong
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

    ############################################################################
    # FILES
    ############################################################################

    def _get_list_of_relevant_files(self, variable, years=None):
        """
        Gets a list of all the files for variable in the odir

        Parameters:
        -----------
        variable : str
            The variable name to match for
        years : Tuple of ints or None
            The years you want; this will be used to get a regular expression
            matching the current years.

        Returns:
        --------
        var_list : list
            A list of filenames with the pattern ``<variable>_fesom_\d+.nc``,
            sorted by modification time.

        Known Improvements:
        -------------------
        This is pretty specific for how output is saved in ``FESOM``.
        """
        r = re.compile(self._determine_regex_from_naming_convention(variable, years))
        # TODO: This is actually a bit double logic, we already have the list of
        # variables in the self._variables dict
        olist = [
            self.OUTDATA_DIR + "/" + f
            for f in os.listdir(self.OUTDATA_DIR)
            if r.match(f)
        ]
        olist.sort(key=lambda x: os.path.getmtime(x))
        # FIXME: This depends on how many years we actually want to get. Default
        # is newest 30?
        if years == None:
            olist = olist[-30:]
        return olist

    def _determine_regex_from_naming_convention(self, variable, years=None):
        if years:
            regex_years = generator().numerical_range(years[0], years[1]).strip("^$")
        else:
            regex_years = r"\d+"

        # NOTE: Make sure that your regular expression does **EXACT** matches to
        # avoid problems later on in the program. Example:
        # ${EXP_ID}_fesom_so_18[56]?0101.nc matches and
        # ${EXP_ID}_fesom_so_18[56]?0101.nc.monmean does not!!!!
        if self.NAMING_CONVENTION == "esm_classic":
            return "^" + variable + "_fesom_" + regex_years + "0101.nc$"
        if self.NAMING_CONVENTION == "esm_new":
            return (
                "^"  # Start of match
                + self.EXP_ID
                + "_fesom_"
                + variable
                + "_"
                + regex_years
                + "0101.nc"
                + "$"  # End of match
            )
        if self.NAMING_CONVENTION == "legacy":
            return "^fesom." + regex_years + "0101" + ".oce.mean.nc$"
        raise ValueError("Unknown naming convention specified!")

    def _load_data(self, variable, years=None):
        olist = self._get_list_of_relevant_files(variable, years)
        print(f"Loading files for {variable}")
        print(f"{len(olist)} files --> {sizeof_fmt(full_size_of_filelist(olist))}")
        self.ds = xr.open_mfdataset(
            olist, parallel=True, combine="by_coords", chunks={"time": 10}
        )

    ############################################################################
    # LEVELwISE OUTPUT
    ############################################################################

    def _select_level_0(self):
        """
        Gets the top level of ``self.ds``; automatically handles
        attribute ``LEVELWISE_OUTPUT`` correct

        Note
        ----
            This method will **modify** ``self.level_data``
        """
        # FIXME (General): This function apparently needs a variable. Shouldn't
        # being able to get level 0 be irrelevant which variable I actually
        # want?
        if not self.LEVELWISE_OUTPUT:
            level_data, elem_no_nan = pf.get_data(
                self.ds.variables[self.variable][:, :], self.MESH, 0
            )
        else:
            # FIXME: This looks wrong for two reasons:
            # 1) What's self.variable?
            # 2) Values triggers a calculation, which we don't want until the
            #    very end...
            level_data = self.ds.variables[self.variable].values
        self.level_data = level_data

    def _select_timesteps(self, timintv=None):
        """
        Assigns a timestep attribute based upon user specifications

        Parameters
        ----------
        timintv : str
            A time interval to select, should conform to ``xarray`` standards
            for selecting time as: ds[timintv]

            Examples could be "time.DJA"...?
        """
        if timintv is not None:
            self.timestep = self.ds_timmean[timintv].values
        else:
            self.timestep = timestep

    ############################################################################
    # INTERPOLATION
    ############################################################################

    def _interpolation_to_dataarray(self, variable):
        """
        After interpolation, this method can be used to turn the resulting
        object into a DataArray

        Parameters
        ----------
        variable : str
            The name the variable should get inside the DataArray object.
        """
        print("\n Generating an DataArray object for saving")
        self.interpolated_ds = xr.DataArray(
            self.nearest,
            dims=["time", "lat", "lon"],
            coords=[self.timestep, self.lat, self.lon],
            name=variable,
        )

    def _prepare_for_interpolation(self):
        """
        Creates lats and lons attributes to be used during interpolation
        """
        # TODO: This probably doesn't need to be here and can happen in the init
        self.lon = np.linspace(-180, 180, 1440)
        self.lat = np.linspace(-90, 90, 720)
        self.lons, self.lats = np.meshgrid(self.lon, self.lat)

    def _interpolation_weights_available(self):
        """
        Checks if the interpolation weight file can be found

        Returns
        -------
        bool : File available or not
        """
        return os.path.isfile(self._interpolation_file)

    def _calculate_weights_distances(self):
        distances, inds = pf.create_indexes_and_distances(
            self.MESH, self.lons, self.lats, k=10, n_jobs=2
        )
        return distances, inds

    def _load_or_create_weights_distances(self):
        if not self._interpolation_weights_available():
            distances, inds = self._calculate_weights_distances()
            np.savez(self._interpolation_file, distances=distances, inds=inds)
        else:
            npzfile = np.load(self._interpolation_file + ".npz")
            distances, inds = npzfile["distances"], npzfile["inds"]
        return distances, inds

    def _interpolate_to_regular_grid(self):
        """
        Calls ``pf.fesom2regular`` to interpolate to a regular grid using
        nearest-neighbor interpolation.
        """
        # TODO: It'd be nice to include the math in the method docstring along
        # with a reference
        #
        # NOTE: This probably doesn't need to be a private method
        print(
            "\nPerforming nearest-neighbor interpolation onto a 0.25 x 0.25 degree regular grid:"
        )
        # QUESTION: This seems to loop over all the levels. Is that really what
        # we want here?

        distances, inds = self._load_or_create_weights_distances()

        if self.timintv is not None:
            nearest = []

            for level_data_tmp in self.level_data:
                nearest.append(
                    pf.fesom2regular(
                        level_data_tmp,
                        self.MESH,
                        self.lons,
                        self.lats,
                        distances=distances,
                        inds=inds,
                    )
                )
            self.nearest = nearest
        else:
            nearest = pf.fesom2regular(
                self.level_data,
                self.MESH,
                self.lons,
                self.lats,
                distances=distances,
                inds=inds,
            )
            # Add an empty array dimension for the timestep
            self.nearest = np.expand_dims(nearest, axis=0)

    ############################################################################

    def determine_variable_dict_from_outdata_contents(self):
        # FIXME: File patterns are inconsistent, this is a "bad feature" in
        # esm-runscripts:fesom_post_processing.
        #
        # IDEA: We can embed this information in the top-of-exp-tree file
        # and ask for it if not there.
        return getattr(self, "_var_dict_" + self.NAMING_CONVENTION)()

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
                mesh=self.MESH,
                levelwise_output=self.LEVELWISE_OUTPUT,
                mesh_rotated=self.MESH_ROTATED,
                naming_convention="esm_new",
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

    def yseasmean(self, varname):
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
                + "_yseasmean.nc",
                timintv="season",
                mesh=self.MESH,
                levelwise_output=self.LEVELWISE_OUTPUT,
                naming_convention="esm_new",
                mesh_rotated=self.MESH_ROTATED,
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
            + "_yseasmean.nc"
        )

    def ymonmean(self, varname):
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
                + "_ymonmean.nc",
                timintv="month",
                mesh=self.MESH,
                levelwise_output=self.LEVELWISE_OUTPUT,
                naming_convention="esm_new",
                mesh_rotated=self.MESH_ROTATED,
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
            + "_ymonmean.nc"
        )

    def AMOC(self):
        """
        Generates AMOC from vertical velocities.
        """
        # Steps:
        # 1. Gather wo files
        # 2. Get mask file
        # 3.
