# -*- coding: utf-8 -*-
"""
OSOS command line interface (CLI)
"""
import click
import logging
from rex import init_logger
from osos.osos import Osos
from osos.version import __version__


logger = logging.getLogger(__name__)


@click.command()
@click.version_option(version=__version__)
@click.option('--config', '-c', default=None, required=False,
              type=click.Path(exists=True),
              help='Path to .csv config file with columns for git_owner, '
              'git_repo, fpath_out, and (optionally) pypi_name, conda_org, '
              'and conda_name. Either input this for multiple osos jobs or '
              'all of the argument explicitly for a single osos job.')
@click.option('--git_owner', '-go', required=False, default=None, type=str,
              help='Github repository owner, e.g. '
              'https://github.com/{git_owner}/{git_repo}. Case insensitive.')
@click.option('--git_repo', '-gr', required=False, default=None, type=str,
              help='Github repository name, e.g. '
              'https://github.com/{git_owner}/{git_repo}. Case insensitive.')
@click.option('--pypi_name', '-pn', required=False, default=None, type=str,
              help='pypi package name. Note that this should include the '
              'prefix for nrel packages e.g. reV -> nrel-rev. This can be '
              'None if there is no pypi package. Case insensitive.')
@click.option('--conda_org', '-co', required=False, default=None, type=str,
              help='Conda organization name, for example: '
              'https://anaconda.org/{org}/{name}. Case insensitive.')
@click.option('--conda_name', '-cn', required=False, default=None, type=str,
              help='Conda package name, for example: '
              'https://anaconda.org/{org}/{name}. Case insensitive.')
@click.option('--fpath_out', '-f', required=False, default=None, type=str,
              help='Output file to save the osos output table. If the file '
              'exists, it will be updated with the latest data. This path can '
              'include the keywords "DATA_DIR" and "NAME" which will get '
              'replaced by the system location of the /osos/data/ directory '
              'and the github repo name, respectively.')
@click.option('-v', '--verbose', is_flag=True,
              help='Flag to turn on debug logging. Default is not verbose.')
@click.pass_context
def main(ctx, config, git_owner, git_repo, pypi_name, conda_org, conda_name,
         fpath_out, verbose):
    """OSOS command line interface (CLI). Try running `osos --help`."""

    ctx.ensure_object(dict)

    msg = ('Need to input either config or (git_owner & git_repo & '
           'fpath_out)! Also maybe try "osos --help" to see the cli '
           'help page.')
    c1 = (config is not None)
    c2 = (git_owner is not None and git_repo is not None
          and fpath_out is not None)
    assert c1 or c2, msg

    if verbose:
        init_logger('osos', log_level='DEBUG')
    else:
        init_logger('osos', log_level='INFO')

    if c1:
        Osos.run_config(config)
    else:
        osos = Osos(git_owner, git_repo, pypi_name=pypi_name,
                    conda_org=conda_org, conda_name=conda_name)
        osos.update(fpath_out)


if __name__ == '__main__':
    try:
        main(obj={})
    except Exception as e:
        msg = 'Error running osos cli!'
        logger.exception(msg)
        raise RuntimeError(msg) from e
