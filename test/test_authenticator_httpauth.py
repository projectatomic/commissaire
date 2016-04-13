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
"""
Test cases for the commissaire.authentication.httpauth module.
"""

import etcd
import falcon
import mock

from . import TestCase, get_fixture_file_path
from falcon.testing.helpers import create_environ
from commissaire.authentication import httpauth
from commissaire.authentication import httpauthbyetcd
from commissaire.authentication import httpauthbyfile


class Test_HTTPBasicAuth(TestCase):
    """
    Tests for the _HTTPBasicAuth class.
    """

    def setUp(self):
        """
        Sets up a fresh instance of the class before each run.
        """
        self.http_basic_auth = httpauth._HTTPBasicAuth()

    def test_decode_basic_auth_with_header(self):
        """
        Verify decoding returns a filled tuple given the proper header no matter the case of basic.
        """
        basic = list('basic')
        for x in range(0, 5):
            headers = {'Authorization': '{0} YTph'.format(''.join(basic))}
            req = falcon.Request(
                create_environ(headers=headers))
            self.assertEquals(
                ('a', 'a'),
                self.http_basic_auth._decode_basic_auth(req))
            # Update the next letter to be capitalized
            basic[x] = basic[x].capitalize()

    def test_decode_basic_auth_with_bad_data_in_header(self):
        """
        Verify decoding returns no user with bad base64 data in the header.
        """
        req = falcon.Request(
            create_environ(headers={'Authorization': 'basic BADDATA'}))
        self.assertEquals(
            (None, None),
            self.http_basic_auth._decode_basic_auth(req))

    def test_decode_basic_auth_with_no_header(self):
        """
        Verify returns no user with no authorization header.
        """
        req = falcon.Request(create_environ(headers={}))
        self.assertEquals(
            (None, None),
            self.http_basic_auth._decode_basic_auth(req))


class TestHTTPBasicAuthByFile(TestCase):
    """
    Tests for the HTTPBasicAuthByFile class.
    """

    def setUp(self):
        """
        Sets up a fresh instance of the class before each run.
        """
        self.user_config = get_fixture_file_path('conf/users.json')
        self.http_basic_auth_by_file = httpauthbyfile.HTTPBasicAuthByFile(
            self.user_config)

    def test_load_with_non_parsable_file(self):
        """
        Verify load gracefully loads no users when the JSON file does not exist.
        """
        for bad_file in ('', get_fixture_file_path('test/bad.json')):
            self.http_basic_auth_by_file.filepath = bad_file
            self.http_basic_auth_by_file.load()
            self.assertEquals(
                {},
                self.http_basic_auth_by_file._data
            )

    def test_authenticate_with_valid_user(self):
        """
        Verify authenticate works with a proper JSON file, Authorization header, and a matching user.
        """
        self.http_basic_auth_by_file = httpauthbyfile.HTTPBasicAuthByFile(
            self.user_config)
        req = falcon.Request(
            create_environ(headers={'Authorization': 'basic YTph'}))
        resp = falcon.Response()
        self.assertEquals(
            None,
            self.http_basic_auth_by_file.authenticate(req, resp))

    def test_authenticate_with_invalid_user(self):
        """
        Verify authenticate denies with a proper JSON file, Authorization header, and no matching user.
        """
        self.http_basic_auth_by_file = httpauthbyfile.HTTPBasicAuthByFile(
            self.user_config)
        req = falcon.Request(
            create_environ(headers={'Authorization': 'basic Yjpi'}))
        resp = falcon.Response()
        self.assertRaises(
            falcon.HTTPForbidden,
            self.http_basic_auth_by_file.authenticate,
            req, resp)

    def test_authenticate_with_invalid_password(self):
        """
        Verify authenticate denies with a proper JSON file, Authorization header, and the wrong password.
        """
        self.http_basic_auth_by_file = httpauthbyfile.HTTPBasicAuthByFile(
            self.user_config)
        req = falcon.Request(
            create_environ(headers={'Authorization': 'basic YTpiCg=='}))
        resp = falcon.Response()
        self.assertRaises(
            falcon.HTTPForbidden,
            self.http_basic_auth_by_file.authenticate,
            req, resp)


