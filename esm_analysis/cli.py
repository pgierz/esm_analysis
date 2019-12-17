# -*- coding: utf-8 -*-

"""Console script for esm_analysis."""
import sys
import click

from esm_analysis import EsmAnalysis

@click.group()
def main(args=None):
    """Console script for esm_analysis."""
    click.echo(
        "Replace this message by putting your code into " "esm_analysis.cli.main"
    )
    click.echo("See click documentation at http://click.pocoo.org/")
    return 0

@main.command()
@click.argument('varname')
def fldmean(varname):
    """Fldmean generator

    Parameters
    ----------
    varname : str
        The variable name to make a fldmean for. This will automatically figure
        out which model ``varname`` belongs to.

    Examples
    --------

    ..code:
        $ esm_analysis fldmean temp2
    """
    click.echo("This will generate a fldmean for: %s" % varname)
    analyzer = EsmAnalysis()
    analyzer.create_analysis_dir()
    analyzer.initialize_analysis_components()
    analyzer.fldmean(varname)


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
