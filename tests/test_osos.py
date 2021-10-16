# -*- coding: utf-8 -*-
"""
Test for high level osos entry points
"""
import datetime
import numpy as np
import pandas as pd
import os
import tempfile
from pandas.testing import assert_frame_equal
from osos.osos import Osos


def test_osos_table():
    """Test basic format of osos output table"""
    osos = Osos('NREL', 'reV', 'nrel-rev')
    table = osos.make_table()

    for col in ('clones', 'views', 'commits', 'pypi_daily'):
        assert col in table

    for col in ('total_commits', 'issues_closed_count',
                'issues_closed_mean_lifetime', 'pulls_closed_count',
                'pulls_closed_mean_lifetime'):
        assert col in table
        assert table[col].dtype == np.float64
        assert not np.isnan(table[col].values).any()

    assert len(table) == 14
    d0 = datetime.date.today()
    d1 = datetime.date.today() - datetime.timedelta(days=13)
    index = pd.date_range(d1, d0, freq='1D').date
    for d in index:
        assert d in table.index


def test_osos_update():
    """Test that osos will make a valid file, save it to disk, and update
    appropriately without losing data."""
    with tempfile.TemporaryDirectory() as td:
        fpath_out = os.path.join(td, 'test.csv')
        osos = Osos('NREL', 'reV', 'nrel-rev')
        truth = osos.make_table()

        d0 = datetime.date.today() - datetime.timedelta(days=3)
        d1 = datetime.date.today() - datetime.timedelta(days=16)
        index = pd.date_range(d1, d0, freq='1D').date
        truth_mod = truth.copy()
        truth_mod.index = index
        truth_mod['updated_on'] = d0

        truth_mod.to_csv(fpath_out)
        fake_dates = [t for t in truth_mod.index.values
                      if t not in truth.index.values]
        assert len(fake_dates) == 3
        with open(fpath_out) as f:
            assert len(f.readlines()) == 15

        test = osos.update(fpath_out)
        assert all(t in test.index.values for t in truth_mod.index.values)
        assert all(t in test.index.values for t in fake_dates)


def test_osos_new_data():
    """Test that osos will add new data columns properly and not delete any
    deprecated columns."""
    with tempfile.TemporaryDirectory() as td:
        fpath_out = os.path.join(td, 'test.csv')
        osos = Osos('NREL', 'reV', 'nrel-rev')
        truth = osos.make_table()
        truth['random'] = np.random.uniform(0, 1, len(truth))
        truth_drop = truth.drop('pypi_daily', axis=1)

        # this will break if github api spuriously returns a different number
        # of days
        fake_dates = pd.date_range('20180101', '20180114', freq='1D')
        truth_drop.index = fake_dates
        truth_drop.to_csv(fpath_out)

        new = osos.update(fpath_out)
        disk = pd.read_csv(fpath_out, index_col=0)
        disk.index = pd.to_datetime(disk.index.values).date

        cols = [c for c in new.columns if c != 'updated_on']
        assert_frame_equal(new[cols], disk[cols])

        assert all(d in new.index.values for d in fake_dates)
        assert all(d in disk.index.values for d in fake_dates)
        assert all(d in new.index.values for d in truth.index.values)
        assert all(d in disk.index.values for d in truth.index.values)

        mask = pd.to_datetime(new.index).year == 2018
        assert not any(np.isnan(new.loc[mask, 'random']))
        assert all(np.isnan(new.loc[~mask, 'random']))

        assert not any(np.isnan(new.loc[~mask, 'pypi_daily']))
        assert all(np.isnan(new.loc[mask, 'pypi_daily']))
