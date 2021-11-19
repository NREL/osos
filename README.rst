*************************************
Open Source Ops and Statistics (OSOS)
*************************************

.. image:: https://github.com/NREL/osos/workflows/Documentation/badge.svg
    :target: https://nrel.github.io/osos/

.. image:: https://github.com/NREL/osos/workflows/pytests/badge.svg
    :target: https://github.com/NREL/osos/actions?query=workflow%3A%22pytests%22

.. image:: https://github.com/NREL/osos/workflows/Lint%20Code%20Base/badge.svg
    :target: https://github.com/NREL/osos/actions?query=workflow%3A%22Lint+Code+Base%22

.. image:: https://img.shields.io/pypi/pyversions/NREL-osos.svg
    :target: https://pypi.org/project/NREL-osos/

.. image:: https://badge.fury.io/py/NREL-osos.svg
    :target: https://badge.fury.io/py/NREL-osos

.. image:: https://img.shields.io/github/license/NREL/osos
    :target: https://github.com/NREL/osos/blob/main/LICENSE

.. image:: https://codecov.io/gh/NREL/osos/branch/main/graph/badge.svg?token=0J5GVFEGYZ
   :target: https://codecov.io/gh/NREL/osos

.. image:: https://mybinder.org/badge_logo.svg
    :target: https://mybinder.org/v2/gh/nrel/osos/HEAD

This package helps track usage and contribution data for open source software.
OSOS can be used to retrieve timeseries data on the usage and activity of open
source repositories. Note that github usage data (clones and views) are only
available for repositories that you have push permissions to, and they are only
available for the last two weeks. Also note that OSOS needs a github API token
stored in the environment variable ``GITHUB_TOKEN`` to pull data from github.
See the `OSOS CLI documentation <https://nrel.github.io/osos/_cli/osos.html#osos>`_
for details on how to run OSOS from the command line.


Installing OSOS
===============

OSOS can be installed via pip: ``pip install nrel-osos`` or by cloning the repo 
and doing a developer install: ``pip install -e .`` from within the repo directory.

Getting Started
===============

After installing, try calling the command line help page with ``osos --help`` to 
see the run options. There are currently two CLI commands: one for running the 
osos utility (``osos run --help``) and one for plotting the osos data files 
(``osos plot --help``).

You can also run osos from python directly. Try 
`launching binder <https://mybinder.org/v2/gh/NREL/osos/HEAD>`_ 
and navigating to `the osos example notebook <https://github.com/NREL/osos/blob/main/examples/running_osos.ipynb>`_. 
You will need your own github api token to run the notebook.

How To Use OSOS
===============

OSOS is a general utility for downloading usage statistics from github, pypi, and conda. 
Feel free to fork the repo to track your own projects. We have a scheduled github action 
workflow set up to automatically pull usage statistics for our projects every Monday morning. 
The data is saved in the `osos data directory <https://github.com/NREL/osos/tree/main/data>`_ 
and plots are saved to the `osos plots directory <https://github.com/NREL/osos/tree/main/plots>`_. 
For example, here is the 180-day cumulative pypi downloads for `reV <https://github.com/NREL/rev>`_, 
one of our open source projects:

.. image:: https://github.com/NREL/osos/blob/main/plots/rev_pypi_180_cumulative.png
  :width: 400
