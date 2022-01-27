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

OSOS retrieves timeseries data and summary statistics on the usage and activity of open source repositories. 

Note that github usage data (clones and views) are only available for repositories that you have push permissions to, and they are only available for the last two weeks. Also note that OSOS needs a github API token stored in the system environment variable ``GITHUB_TOKEN`` or the github secret ``GIT_API_TOKEN`` to pull data from github. 

See the `OSOS CLI documentation <https://nrel.github.io/osos/_cli/osos.html#osos>`_ for details on how to run OSOS from the command line. If you want to set up a chron job to regularly pull and save usage statistics from your projects, see the instructions on how to fork OSOS below. 

Installing OSOS
===============

OSOS can be installed via pip: ``pip install nrel-osos`` or by cloning the repo and doing a developer install: ``pip install -e .`` from within the repo directory.

Getting Started
===============

After installing, try calling the command line help page with ``osos --help`` to see the run options. There are currently two CLI commands: one for running the osos utility (``osos run --help``) and one for plotting the osos data files (``osos plot --help``).

You can also run osos from python directly, which will give you more detailed information on a given repository. Try `launching binder <https://mybinder.org/v2/gh/NREL/osos/HEAD>`_ and navigating to `the osos example notebook <https://github.com/NREL/osos/blob/main/examples/running_osos.ipynb>`_. You will need your own github api token to run the notebook.

Finally, you can run OSOS from a config file for several repositories at once. We have a chron job set up using github actions to run a job every Monday morning. If you want to set up your own chron job you will have to fork and configure the OSOS repository (see details in the section below). Data produced from the github action is saved in the `osos data directory <https://github.com/NREL/osos/tree/main/data>`_ and plots are saved to the `osos plots directory <https://github.com/NREL/osos/tree/main/plots>`_. For example, here is the 180-day cumulative pypi downloads for `reV <https://github.com/NREL/rev>`_, one of our open source projects:

.. image:: https://github.com/NREL/osos/blob/main/plots/rev_pypi_180_cumulative.png
  :width: 400

*note that the PyPI 180 day download metric is updated every week by OSOS, so decreases in the metric are due to a moving 180-day window

Forking OSOS
============

If you fork the repo, you can schedule a github action workflow to automatically pull usage statistics for projects every Monday morning. To fork OSOS, follow these steps:

#. Go to the `OSOS github page <https://github.com/NREL/osos>`_ and click "Fork" in the top right
#. Fork the repository into a personal github account or organization
#. Create a `github personal access token <https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token>`_
#. Add the access token as a `secret <https://docs.github.com/en/actions/security-guides/encrypted-secrets>`_ to your forked repository with the name ``GIT_API_TOKEN``
#. Update your `OSOS config file <https://github.com/NREL/osos/blob/main/osos_config.csv>`_ with the repositories you want to track
#. Set up your `Update OSOS Data <https://github.com/NREL/osos/blob/main/.github/workflows/update_osos_data.yml>`_ github action and try running it in the `github actions interface <https://github.com/NREL/osos/actions/workflows/update_osos_data.yml>`_
#. Check back when your update job is scheduled to run and make sure it actually ran successfully
#. Let us know how it goes and feel free to contribute improvements or bug fixes!
