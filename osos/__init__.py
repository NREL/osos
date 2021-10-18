# -*- coding: utf-8 -*-
"""
Open Source Ops and Statistics
"""
import os
from osos.osos import Osos
from osos.version import __version__


OSOS_DIR = os.path.dirname(os.path.realpath(__file__))
DATA_DIR = os.path.join(os.path.dirname(OSOS_DIR), 'data')
TEST_DATA_DIR = os.path.join(os.path.dirname(OSOS_DIR), 'tests', 'data')


__author__ = "Grant Buster"
__email__ = "grant.buster@nrel.gov"
