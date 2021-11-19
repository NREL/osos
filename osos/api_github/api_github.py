# -*- coding: utf-8 -*-
"""
Interface module for github API
"""
import re
import datetime
import numpy as np
import pandas as pd
import requests
import os
import logging


logger = logging.getLogger(__name__)


class Github:
    """Class to call github api and return osos-formatted usage data."""

    BASE_REQ = 'https://api.github.com/repos/{owner}/{repo}'
    TIME_FORMAT = '%Y-%m-%dT%H:%M:%SZ'

    def __init__(self, owner, repo, token=None):
        """
        Parameters
        ----------
        owner : str
            Repository owner, e.g. https://github.com/{owner}/{repo}
        repo : str
            Repository name, e.g. https://github.com/{owner}/{repo}
        token : str | None
            Github api authorization token. If none this gets retrieved from
            the GITHUB_TOKEN environment variable
        """

        self._owner = owner
        self._repo = repo
        self.base_req = self.BASE_REQ.format(owner=owner, repo=repo)

        self.token = token
        if self.token is None:
            self.token = os.getenv('GITHUB_TOKEN', None)
            if self.token is None:
                msg = 'Could not find environment variable "GITHUB_TOKEN".'
                logger.error(msg)
                raise OSError(msg)
            else:
                logger.debug('Using github token from environment variable '
                             '"GITHUB_TOKEN".')
        else:
            logger.debug('Using github token from kwarg input to osos.')

    def __str__(self):
        st = (f'Github API interface for https://github.com/'
              f'{self._owner}/{self._repo}/')
        return st

    def __repr__(self):
        return str(self)

    def get_issues_pulls(self, option='issues', state='open',
                         get_lifetimes=False, **kwargs):
        """Get open/closed issues/pulls for the repo (all have the same
        general parsing format)

        Parameters
        ----------
        option : str
            "issues" or "pulls"
        state : str
            "open" or "closed"
        get_lifetimes : bool
            Flag to get the lifetime statistics of issues/pulls. Default is
            false to reduce number of API queries. Turning this on requires
            that we get the full data for every issue/pull. It is recommended
            that users retrieve lifetime statistics manually when desired and
            not as part of an automated OSOS workflow.
        kwargs : dict
            Optional kwargs to get passed to requests.get()

        Returns
        -------
        out : int | dict
            Integer count of the number of issues/pulls if get_lifetimes=False,
            or a dict Namespace with keys: "{option}_{state}" and
            "{option}_{state}_*" for count, lifteimtes, and mean/median
            lifetime in days
        """

        # github api has max 100 items per page. Use max to reduce the total
        # number of requests.
        if 'params' in kwargs:
            kwargs['params']['state'] = state
            kwargs['params']['per_page'] = 100
        else:
            kwargs['params'] = {'state': state, 'per_page': 100}

        request = self.base_req + f'/{option}'

        if not get_lifetimes and option == 'pulls':
            out = self._total_count(request, **kwargs)
            return out

        elif not get_lifetimes and option == 'issues':
            # pulls get listed as issues but not the other way around
            i_out = self._total_count(request, **kwargs)
            request = self.base_req + '/pulls'
            p_out = self._total_count(request, **kwargs)
            out = i_out - p_out
            return out

        else:
            items = self.get_generator(request, **kwargs)

            numbers = []
            lifetimes = []
            for item in items:
                d0 = item['created_at']
                d1 = item['closed_at']
                d0 = datetime.datetime.strptime(d0, self.TIME_FORMAT)
                if state == 'closed' and d1 is not None:
                    d1 = datetime.datetime.strptime(d1, self.TIME_FORMAT)
                elif state == 'open':
                    d1 = datetime.datetime.now()

                assert d1 is not None, f'Bad final date for: {item}'

                # pulls get listed as issues but not the other way around
                condition_1 = option == 'pulls'
                condition_2 = option == 'issues' and 'pull_request' not in item

                if condition_1 or condition_2:
                    numbers.append(item['number'])
                    lifetime = (d1 - d0).total_seconds() / (24 * 3600)
                    lifetimes.append(lifetime)

            mean = np.nan if not any(lifetimes) else np.mean(lifetimes)
            median = np.nan if not any(lifetimes) else np.median(lifetimes)
            out = {f'{option}_{state}': numbers,
                   f'{option}_{state}_count': len(numbers),
                   f'{option}_{state}_lifetimes': lifetimes,
                   f'{option}_{state}_mean_lifetime': mean,
                   f'{option}_{state}_median_lifetime': median,
                   }

            return out

    def _traffic(self, option='clones', **kwargs):
        """Get the daily github repo traffic data for the last two weeks

        Parameters
        ----------
        option : str
            "clones" or "views"
        kwargs : dict
            Optional kwargs to get passed to requests.get()

        Returns
        -------
        out : pd.DataFrame
            Timeseries of daily git clone data. Includes columns for "views" or
            "clones" and "views_unique" or "clones_unique". Index is a pandas
            datetime index with just the datetime.date part.
        """
        request = self.base_req + f'/traffic/{option}'
        out = self.get_request(request, **kwargs).json()
        out = pd.DataFrame(out[option])

        if 'timestamp' in out:
            out.index = pd.to_datetime(out['timestamp']).dt.date
            out = out.drop('timestamp', axis=1)
        else:
            out = pd.DataFrame({'count': [0], 'uniques': [0]},
                               index=[datetime.date.today()])

        out.index.name = None
        out = out.rename({'count': option, 'uniques': f'{option}_unique'},
                         axis=1)
        return out

    def _total_count(self, request, **kwargs):
        """Get the total count of a request object without querying every page

        Parameters
        ----------
        request : str
            Request URL, example: "https://api.github.com/repos/NREL/reV/pulls"
        kwargs : dict
            Optional kwargs to get passed to requests.get()

        Returns
        -------
        out : int
            Total number of items in all pages of the request
        """

        req = self.get_request(request, **kwargs)
        num_pages = 1
        n_last = 0

        if 'last' in req.links:
            last_url = req.links['last']['url']
            match = re.search(r'page=[0-9]*$', last_url)
            if not match:
                msg = f'Could not find page=[0-9]*$ in url: {last_url}'
                logger.error(msg)
                raise RuntimeError(msg)

            num_pages = int(match.group().replace('page=', '')) - 1
            last_page = self.get_request(last_url, **kwargs)
            n_last = len(last_page.json())

        out = len(req.json()) * num_pages + n_last
        return out

    def get_request(self, request, **kwargs):
        """Get the raw request output object

        Parameters
        ----------
        request : str
            Request URL, example: "https://api.github.com/repos/NREL/reV/pulls"
        kwargs : dict
            Optional kwargs to get passed to requests.get()

        Returns
        -------
        out : requests.models.Response
            requests.get() output object.
        """

        headers = kwargs.pop('headers', {})
        if 'Authorization' not in headers:
            headers['Authorization'] = f'token {self.token}'

        out = requests.get(request, headers=headers, **kwargs)
        if out.status_code != 200:
            msg = ('Received unexpected status code "{}" for reason "{}".'
                   '\nRequest: {}\nOutput: {}'
                   .format(out.status_code, out.reason, request,
                           out.text))
            logger.error(msg)
            raise IOError(msg)

        return out

    def get_generator(self, request, **kwargs):
        """Call the github API using the requests.get() method and merge all
        the paginated results into a single output

        Parameters
        ----------
        request : str
            Request URL, example: "https://api.github.com/repos/NREL/reV/pulls"
        kwargs : dict
            Optional kwargs to get passed to requests.get()

        Returns
        -------
        out : generator
            generator of list items in the request output
        """

        headers = kwargs.pop('headers', {})
        if 'Authorization' not in headers:
            headers['Authorization'] = f'token {self.token}'

        params = kwargs.pop('params', {})
        params['page'] = 0

        while True:
            params['page'] += 1
            temp = requests.get(request, headers=headers, params=params,
                                **kwargs)
            if temp.status_code != 200:
                msg = ('Received unexpected status code "{}" for reason "{}".'
                       '\nRequest: {}\nOutput: {}'
                       .format(temp.status_code, temp.reason, request,
                               temp.text))
                logger.error(msg)
                raise IOError(msg)

            temp = temp.json()
            if not any(temp):
                break
            elif not isinstance(temp, list):
                msg = ('JSON output is type "{}", not list, could '
                       'not parse output from request: "{}"'
                       .format(type(temp), request))
                logger.error(msg)
                raise TypeError(msg)
            else:
                for entry in temp:
                    yield entry

    def contributors(self, **kwargs):
        """Get the number of repo contributors

        Parameters
        ----------
        kwargs : dict
            Optional kwargs to get passed to requests.get()

        Returns
        -------
        out : int
            Number of contributors for the repo.
        """
        logger.debug(f'Getting contributors for "{self._owner}/{self._repo}"')
        request = self.base_req + '/contributors'
        count = self._total_count(request, **kwargs)
        return count

    def commit_count(self, **kwargs):
        """Get the number of repo commits

        Parameters
        ----------
        kwargs : dict
            Optional kwargs to get passed to requests.get()

        Returns
        -------
        out : int
            Total number of commits to the repo.
        """
        logger.debug(f'Getting commit count for "{self._owner}/{self._repo}"')
        request = self.base_req + '/commits'
        out = self._total_count(request, **kwargs)
        return out

    def commits(self, date_start=None, date_iter=None, search_all=False,
                **kwargs):
        """Get the number of commits by day in a given set of dates.

        Parameters
        ----------
        date_start : datetime.date | None
            Option to search for commits from this date to today. Either input
            this or the date_iter.
        date_iter : list | tuple | pd.DatetimeIndex | None
            Iterable of dates to search for. Either input this or the
            date_start.
        search_all : bool
            Flag to search all commits or to terminate early (default) when the
            commit date is before all dates in the date_iter
        kwargs : dict
            Optional kwargs to get passed to requests.get()

        Returns
        -------
        out : pd.DataFrame
            Timeseries of commit data based on date_iter as the index. Includes
            columns for "commits".
        """

        if date_start is not None:
            date_iter = pd.date_range(date_start, datetime.date.today())

        if date_iter is None:
            msg = 'Must either input date_start or date_iter!'
            logger.error(msg)
            raise RuntimeError(msg)

        logger.debug('Getting commit history for '
                     f'"{self._owner}/{self._repo}"')
        out = pd.DataFrame(index=date_iter)
        out['commits'] = 0
        request = self.base_req + '/commits'
        commit_iter = self.get_generator(request, **kwargs)
        for com in commit_iter:
            c_date = com['commit']['committer']['date']
            c_date = datetime.datetime.strptime(c_date, self.TIME_FORMAT)
            c_date = c_date.date()
            stop = True
            for date in date_iter:
                if c_date == date:
                    out.at[date, 'commits'] += 1
                    stop = False
                    break
                elif c_date > date:
                    stop = False

            if stop and not search_all:
                break

        return out

    def clones(self, **kwargs):
        """Get the daily github repo clone data for the last two weeks.

        Parameters
        ----------
        kwargs : dict
            Optional kwargs to get passed to requests.get()

        Returns
        -------
        out : pd.DataFrame
            Timeseries of daily git clone data. Includes columns for "clones"
            and "clones_unique". Index is a pandas datetime index with just the
            datetime.date part.
        """
        logger.debug(f'Getting clones for "{self._owner}/{self._repo}"')
        return self._traffic(option='clones', **kwargs)

    def forks(self, **kwargs):
        """Get the number of repo forks.

        Parameters
        ----------
        kwargs : dict
            Optional kwargs to get passed to requests.get()

        Returns
        -------
        out : int
            The number of forks.
        """
        logger.debug(f'Getting forks for "{self._owner}/{self._repo}"')
        request = self.base_req + '/forks'
        count = self._total_count(request, **kwargs)
        return count

    def issues_closed(self, get_lifetimes=False, **kwargs):
        """Get data on the closed repo issues.

        Parameters
        ----------
        get_lifetimes : bool
            Flag to get the lifetime statistics of issues/pulls. Default is
            false to reduce number of API queries. Turning this on requires
            that we get the full data for every issue/pull. It is recommended
            that users retrieve lifetime statistics manually when desired and
            not as part of an automated OSOS workflow.
        kwargs : dict
            Optional kwargs to get passed to requests.get()

        Returns
        -------
        out : int | dict
            Number of closed issues, or if get_lifetimes is True, this returns
            a dict with additional metrics.
        """
        logger.debug(f'Getting closed issues for "{self._owner}/{self._repo}"')
        out = self.get_issues_pulls(option='issues', state='closed',
                                    get_lifetimes=get_lifetimes,
                                    **kwargs)
        return out

    def issues_open(self, get_lifetimes=False, **kwargs):
        """Get data on the open repo issues.

        Parameters
        ----------
        get_lifetimes : bool
            Flag to get the lifetime statistics of issues/pulls. Default is
            false to reduce number of API queries. Turning this on requires
            that we get the full data for every issue/pull. It is recommended
            that users retrieve lifetime statistics manually when desired and
            not as part of an automated OSOS workflow.
        kwargs : dict
            Optional kwargs to get passed to requests.get()

        Returns
        -------
        out : int | dict
            Number of open issues, or if get_lifetimes is True, this returns
            a dict with additional metrics.
        """
        logger.debug(f'Getting open issues for "{self._owner}/{self._repo}"')
        out = self.get_issues_pulls(option='issues', state='open',
                                    get_lifetimes=get_lifetimes,
                                    **kwargs)
        return out

    def pulls_closed(self, get_lifetimes=False, **kwargs):
        """Get data on the closed repo pull requests.

        Parameters
        ----------
        get_lifetimes : bool
            Flag to get the lifetime statistics of issues/pulls. Default is
            false to reduce number of API queries. Turning this on requires
            that we get the full data for every issue/pull. It is recommended
            that users retrieve lifetime statistics manually when desired and
            not as part of an automated OSOS workflow.
        kwargs : dict
            Optional kwargs to get passed to requests.get()

        Returns
        -------
        out : int | dict
            Number of closed pull requests, or if get_lifetimes is True, this
            returns a dict with additional metrics.
        """
        logger.debug(f'Getting closed pulls for "{self._owner}/{self._repo}"')
        out = self.get_issues_pulls(option='pulls', state='closed',
                                    get_lifetimes=get_lifetimes,
                                    **kwargs)
        return out

    def pulls_open(self, get_lifetimes=False, **kwargs):
        """Get data on the open repo pull requests.

        Parameters
        ----------
        get_lifetimes : bool
            Flag to get the lifetime statistics of issues/pulls. Default is
            false to reduce number of API queries. Turning this on requires
            that we get the full data for every issue/pull. It is recommended
            that users retrieve lifetime statistics manually when desired and
            not as part of an automated OSOS workflow.
        kwargs : dict
            Optional kwargs to get passed to requests.get()

        Returns
        -------
        out : int | dict
            Number of open pull requests, or if get_lifetimes is True, this
            returns a dict with additional metrics.
        """
        logger.debug(f'Getting open pulls for "{self._owner}/{self._repo}"')
        out = self.get_issues_pulls(option='pulls', state='open',
                                    get_lifetimes=get_lifetimes,
                                    **kwargs)
        return out

    def stargazers(self, **kwargs):
        """Get the number of repo stargazers

        Parameters
        ----------
        kwargs : dict
            Optional kwargs to get passed to requests.get()

        Returns
        -------
        out : int
            Number of stargazers for the repo.
        """
        logger.debug(f'Getting stargazers for "{self._owner}/{self._repo}"')
        request = self.base_req + '/stargazers'
        count = self._total_count(request, **kwargs)
        return count

    def subscribers(self, **kwargs):
        """Get the number of repo subscribers

        Parameters
        ----------
        kwargs : dict
            Optional kwargs to get passed to requests.get()

        Returns
        -------
        out : int
            Number of subscribers for the repo.
        """
        logger.debug(f'Getting subscribers for "{self._owner}/{self._repo}"')
        request = self.base_req + '/subscribers'
        count = self._total_count(request, **kwargs)
        return count

    def views(self, **kwargs):
        """Get the daily github repo views data for the last two weeks.

        Parameters
        ----------
        kwargs : dict
            Optional kwargs to get passed to requests.get()

        Returns
        -------
        out : pd.DataFrame
            Timeseries of daily git views data. Includes columns for "views"
            and "views_unique". Index is a pandas datetime index with just the
            datetime.date part.
        """
        logger.debug(f'Getting views history for "{self._owner}/{self._repo}"')
        return self._traffic(option='views', **kwargs)
