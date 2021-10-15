# -*- coding: utf-8 -*-
"""
Test for pypi API
"""
import datetime
import pandas as pd
import numpy as np
from osos.api_pypi.api_pypi import Pypi


def test_pypi():
    """Test a simple pypi request"""
    d0 = datetime.date.today()
    dates = []
    for nd in range(1, 14):
        dates.append(d0 - datetime.timedelta(days=nd))

    out = Pypi.get_daily_data('nrel-rev', dates)

    assert len(out) == len(dates)

    assert isinstance(out, pd.DataFrame)
    assert 'pypi_daily' in out
    assert out['pypi_daily'].dtype == np.int64

    assert isinstance(out, pd.DataFrame)
    assert 'pypi_180_cumulative' in out
    assert out['pypi_180_cumulative'].dtype == np.int64
