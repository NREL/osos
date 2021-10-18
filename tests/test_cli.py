# -*- coding: utf-8 -*-
"""
Test for osos cli
"""
from click.testing import CliRunner
import pandas as pd
import os
import tempfile
from osos import TEST_DATA_DIR
from osos.cli import main


def test_cli():
    """Test running the cli with input args for a single run."""
    with tempfile.TemporaryDirectory() as td:
        fp = str(td).replace('\\', '/') + '/test.csv'
        runner = CliRunner()
        out = runner.invoke(main, f"-go NREL -gr reV -pn nrel-rev -f {fp}")
        assert out.exit_code == 0
        assert os.path.exists(fp)


def test_cli_config():
    """Test running the cli with a config input for multiple rex runs."""
    source = pd.read_csv(os.path.join(TEST_DATA_DIR, 'test_config.csv'),
                         index_col=0)
    with tempfile.TemporaryDirectory() as td:
        fpath_out1 = str(td).replace('\\', '/') + '/osos_rev.csv'
        fpath_out2 = str(td).replace('\\', '/') + '/osos_rex.csv'
        config = str(td).replace('\\', '/') + '/test_config.csv'
        source.at['rev', 'fpath_out'] = fpath_out1
        source.at['rex', 'fpath_out'] = fpath_out2
        source.to_csv(config)

        runner = CliRunner()
        out = runner.invoke(main, f"-c {config}")
        assert out.exit_code == 0
        assert os.path.exists(fpath_out1)
        assert os.path.exists(fpath_out2)
