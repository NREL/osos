# -*- coding: utf-8 -*-
"""
Test for high level osos entry points
"""
import pandas as pd
import os
import tempfile
from pandas.testing import assert_frame_equal
from osos.osos import Osos


def test_osos_update():
    """Test that osos will make a valid file, save it to disk, and update
    appropriately without losing data."""
    with tempfile.TemporaryDirectory() as td:
        cache_file = os.path.join(td, 'test.csv')
        osos = Osos('NREL', 'reV', 'nrel-rev')
        truth = osos.make_table()
        truth.iloc[0:3].to_csv(cache_file)
        with open(cache_file) as f:
            assert len(f.readlines()) == 4
        test = osos.update(cache_file)
        assert_frame_equal(truth, test)
        test = pd.read_csv(cache_file, index_col=0)
        test.index = pd.to_datetime(test.index.values).date
        assert_frame_equal(truth, test)
