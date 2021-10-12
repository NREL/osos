# -*- coding: utf-8 -*-
"""
Interface module for pypi API
"""
from datetime import datetime
import os
import json
import shlex
import subprocess


class Pypinfo:
    """Class to call pypinfo cli and return osos-formatted pypi usage data."""

    @staticmethod
    def preflight(auth=None):
        """Check that the authentication file exists for the
        pypinfo-google-big-query linkage

        Parameters
        ----------
        auth : str | dict | None
            pypinfo-google-big-query authentication filepath (.json) or
            extracted dictionary. Default is None to use the environment
            variable "GOOGLE_APPLICATION_CREDENTIALS".
        """

        if isinstance(auth, str):
            msg = ('Could not find pypinfo authentication filepath that '
                   'was input: "{}"'.format(auth))
            assert os.path.exists(auth), msg

        elif isinstance(auth, dict):
            required = ('private_key', 'private_key_id')
            for req in required:
                msg = 'Could not find "{}" in auth dict input'.format(req)
                assert 'private_key' in auth, msg

        else:
            credentials = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', None)
            msg = ('Could not find environment variable '
                   '"GOOGLE_APPLICATION_CREDENTIALS"')
            assert credentials is not None, msg
            msg = ('Could not find environment variable '
                   '"GOOGLE_APPLICATION_CREDENTIALS" '
                   'filepath: "{}"'.format(credentials))
            assert os.path.exists(credentials), msg

    @staticmethod
    def cli(cmd):
        """Run the pypinfo cli

        Parameters
        ----------
        cmd : str
            cli call starting with "pypinfo". Note that -j flag will be used
            for json output. --all should not be included (do not include
            mirror downloads). For example for the month of september:
            pypinfo --json --start-date 2021-09 --end-date 2021-09 nrel-rev

        Returns
        -------
        out : dict
            output dictionary from json-formatted pypinfo output
        """

        msg = 'CLI call must be a pypinfo call: "{}"'.format(cmd)
        assert cmd.startswith('pypinfo '), msg

        if '-j' not in cmd and '--json' not in cmd:
            cmd = cmd.replace('pypinfo ', 'pypinfo --json ')

        cmd = shlex.split(cmd)

        # use subprocess to submit command and get piped o/e
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        stderr = stderr.decode('ascii').rstrip()

        if process.returncode != 0:
            raise OSError('Pypinfo cli failed with return code {} '
                          'and stderr:\n{}'
                          .format(process.returncode, stderr))

        out = stdout.decode('ascii').rstrip()
        out = json.loads(out)

        return out

    @classmethod
    def get_monthly_data(cls, name, month, year=None, auth=None):
        """Get one month of usage data for a pypi package

        Parameters
        ----------
        name : str
            pypi package name. Note that this should include the prefix for
            nrel packages e.g. reV -> nrel-rev
        month : int | str
            Month integer to retrieve data for.
        year : int | str | None
            Year integer to retrieve data for. Default is None which uses
            current year
        auth : str | dict | None
            pypinfo-google-big-query authentication filepath (.json) or
            extracted dictionary. Default is None to use the environment
            variable "GOOGLE_APPLICATION_CREDENTIALS".

        Returns
        -------
        out : dict
            Monthly downloads (values) broken down by country code (keys)
            including "total"
        """

        cls.preflight(auth=auth)
        month = str(month).zfill(2)
        year = datetime.now().year if year is None else year
        auth_arg = '' if auth is None else f'--auth {auth} '
        cmd = (f'pypinfo --json {auth_arg}'
               f'--start-date {year}-{month} '
               f'--end-date {year}-{month} '
               f'{name} country')
        cli_out = cls.cli(cmd)
        out = {row['country']: row['download_count']
               for row in cli_out['rows']}
        out['total'] = sum(out.values())
        return out


if __name__ == '__main__':
    out = Pypinfo.get_monthly_data('nrel-rev', 8)
    from pprint import pprint
    pprint(out)
