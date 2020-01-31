======================
Command Line Interface
======================

The ESM Analysis software provides a command line interface for common operations you may want to perform on model output. To see which operators are available::

	$ esm_analysis —-help

This will print a list of currently implemented subcommands. For suggestions, improvements, or feature requests, please open an issue.

Effectively, the command line interface provides “syntax sugar” around several ``CDO`` commands to take away some of the overhead, including:

* Automatic awareness of file and directory locations
* Avoids reprocessing already existing analysis
* Uniform, semantic output file names in organized subdirectories

This eases some of the problems commonly experiences when sharing data with colleagues, such as:

* Different preferences in filenames (``esm_analysis`` does this for you)
* No ambiguity in what sort of analysis you are getting (``esm_analysis`` clearly marks what it does)

You can execute ``esm_analysis`` from anywhere within an experiment tree. It doesn’t matter if you are in ``outdata``, ``analysis``, ``work``, ``restart``, the top of the experiment, or an arbitrarily deep subfolder. The only pre-requisite here is that a file ``.top_of_experiment`` is in the top level directory. If this is not found, and ``esm_analysis`` finds the root of the filesystem, it will ask you for assistance.

Example
=======

Let’s say you want to make a globally spatial average of ``temp2``, the 2 meter near surface air temperature. From anywhere in the experiment, just say::

	$ esm_analysis fldmean temp2

``esm_analysis`` will figure out that:

* ``temp2`` is an echam variable
* which files in echam have ``temp2`` information (if more than one, it will ask which files you want to use)
* Make an analysis directory for you
* Generate a file ``${EXP_ID}_echam6_temp2_fldmean.nc``

=====
Usage
=====

To use ESM Analysis in a project::

    import esm_analysis
