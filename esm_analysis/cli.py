# @Author: Paul Gierz <pgierz>
# @Date:   2020-01-31T19:03:13+01:00
# @Email:  pgierz@awi.de
# @Filename: cli.py
# @Last modified by:   pgierz
# @Last modified time: 2020-02-03T12:41:49+01:00


# -*- coding: utf-8 -*-

"""
Console script for esm_analysis.

This section describes how to use the command line interface

There are 2 top level flags that can be set: ``--debug`` or ``--verbose``. If
both are given, ``--debug`` has precedence.

Entering ``esm_viz --help`` prints a list of currently implemented methods.

The individual operators are documented below.
"""
import logging
import sys

import click
from esm_analysis.logfile import Logfile
import tabulate

from esm_analysis import EsmAnalysis


@click.group()
@click.option("--debug", default=False, is_flag=True)
@click.option("--verbose", default=False, is_flag=True)
@click.version_option()
def main(args=None, verbose=False, debug=False):
    """Console script for esm_analysis."""
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    elif verbose:
        logging.basicConfig(level=logging.INFO)
    return 0


@main.command()
@click.argument("varname")
@click.option("--preferred_analysis_dir", default=None)
def fldmean(varname, preferred_analysis_dir=None):
    """Fldmean generator

    Parameters
    ----------
    varname : str
        The variable name to make a fldmean for. This will automatically figure
        out which model ``varname`` belongs to.

    Examples
    --------

    ..code ::

        $ esm_analysis fldmean temp2
    """
    click.echo("This will generate a fldmean for: %s" % varname)
    click.echo("You passed in preferred_analysis_dir: %s" % preferred_analysis_dir)
    analyzer = EsmAnalysis(preferred_analysis_dir=preferred_analysis_dir)
    analyzer.initialize_analysis_components(
        preferred_analysis_dir=preferred_analysis_dir
    )
    analyzer.fldmean(varname)


@main.command()
@click.argument("varname")
@click.option("--preferred_analysis_dir", default=None)
def ymonmean(varname, preferred_analysis_dir=None):
    """Fldmean generator

    Parameters
    ----------
    varname : str
        The variable name to make a ymonmean for. This will automatically figure
        out which model ``varname`` belongs to.

    Examples
    --------

    ..code ::

        $ esm_analysis ymonmean temp2
    """
    click.echo("This will generate a ymonmean for: %s" % varname)
    if preferred_analysis_dir:
        click.echo("You passed in preferred_analysis_dir: %s" % preferred_analysis_dir)
    analyzer = EsmAnalysis(preferred_analysis_dir=preferred_analysis_dir)
    analyzer.initialize_analysis_components(
        preferred_analysis_dir=preferred_analysis_dir
    )
    analyzer.ymonmean(varname)


@main.command()
@click.argument("varname")
@click.option("--preferred_analysis_dir", default=None)
def yseasmean(varname, preferred_analysis_dir=None):
    """Fldmean generator

    Parameters
    ----------
    varname : str
        The variable name to make a yseasmean for. This will automatically figure
        out which model ``varname`` belongs to.

    Examples
    --------

    ..code ::

        $ esm_analysis yseasmean temp2
    """
    click.echo("This will generate a yseasmean for: %s" % varname)
    if preferred_analysis_dir:
        click.echo("You passed in preferred_analysis_dir: %s" % preferred_analysis_dir)
    analyzer = EsmAnalysis(preferred_analysis_dir=preferred_analysis_dir)
    analyzer.initialize_analysis_components(
        preferred_analysis_dir=preferred_analysis_dir
    )
    analyzer.yseasmean(varname)


@main.command()
@click.argument("varname")
@click.option("--preferred_analysis_dir", default=None)
def newest_climatology(varname, preferred_analysis_dir):
    """
    Newest climatology
    """
    click.echo("This will generate the newest climatology for: %s" % varname)
    analyzer = EsmAnalysis(preferred_analysis_dir=preferred_analysis_dir)
    analyzer.initialize_analysis_components(
        preferred_analysis_dir=preferred_analysis_dir
    )
    analyzer.newest_climatology(varname)


@main.command()
@click.argument("fname", type=click.Path(exists=True))
def logfile_stats(fname):
    log = Logfile.from_file(fname)
    run_stats = log.run_stats()
    print(tabulate.tabulate(run_stats, headers="keys", tablefmt="psql"))


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
