# -*- coding: utf-8 -*-
"""
Test for pypi API
"""
from datetime import datetime
import pandas as pd
import numpy as np
import json
from osos.api_pypi.api_pypi import Pypinfo


def test_pypinfo():
    """Test a simple pypinfo request"""
    out = Pypinfo.get_monthly_data('nrel-rev', 1)
    i = int(str(datetime.now().year) + '01')

    assert isinstance(out, pd.DataFrame)
    assert 'pypi_total' in out
    assert isinstance(out.at[i, 'pypi_total'], np.integer)

    assert 'pypi_country_stats' in out
    cstats = out.at[i, 'pypi_country_stats']
    assert isinstance(cstats, str)
    cstats = json.loads(cstats)
    assert 'US' in cstats
    assert isinstance(cstats['US'], int)
