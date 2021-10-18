# -*- coding: utf-8 -*-
"""
Interface module for conda API

Note that at this time I haven't figured out how to use the condastats package
for repositories with groups (not just in be base anaconda group) so just
pulling the total download number from the conda website is a simple solution.
"""
import requests
import re
import logging
from warnings import warn


logger = logging.getLogger(__name__)


class Conda:
    """Class to parse download data from conda."""

    @staticmethod
    def get_data(org, name):
        """Get the number of downloads for a conda package.

        Parameters
        ----------
        org : str
            Conda organization name, for example:
            https://anaconda.org/{org}/{name}
        name : str
            Conda package name, for example:
            https://anaconda.org/{org}/{name}

        Returns
        -------
        downloads : int
            Total number of downloads for conda package.
        """

        logger.debug(f'Getting data from conda package "{org}/{name}"')
        request = f'https://anaconda.org/{org}/{name}'
        out = requests.get(request)

        if out.status_code != 200:
            msg = ('Received unexpected status code "{}" for reason "{}".'
                   '\nRequest: {}\nOutput: {}'
                   .format(out.status_code, out.reason, request,
                           out.text))
            logger.error(msg)
            raise IOError(msg)

        # could probably use an html parser but this is easy since we're only
        # looking for one number
        regex = re.search("<span>[0-9]*</span> total downloads", out.text)

        downloads = 0
        if regex is None:
            msg = f'Could not find conda download count for "{request}".'
            logger.warning(msg)
            warn(msg)
        else:
            downloads = regex.group()
            downloads = int(''.join([s for s in downloads if s.isdigit()]))

        return downloads
