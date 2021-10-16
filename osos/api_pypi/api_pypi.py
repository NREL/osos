# -*- coding: utf-8 -*-
"""
Interface module for pypi API
"""
import pypistats
import datetime
import numpy as np
import pandas as pd
import logging


logger = logging.getLogger(__name__)


class Pypi:
    """Class to call pypi data and return osos-formatted pypi usage data."""

    @staticmethod
    def get_data(name, include_mirrors=False):
        """Get the dataframe for the last 180 days of download data

        Parameters
        ----------
        name : str
            pypi package name. Note that this should include the prefix for
            nrel packages e.g. reV -> nrel-rev
        include_mirrors : bool
            Flag to include mirror downloads or not

        Returns
        -------
        out : pd.DataFrame
            DataFrame of pypistats data for the last 180 days with:
            "pypi_daily" and "pypi_180_cumulative". Note that the
            180 day cumulative is for the last 180 days from today's actual
            date, not 180 days from the date in the output row index.
        """

        out = pypistats.overall(name, total=True, format="pandas")
        out = out.iloc[:-1]  # drop totals row, unnecessary

        if not include_mirrors:
            out = out[(out['category'] == 'without_mirrors')]
        else:
            out = out[(out['category'] == 'with_mirrors')]

        out.index = pd.to_datetime(out['date']).dt.date
        out = out.sort_index()
        out = out.drop(['category', 'percent', 'date'], axis=1)
        out = out.rename({'downloads': 'pypi_daily'}, axis=1)

        cumulative = np.cumsum(out['pypi_daily'])
        out['pypi_180_cumulative'] = cumulative
        return out

    @classmethod
    def get_daily_data(cls, name, dates, include_mirrors=False):
        """Get one month of usage data for a pypi package

        Parameters
        ----------
        name : str
            pypi package name. Note that this should include the prefix for
            nrel packages e.g. reV -> nrel-rev
        dates : datetime.date | list
            One or more dates to retrieve data for
        include_mirrors : bool
            Flag to include mirror downloads or not

        Returns
        -------
        out : pd.DataFrame
            DataFrame with sorted index of the "dates" input with:
            "pypi_daily" and "pypi_180_cumulative". Note that the
            180 day cumulative is for the last 180 days from today's actual
            date, not 180 days from the date in the output row index.
        """

        logger.debug(f'Getting daily pypi data for "{name}"')
        logger.debug(f'Including mirrors: {include_mirrors}')

        out = cls.get_data(name, include_mirrors=include_mirrors)

        if isinstance(dates, datetime.date):
            dates = [dates]

        out = pd.DataFrame(index=sorted(dates)).join(out)
        out['pypi_daily'] = out['pypi_daily'].fillna(0)
        out['pypi_180_cumulative'] = out['pypi_180_cumulative'].ffill().bfill()
        out = out.astype(np.int64)
        return out
