"""
osos base class.
"""
import datetime
import os
import pandas as pd
import logging
from warnings import warn
from osos.api_github import Github
from osos.api_pypi import Pypi
from osos.api_conda import Conda


OSOS_DIR = os.path.dirname(os.path.realpath(__file__))
DATA_DIR = os.path.join(os.path.dirname(OSOS_DIR), 'data')

logger = logging.getLogger(__name__)


class Osos:
    """Base class to handle open source ops and statistics (osos) for a given
    repo/package.
    """

    def __init__(self, git_owner, git_repo, pypi_name=None, conda_org=None,
                 conda_name=None):
        """
        Parameters
        ----------
        git_owner : str
            Github repository owner, e.g. https://github.com/{owner}/{repo}.
            Case insensitive.
        git_repo : str
            Github repository name, e.g. https://github.com/{owner}/{repo}.
            Case insensitive.
        pypi_name : str | None
            pypi package name. Note that this should include the prefix for
            nrel packages e.g. reV -> nrel-rev. This can be None if there is no
            pypi package. Case insensitive.
        conda_org : str
            Conda organization name, for example:
            https://anaconda.org/{org}/{name}. Case insensitive.
        conda_name : str
            Conda package name, for example:
            https://anaconda.org/{org}/{name}. Case insensitive.
        """

        self._git_owner = git_owner
        self._git_repo = git_repo
        self._pypi_name = pypi_name
        self._conda_org = conda_org
        self._conda_name = conda_name

        self._gh = Github(self._git_owner, self._git_repo)

        d0 = datetime.date.today()
        d1 = datetime.date.today() - datetime.timedelta(days=13)
        self._index = pd.date_range(d1, d0, freq='1D').date

    def clean_table(self, table):
        """Fill nan values and make sure the timeseries index has 14 days.

        Parameters
        ----------
        table : pd.DataFrame
            Repository usage and statistics table with datetime.date index for
            the last two weeks including today and columns for various
            github and pypi usage metrics.

        Returns
        -------
        table : pd.DataFrame
            Repository usage and statistics table with datetime.date index for
            the last two weeks including today and columns for various
            github and pypi usage metrics.
        """

        table = table.reindex(self._index)

        timeseries_cols = ['clones', 'clones_unique', 'views', 'views_unique',
                           'commits', 'pypi_daily']
        timeseries_cols = [c for c in table.columns if c in timeseries_cols]
        other_cols = [c for c in table.columns if c not in timeseries_cols]

        table[timeseries_cols] = table[timeseries_cols].fillna(0)

        table[other_cols] = table[other_cols].ffill().bfill()
        table[other_cols] = table[other_cols].fillna(0)

        return table

    def make_table(self):
        """Make the usage and statistics table for the last two weeks.

        Returns
        -------
        table : pd.DataFrame
            Repository usage and statistics table with datetime.date index for
            the last two weeks including today and columns for various
            github and pypi usage metrics.
        """

        logger.info('Collecting data for: '
                    f'"{self._git_owner}/{self._git_repo}"')

        table = pd.DataFrame(index=self._index)

        try:
            table = table.join(self._gh.clones())
            table = table.join(self._gh.views())
        except OSError:
            msg = ('Could not get github clone/views data from '
                   f'"{self._git_owner}/{self._git_repo}", '
                   'try setting a GITHUB_TOKEN with push permissions.')
            warn(msg)
            logger.warning(msg)

        issues_pulls = (self._gh.issues_closed(),
                        self._gh.issues_open(),
                        self._gh.pulls_closed(),
                        self._gh.pulls_open())
        options = (('issues', 'closed'), ('issues', 'open'),
                   ('pulls', 'closed'), ('pulls', 'open'))

        for ip_count, (op1, op2) in zip(issues_pulls, options):
            table[f'{op1}_{op2}'] = ip_count

        table['forks'] = self._gh.forks()
        table['stargazers'] = self._gh.stargazers()
        table['subscribers'] = self._gh.subscribers()
        table['contributors'] = self._gh.contributors()

        table = table.join(self._gh.commits(date_iter=self._index))
        table['total_commits'] = self._gh.commit_count()

        if self._pypi_name is not None:
            pypi_out = Pypi.get_daily_data(self._pypi_name, table.index.values)
            table = table.join(pypi_out)

        if self._conda_org is not None and self._conda_name is not None:
            conda_out = Conda.get_data(self._conda_org, self._conda_name)
            table['conda_total_downloads'] = conda_out

        table['updated_on'] = datetime.date.today()
        table = self.clean_table(table)

        return table

    def update(self, fpath_out):
        """Update and save the fpath_out file. The current update data will be
        used if there are duplicates.

        Parameters
        ----------
        fpath_out : str
            Output file to save the osos output table. If the file exists, it
            will be updated with the latest data. This path can include the
            keywords "DATA_DIR" and "NAME" which will get replaced by the
            system location of the /osos/data/ directory and the github repo
            name, respectively.

        Returns
        -------
        table : pd.DataFrame
            osos table including the original data from fpath_out (if exists)
            updated with the currently available data from github and pypi.
            This is also saved to fpath_out.
        """

        fpath_out = fpath_out.replace('DATA_DIR', DATA_DIR)
        fpath_out = fpath_out.replace('NAME', self._git_repo)

        table = self.make_table()
        if os.path.exists(fpath_out):
            logger.info(f'Updating cached file: {fpath_out}')
            original = pd.read_csv(fpath_out, index_col=0)
            original.index = pd.to_datetime(original.index.values).date
            table = table.append(original)
            table = table[~table.index.duplicated(keep='first')]
            table = table.sort_index()

        logger.info(f'Saved osos output to: {fpath_out}')
        table.to_csv(fpath_out)
        return table

    @classmethod
    def run_config(cls, config):
        """Run multiple osos jobs from a csv config.

        Parameters
        ----------
        config : str
            Path to .csv config file with columns for git_owner, git_repo,
            fpath_out, and (optionally) pypi_name, conda_org, and conda_name.
        """

        assert os.path.exists(config), 'config must be a valid filepath'
        assert config.endswith('.csv'), 'config must be .csv'
        config = pd.read_csv(config)

        required = ('git_owner', 'git_repo', 'fpath_out')
        missing = [r for r in required if r not in config]
        if any(missing):
            msg = f'Config had missing required columns: {missing}'
            logger.error(msg)
            raise KeyError(msg)

        for _, row in config.iterrows():
            row = row.to_dict()

            conda_org = row.get('conda_org', None)
            conda_name = row.get('conda_name', None)
            pypi_name = row.get('pypi_name', None)
            conda_org = conda_org if isinstance(conda_org, str) else None
            conda_name = conda_name if isinstance(conda_name, str) else None
            pypi_name = pypi_name if isinstance(pypi_name, str) else None

            fpath_out = row['fpath_out'].replace('DATA_DIR', DATA_DIR)
            fpath_out = row['fpath_out'].replace('NAME', row['git_repo'])

            osos = cls(row['git_owner'], row['git_repo'],
                       pypi_name=pypi_name,
                       conda_org=conda_org,
                       conda_name=conda_name)

            osos.update(fpath_out)
