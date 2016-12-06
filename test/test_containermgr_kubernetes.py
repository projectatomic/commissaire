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
Tests for the commissaire.containermgr.kubernetes module.
"""

import json

from unittest import mock

from . import TestCase, mock

from commissaire.containermgr import kubernetes
from commissaire.util.config import ConfigurationError


CONTAINER_MGR_CONFIG = {
    'server_url': 'http://127.0.0.1:8080/'
}


class TestKubeContainerManager(TestCase):
    """
    Tests for the commissaire.containermgr.kubernetes module.
    """

    def setUp(self):
        """
        Set up an instance for every test.
        """
        self.instance = kubernetes.KubeContainerManager(CONTAINER_MGR_CONFIG)

    def test_initialization(self):
        """
        Verify using new on a model creates a default instance.
        """

        self.assertEquals('http://127.0.0.1:8080/api/v1', self.instance.base_uri)
        self.assertTrue(self.instance.con)

    def test_initialization_with_bad_config(self):
        """
        Verify using new on a model creates a default instance.
        """
        for config in (
                {},
                {'server_url': 'http://127.0.0.1:8080/', 'certificate_path': '/tmp/'},
                {'server_url': 'http://127.0.0.1:8080/', 'certificate_path': '/tmp/',
                 'certificate_key_path': '/tmp/'}):
            self.assertRaises(
                ConfigurationError,
                kubernetes.KubeContainerManager,
                config)

    def test__get(self):
        """
        Verify _get makes proper HTTP requests.
        """
        self.instance.con = mock.MagicMock()
        self.instance._get('test')
        self.instance.con.get.assert_called_once_with(
            CONTAINER_MGR_CONFIG['server_url'] + 'api/v1/test')

    def test_node_registered(self):
        """
        Verify node_registered makes the proper remote call and returns the proper result.
        """
        for code, result in ((200, True), (404, False)):
            self.instance.con = mock.MagicMock()
            self.instance.con.get.return_value = mock.MagicMock(status_code=code)
            self.assertEquals(result, self.instance.node_registered('test'))
            self.instance.con.get.assert_called_once_with(
                CONTAINER_MGR_CONFIG['server_url'] + 'api/v1/nodes/test')

    def test_get_host_status(self):
        """
        Verify get_host_status makes the proper remote call.
        """
        data = {'data': 'data', 'status': 'status'}
        for raw, result in ((True, 'status'), (False, data)):
            self.instance.con = mock.MagicMock()
            resp = mock.MagicMock(json=mock.MagicMock(return_value=data))
            self.instance.con.get.return_value = resp
            self.instance.con.get().status_code = 200
            self.assertEquals((200, result), self.instance.get_host_status('test', raw))
            self.instance.con.get.assert_called_with(
                CONTAINER_MGR_CONFIG['server_url'] + 'api/v1/nodes/test')

