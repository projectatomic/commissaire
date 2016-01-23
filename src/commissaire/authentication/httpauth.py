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


import bcrypt
import etcd
import falcon
import json

from commissaire.authentication import Authenticator
from commissaire.compat.b64 import base64


class _HTTPBasicAuth(Authenticator):
    """
    Basic auth implementation of an authenticator.
    """

    def _decode_basic_auth(self, req):
        """
        Decodes basic auth from the header.

        :param req: Request instance that will be passed through.
        :type req: falcon.Request
        :returns: tuple -- (username, passphrase) or (None, None) if empty.
        :rtype: tuple
        """
        if req.auth is not None:
            if req.auth.lower().startswith('basic '):
                try:
                    return tuple(base64.decodebytes(
                        req.auth[6:].encode('utf-8')).decode().split(':'))
                except base64.binascii.Error:
                    self.logger.info(
                        'Bad base64 data sent. Setting to no user/pass.')
        # Default meaning no user or password
        return (None, None)


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
        except (ValueError, IOError) as ve:
            self.logger.warn(
                'Denying all access due to problem parsing '
                'JSON file: {0}'.format(ve))
            self._data = {}

    def authenticate(self, req, resp):
        """
        Implements the authentication logic.

        :param req: Request instance that will be passed through.
        :type req: falcon.Request
        :param resp: Response instance that will be passed through.
        :type resp: falcon.Response
        :raises: falcon.HTTPForbidden
        """
        user, passwd = self._decode_basic_auth(req)
        if user is not None and passwd is not None:
            if user in self._data.keys():
                if bcrypt.hashpw(
                        passwd.encode('utf-8'),
                        self._data[user]['hash'].encode('utf-8')):
                    return  # Authentication is good

        # Forbid by default
        raise falcon.HTTPForbidden('Forbidden', 'Forbidden')


class HTTPBasicAuthByEtcd(_HTTPBasicAuth):
    """
    HTTP Basic auth backed by Etcd JSON value.
    """

    def __init__(self, ds):
        """
        Creates an instance of the HTTPBasicAuthByEtcd authenticator.

        :param datastore: The Etcd client to use.
        :type datastore: etcd.Client
        :returns: HTTPBasicAuthByEtcd
        """
        self.ds = ds
        self._data = {}
        self.load()

    def load(self):
        """
        Loads the authentication information from etcd.
        """
        try:
            d = self.ds.get(
                '/commissaire/config/httpbasicauthbyuserlist')
            self._data = json.loads(d.value)
            self.logger.info('Loaded authentication data from Etcd.')
            # TODO: Watch endpoint and reload on changes
        except etcd.EtcdKeyNotFound as eknf:
            self.logger.warn(
                'User configuration not found in Etcd. Raising...')
            self._data = {}
            raise eknf
        except ValueError as ve:
            self.logger.warn(
                'User configuration in Etcd is not valid JSON. Raising...')
            raise ve

    def authenticate(self, req, resp):
        """
        Implements the authentication logic.

        :param req: Request instance that will be passed through.
        :type req: falcon.Request
        :param resp: Response instance that will be passed through.
        :type resp: falcon.Response
        :raises: falcon.HTTPForbidden
        """
        user, passwd = self._decode_basic_auth(req)
        if user is not None and passwd is not None:
            if user in self._data.keys():
                if bcrypt.hashpw(
                        passwd.encode('utf-8'),
                        self._data[user]['hash'].encode('utf-8')):
                    return  # Authentication is good

        # Forbid by default
        raise falcon.HTTPForbidden('Forbidden', 'Forbidden')