class TestHTTPBasicAuthByEtcd(TestCase):
    """
    Tests for the HTTPBasicAuthByEtcd class.
    """

    def setUp(self):
        """
        Sets up a fresh instance of the class before each run.
        """
        self.user_config = get_fixture_file_path('conf/users.json')

    def test_load_with_non_key(self):
        """
        Verify load raises when the key does not exist in etcd.
        """
        with mock.patch('cherrypy.engine.publish') as _publish:
            _publish.return_value = [[[], etcd.EtcdKeyNotFound()]]

            self.assertRaises(
                etcd.EtcdKeyNotFound,
                httpauthbyetcd.HTTPBasicAuthByEtcd)

    def test_load_with_bad_data(self):
        """
        Verify load raises when the data in Etcd is bad.
        """
        with mock.patch('cherrypy.engine.publish') as _publish:
            _publish.return_value = [[[], ValueError()]]

            self.assertRaises(
                ValueError,
                httpauthbyetcd.HTTPBasicAuthByEtcd)

    def test_authenticate_with_valid_user(self):
        """
        Verify authenticate works with a proper JSON in Etcd, Authorization header, and a matching user.
        """
        with mock.patch('cherrypy.engine.publish') as _publish:
            # Mock the return of the Etcd get result
            return_value = mock.MagicMock(etcd.EtcdResult)
            with open(self.user_config, 'r') as users_file:
                return_value.value = users_file.read()

            _publish.return_value = [[return_value, None]]

            # Reload with the data from the mock'd Etcd
            http_basic_auth_by_etcd = httpauthbyetcd.HTTPBasicAuthByEtcd()

            # Test the call
            req = falcon.Request(
                create_environ(headers={'Authorization': 'basic YTph'}))
            resp = falcon.Response()
            self.assertEquals(
                None,
                http_basic_auth_by_etcd.authenticate(req, resp))

    def test_authenticate_with_invalid_user(self):
        """
        Verify authenticate denies with a proper JSON in Etcd, Authorization header, and no matching user.
        """
        with mock.patch('cherrypy.engine.publish') as _publish:
            # Mock the return of the Etcd get result
            return_value = mock.MagicMock(etcd.EtcdResult)
            with open(self.user_config, 'r') as users_file:
                return_value.value = users_file.read()
            _publish.return_value = [[return_value, None]]

            # Reload with the data from the mock'd Etcd
            http_basic_auth_by_etcd = httpauthbyetcd.HTTPBasicAuthByEtcd()

            # Test the call
            req = falcon.Request(
                create_environ(headers={'Authorization': 'basic Yjpi'}))
            resp = falcon.Response()
            self.assertRaises(
                falcon.HTTPForbidden,
                http_basic_auth_by_etcd.authenticate,
                req, resp)

    def test_authenticate_with_invalid_password(self):
        """
        Verify authenticate denies with a proper JSON file, Authorization header, and the wrong password.
        """
        with mock.patch('cherrypy.engine.publish') as _publish:
            return_value = mock.MagicMock(etcd.EtcdResult)
            with open(self.user_config, 'r') as users_file:
                return_value.value = users_file.read()
            _publish.return_value = [[return_value, None]]

            # Reload with the data from the mock'd Etcd
            http_basic_auth_by_etcd = httpauthbyetcd.HTTPBasicAuthByEtcd()

            req = falcon.Request(
                create_environ(headers={'Authorization': 'basic YTpiCg=='}))
            resp = falcon.Response()
            self.assertRaises(
                falcon.HTTPForbidden,
                http_basic_auth_by_etcd.authenticate,
                req, resp)
