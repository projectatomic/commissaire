# Copyright (C) 2016  Red Hat, Inc
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import cherrypy
import json

from commissaire.authentication.httpauth import _HTTPBasicAuth


class HTTPBasicAuthByEtcd(_HTTPBasicAuth):
    """
    HTTP Basic auth backed by Etcd JSON value.
    """

    def __init__(self):
        """
        Creates an instance of the HTTPBasicAuthByEtcd authenticator.

        :returns: HTTPBasicAuthByEtcd
        """
        self._data = {}
        self.load()

    def load(self):
        """
        Loads the authentication information from etcd.
        """
        d, error = cherrypy.engine.publish(
            'store-get', '/commissaire/config/httpbasicauthbyuserlist')[0]

        if error:
            if type(error) == ValueError:
                self.logger.warn(
                    'User configuration in Etcd is not valid JSON. Raising...')
            else:
                self.logger.warn(
                    'User configuration not found in Etcd. Raising...')
            self._data = {}
            raise error

        self._data = json.loads(d.value)
        self.logger.info('Loaded authentication data from Etcd.')


AuthenticationPlugin = HTTPBasicAuthByEtcd
