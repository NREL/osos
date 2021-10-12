# -*- coding: utf-8 -*-
"""
Test for pypi API
"""
from osos.api_pypi.api_pypi import Pypinfo


def test_pypinfo():
    """Test a simple pypinfo request"""
    out = Pypinfo.get_monthly_data('nrel-rev', 1)
    assert isinstance(out, dict)
    assert 'total' in out
    assert isinstance(out['total'], int)
