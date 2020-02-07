============
ESM Analysis
============


.. image:: https://img.shields.io/pypi/v/esm_analysis.svg
        :target: https://pypi.python.org/pypi/esm_analysis

.. image:: https://img.shields.io/travis/pgierz/esm_analysis.svg
        :target: https://travis-ci.org/pgierz/esm_analysis

.. image:: https://readthedocs.org/projects/esm-tools-analysis/badge/?version=latest
        :target: https://esm-tools-analysis.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status


Analysis Scripts for ESM Simulations


Quickstart
----------

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

Isn't that better than this? (Note that the counterexample is purposefully "over-the-top")

.. code-block:: shell

    outdata_dir=... # oh man now I need to figure out where the outdata is
    expid=PI # ...uh...PI, I guess?...
    outfile=test.nc # ...I guess I should think of a real name for my output
    vars=temp2 # Oh! I know that one!
    filepattern="echam6_echam"
    fileext=".nc" # Aww geez I have no idea. Is it nc? grb? Let's just guess...
    # How did cdo work again?
    cdo -h select
    cdo -h timmmean
    # Ok, now I think I know what I want:
    cdo -f nc -t echam6 -timmean -select,name=$vars ${outdata_dir}/${expid}_${filepattern}${fileext} $outfile

I'd support the following hypothesis: you clearly don't want to type all that stuff
out. Just say what you want. Easy, right?

The computer should be able to figure out the rest for you. If Google can
predict where I get my breakfast, why can't my computer figure out what ``CDO``
command I want to use??

Features!
---------

* Command line interface: Quickly create common analyses!
* Python library usage: Same analysis as with the CLI, but you get back usable `xarray.Dataset <http://xarray.pydata.org/en/stable/generated/xarray.Dataset.html>`_ objects! Just do ``temp2_plot = analyzer("temp2").plot()`` to get a matplotlib plot!
* Free software: GNU General Public License v3!
* Documentation: https://esm-tools-analysis.readthedocs.io!


