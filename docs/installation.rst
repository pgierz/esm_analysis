.. highlight:: shell

============
Installation
============

Roadmap
-------

Currently, this software is still in "alpha" mode. Features are still being
actively developed, and the API is not stable. There is a planned ``1.0.0``
release once the following has been achieved:

+ ECHAM6 climatologies, ymonmean, yseasmean, and anomaly vs. a different run
+ FESOM for the same; plus AMOC
+ Easy checks for throughput, walltime, queue time
+ For Martin: isotopes
+ For Monica: some sort of stats stuff
+ For myself: PISM stuff
+ For general sanity: documentation, useful testing, python-version independent

For planning:

+ **Everything** should return an ``xarray`` object, where appropriate.
+ Library usage needs to be independent of where it is started from.

Stable release
--------------

.. warning::
    There is no "Stable release" yet!

To install ESM Analysis, run this command in your terminal:

.. code-block:: console

    $ pip install esm_analysis

This is the preferred method to install ESM Analysis, as it will always install the most recent stable release.

If you don't have `pip`_ installed, this `Python installation guide`_ can guide
you through the process.

Please note that if you need to use the ``--user`` flag in ``pip``, the program
will be installed in ``${HOME}/.local/bin``, which may not be on your ``$PATH``.
For more information, see the `pip`_ documentation.

.. _pip: https://pip.pypa.io
.. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/

From sources
------------

The sources for ESM Analysis can be downloaded from the `Github repo`_.

You can either clone the public repository:

.. code-block:: console

    $ git clone git://github.com/pgierz/esm_analysis

Or download the `tarball`_:

.. code-block:: console

    $ curl  -OL https://github.com/pgierz/esm_analysis/tarball/master

Once you have a copy of the source, you can install it with:

.. code-block:: console

    $ python setup.py install


.. _Github repo: https://github.com/pgierz/esm_analysis
.. _tarball: https://github.com/pgierz/esm_analysis/tarball/master
