# -*- coding: utf-8 -*-
"""
Open Source Ops and Statistics
"""
import os
from osos.osos import Osos
from osos.api_pypi import Pypi
from osos.api_conda import Conda
from osos.api_github import Github
from osos.version import __version__


OSOS_DIR = os.path.dirname(os.path.realpath(__file__))
DATA_DIR = os.path.join(os.path.dirname(OSOS_DIR), 'data')
PLOT_DIR = os.path.join(os.path.dirname(OSOS_DIR), 'plots')
TEST_DATA_DIR = os.path.join(os.path.dirname(OSOS_DIR), 'tests', 'data')


__author__ = "Grant Buster"
__email__ = "grant.buster@nrel.gov"
