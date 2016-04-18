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
"""
Test cases for the commissaire.script module.
"""

import mock
import falcon
import etcd
import os.path

from . import TestCase
from commissaire import script


class Test_CreateApp(TestCase):
    """
    Tests for the create_app function.
    """

    def test_create_app(self):
        """
        Verify cli_etcd_or_default works with cli input.
        """
        with mock.patch('cherrypy.engine.publish') as _publish:
            _publish.return_value = [[[], etcd.EtcdKeyNotFound]]
            app = script.create_app(
                None,
                'commissaire.authentication.httpauthbyfile',
                {'filepath': os.path.realpath('../conf/users.json')})
            self.assertTrue(isinstance(app, falcon.API))
            self.assertEquals(2, len(app._middleware))


class Test_ParseUri(TestCase):
    """
    Tests the parse_uri function.
    """

    def test_parse_uri(self):
        """
        Verify parse_uri properly parses URIs.
        """
        parsed = script.parse_uri('http://127.0.0.1:2379', 'test')
        self.assertEquals('127.0.0.1', parsed.hostname)
        self.assertEquals(2379, parsed.port)
        self.assertEquals('http', parsed.scheme)

        for x in ('http://127.0.0.1:', 'http://127.0.0.1', 'http://1:a', ''):
            self.assertRaises(Exception, script.parse_uri, x, 'test')
