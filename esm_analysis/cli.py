# -*- coding: utf-8 -*-

"""Console script for esm_analysis."""
import logging
import sys

import click

from esm_analysis import EsmAnalysis


@click.group()
@click.option("--verbose", default=False, is_flag=True)
def main(args=None, verbose=False):
    """Console script for esm_analysis."""
    if verbose:
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


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
