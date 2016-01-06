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

import falcon

from commissaire.authentication import Authenticator
from commissaire.compat.b64 import base64


class _HTTPAuth(Authenticator):

    def _decode_basic_auth(self, req):
        if req.auth is not None:
            if req.auth.lower().startswith('basic '):
                return base64.decodebytes(
                    req.auth[6:].encode('utf-8')).decode().split(':')
        # Default meaning no user or password
        return (None, None)


class HTTPAuthByFile(_HTTPAuth):
    """
    Not a secure method! Used for testing and development.
    """

    import yaml
    import bcrypt

    def __init__(self, filename):
        self.filename = filename
        self._data = {}
        self.load()

    def load(self):
        with open(self.filename, 'r') as afile:
            self._data = self.yaml.safe_load(afile)

    def authenticate(self, req, resp):
        user, passwd = self._decode_basic_auth(req)
        if user is not None and passwd is not None:
            if user in self._data.keys():
                try:
                    if self.bcrypt.hashpw(
                            passwd.encode('utf-8'),
                            self._data[user].encode('utf-8')):
                        return  # Authentication is good
                except ValueError as ve:
                    # TODO: the file format is bad
                    pass

        # Forbid by default
        raise falcon.HTTPForbidden('Forbidden', 'Forbidden')
