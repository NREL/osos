"""
osos base class.
"""
import datetime
import os
import pandas as pd
import logging
from osos.api_github import Github
from osos.api_pypi import Pypi


OSOS_DIR = os.path.dirname(os.path.realpath(__file__))
DATA_DIR = os.path.join(os.path.dirname(OSOS_DIR), 'data')

logger = logging.getLogger(__name__)


class Osos:
    """Base class to handle open source ops and statistics (osos) for a given
    repo/package.
    """

    def __init__(self, git_owner, git_repo, pypi_name=None):
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
        """

        self._git_owner = git_owner
        self._git_repo = git_repo
        self._pypi_name = pypi_name

        self._gh = Github(self._git_owner, self._git_repo)

    @staticmethod
    def clean_table(table):
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
        d0 = datetime.date.today()
        d1 = datetime.date.today() - datetime.timedelta(days=13)
        index = pd.date_range(d1, d0, freq='1D').date
        table = table.reindex(index)

        cols = ['clones', 'clones_unique', 'views', 'views_unique', 'commits']
        table[cols] = table[cols].fillna(0)

        cols = ['issues_closed_count', 'issues_closed_mean_lifetime',
                'issues_closed_median_lifetime', 'issues_open_count',
                'issues_open_mean_lifetime', 'issues_open_median_lifetime',
                'pulls_closed_count', 'pulls_closed_mean_lifetime',
                'pulls_closed_median_lifetime', 'pulls_open_count',
                'pulls_open_mean_lifetime', 'pulls_open_median_lifetime',
                'forks', 'stargazers', 'subscribers', 'contributors',
                'total_commits', 'updated_on']
        table[cols] = table[cols].ffill().bfill()
        table[cols] = table[cols].fillna(0)

        if 'pypi_daily' in table:
            table['pypi_daily'] = table['pypi_daily'].fillna(0)
            table['pypi_180_cumulative'] = table['pypi_180_cumulative']\
                .ffill().bfill()

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

        table = self._gh.clones()
        table = table.join(self._gh.views(), how='outer')
        iend = table.index.values[-1]

        keys = ('{op1}_{op2}_count', '{op1}_{op2}_mean_lifetime',
                '{op1}_{op2}_median_lifetime')
        issues_pulls = (self._gh.issues_closed(),
                        self._gh.issues_open(),
                        self._gh.pulls_closed(),
                        self._gh.pulls_open())
        options = (('issues', 'closed'), ('issues', 'open'),
                   ('pulls', 'closed'), ('pulls', 'open'))

        for ip_dict, (op1, op2) in zip(issues_pulls, options):
            for k in keys:
                column = k.format(op1=op1, op2=op2)
                table.at[iend, column] = ip_dict[column]
                table[column] = table[column].round(1)

        table.at[iend, 'forks'] = self._gh.forks()
        table.at[iend, 'stargazers'] = self._gh.stargazers()
        table.at[iend, 'subscribers'] = self._gh.subscribers()
        table.at[iend, 'contributors'] = self._gh.contributors()

        commits = self._gh.commits(table.index.values)
        table = table.join(commits, how='outer')
        table.at[iend, 'total_commits'] = self._gh.commit_count()

        if self._pypi_name is not None:
            pypi_out = Pypi.get_daily_data(self._pypi_name, table.index.values)
            table = table.join(pypi_out, how='outer')

        table['updated_on'] = datetime.date.today()
        table = self.clean_table(table)

        return table

    def update(self, fpath_out):
        """Update and save the fpath_out file. The current update data will be
        used if there are duplicates.

        Parameters
        ----------
        fpath_out : str
            Full filepath to a .csv that the osos table should be saved and
            updated at. This path can include the "DATA_DIR" keyword which will
            get replaced by the system location of the /osos/data/ directory.

        Returns
        -------
        table : pd.DataFrame
            osos table including the original data from fpath_out (if exists)
            updated with the currently available data from github and pypi.
            This is also saved to fpath_out.
        """
        fpath_out = fpath_out.replace('DATA_DIR', DATA_DIR)
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
        Path to .csv config file with columns for name, git_owner, git_repo,
        pypi_name, and fpath_out.
        """

        assert os.path.exists(config), 'config must be a valid filepath'
        assert config.endswith('.csv'), 'config must be .csv'
        config = pd.read_csv(config)

        required = ('name', 'git_owner', 'git_repo', 'fpath_out')
        missing = [r for r in required if r not in config]
        if any(missing):
            msg = f'Config had missing required columns: {missing}'
            logger.error(msg)
            raise KeyError(msg)

        for _, row in config.iterrows():
            row = row.to_dict()
            pypi_name = row.get('pypi_name', None)
            pypi_name = pypi_name if isinstance(pypi_name, str) else None
            osos = cls(row['git_owner'], row['git_repo'],
                       pypi_name=pypi_name)
            fpath_out = row['fpath_out'].replace('DATA_DIR', DATA_DIR)
            osos.update(fpath_out)
