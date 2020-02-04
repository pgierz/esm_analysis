Welcome to ESM Analysis's documentation!
========================================

This is the documentation for ``esm_analysis``, a command line interface and
Python module for stream-lining analysis of Earth System Model output produced
with the ``esm-tools``.

.. include:: ../QUICKSTART.rst

For more information, see the more detailed documentation below.

Quickstart
==========

``esm_analysis`` is the sugar for your bitter CDO-coffee. Check it out:

Install ``esm_analysis`` with::

    pip install esm_analysis

Go to an experiment::

    cd /work/ba0989/a270077/AWICM_PISM/LGM_011

Get a climatology::

    esm_analysis newest-climatology temp2
    esm_analysis newest-climatology thetao

Calculate AMOC::

    esm_analysis amoc

For more information, see the more detailed documentation below.

Contents
========
.. toctree::
   :maxdepth: 2
   :caption: Contents:

   readme
   installation
   usage
   modules
   history

Indices and tables
==================
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. If interested, add: contributing authors to toctree. For now it is deactivated.
