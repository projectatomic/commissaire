# Copyright (C) 2016  Red Hat, Inc
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import json

from commissaire.compat import exception
from commissaire.authentication.httpauth import _HTTPBasicAuth


class HTTPBasicAuthByFile(_HTTPBasicAuth):
    """
    HTTP Basic auth backed by a JSON file.
    """

    def __init__(self, filepath):
        """
        Creates an instance of the HTTPBasicAuthByFile authenticator.

        :param filepath: The file path to the JSON file backing authentication.
        :type filepath: string
        :returns: HTTPBasicAuthByFile
        """
        self.filepath = filepath
        self._data = {}
        self.load()

    def load(self):
        """
        Loads the authentication information from the JSON file.
        """
        try:
            with open(self.filepath, 'r') as afile:
                self._data = json.load(afile)
                self.logger.info('Loaded authentication data from local file.')
        except:
            _, ve, _ = exception.raise_if_not((ValueError, IOError))
            self.logger.warn(
                'Denying all access due to problem parsing '
                'JSON file: {0}'.format(ve))
            self._data = {}


AuthenticationPlugin = HTTPBasicAuthByFile
