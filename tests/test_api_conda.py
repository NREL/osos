# -*- coding: utf-8 -*-
"""
Test for conda API
"""
import pytest
from osos.api_conda.api_conda import Conda


def test_conda():
    """Test a simple conda download parse"""
    out = Conda.get_data('nrel', 'nrel-rev')
    assert isinstance(out, int)
    assert out >= 362


def test_conda_bad():
    """Test a failed conda parse"""
    with pytest.warns(UserWarning):
        out = Conda.get_data('nrel', 'nrel-asdfasdf')

    assert isinstance(out, int)
    assert out == 0
