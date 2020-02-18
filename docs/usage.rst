======================
Command Line Interface
======================

The ESM Analysis software provides a command line interface for common
operations you may want to perform on model output. To see which operators are
available::

	$ esm_analysis —-help

This will print a list of currently implemented subcommands. For suggestions,
improvements, or feature requests, please open an issue.

Effectively, the command line interface provides “syntax sugar” around several
``CDO`` commands to take away some of the overhead, including:

* Automatic awareness of file and directory locations
* Avoids reprocessing already existing analysis
* Uniform, semantic output file names in organized subdirectories

This eases some of the problems commonly experiences when sharing data with
colleagues, such as:

* Different preferences in filenames (``esm_analysis`` does this for you)
* No ambiguity in what sort of analysis you are getting (``esm_analysis``
  clearly marks what it does)

You can execute ``esm_analysis`` from anywhere within an experiment tree. It
doesn’t matter if you are in ``outdata``, ``analysis``, ``work``, ``restart``,
the top of the experiment, or an arbitrarily deep subfolder. The only
pre-requisite here is that a file ``.top_of_experiment`` is in the top level
directory. If this is not found, and ``esm_analysis`` finds the root of the
filesystem, it will ask you for assistance.

Example
-------

Let’s say you want to make a globally spatial average of ``temp2``, the 2 meter
near surface air temperature. From anywhere in the experiment, just say::

	$ esm_analysis fldmean temp2

``esm_analysis`` will figure out that:

* ``temp2`` is an echam variable
* which files in echam have ``temp2`` information (if more than one, it will ask
  which files you want to use)
* Make an analysis directory for you
* Generate a file ``${EXP_ID}_echam6_temp2_fldmean.nc``

===========
Preferences
===========

Certain parts of ``esm_analysis`` can be configured. In particular, it is
possible to control if filepatterns for certain variables are saved or not. As
an example, imagine if you wanted to get a ``fldmean`` for the variable
``tsurf``. By default, the


=============
Library Usage
=============

To use ESM Analysis in a project::

    import esm_analysis

The ESM Analysis module allows for creation of several common analyis from
Python objects.

The main object you probably want to use is: ``EsmAnalysis``. You can create one
like this, if you are currently working within an experiment directory::

    from esm_analysis import EsmAnalysis
    analyser = EsmAnalysis()

Optionally, you can give it a path where to start from::

    analyser = EsmAnalysis(exp_base="/work/ba0989/a270077/AWICM_PISM/LGM_011")

You can also tell it where to store analysis::

    analyser = EsmAnalysis(preferred_analysis_dir="/work/ba0989/a270077/store_analysis_here")

The ``analyser`` that was just created still needs to be initialized. This
serves to figure out which components you were using and to populate information
regarding which variables can be found in which files::

    analyser.initialize_analysis_components()

Once you have created the ``analyzer`` object, you can use the attached methods
to quickly get some typical analyses. The methods always return an
``xarray.Dataset`` object. Typically, the only required argument is the variable
name::

    t2m_fldmean = analyser.fldmean("temp2")
