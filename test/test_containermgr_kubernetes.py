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

from commissaire.containermgr import ContainerManagerError, kubernetes
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

    def test__get_and_delete(self):
        """
        Verify _get and _delete makes proper HTTP requests.
        """
        for method in ('get', 'delete'):
            self.instance.con = mock.MagicMock()
            method_callable = getattr(self.instance, '_' + method)
            method_callable('test')
            assertable_callable = getattr(self.instance.con, method)
            assertable_callable.assert_called_once_with(
                CONTAINER_MGR_CONFIG['server_url'] + 'api/v1/test')

    def test__put_and__post(self):
        """
        Verify _put and _post makes proper HTTP requests.
        """
        expected = {'test': 'test'}
        for method in ('put', 'post'):
            self.instance.con = mock.MagicMock()
            method_callable = getattr(self.instance, '_' + method)
            method_callable('test', expected)
            assertable_callable = getattr(self.instance.con, method)
            assertable_callable.assert_called_once_with(
                CONTAINER_MGR_CONFIG['server_url'] + 'api/v1/test',
                data=json.dumps(expected))

    def test_node_registered(self):
        """
        Verify node_registered makes the proper remote call and returns the proper result.
        """
        self.instance.con = mock.MagicMock()
        self.instance.con.get.return_value = mock.MagicMock(status_code=200)
        self.assertEquals(None, self.instance.node_registered('test'))
        self.instance.con.get.assert_called_once_with(
            CONTAINER_MGR_CONFIG['server_url'] + 'api/v1/nodes/test')

    def test_node_registered_when_node_is_not_registered(self):
        """
        Verify node_registered raises when the node is not registered.
        """
        self.instance.con = mock.MagicMock()
        self.instance.con.get.return_value = mock.MagicMock(status_code=404)
        self.assertRaises(
            ContainerManagerError,
            self.instance.node_registered,
            'test')
        self.instance.con.get.assert_called_once_with(
            CONTAINER_MGR_CONFIG['server_url'] + 'api/v1/nodes/test')

    def test_register_node(self):
        """
        Verify register_node makes the proper remote call and returns the proper result.
        """
        self.instance.con = mock.MagicMock()
        self.instance.con.post.return_value = mock.MagicMock(
            status_code=201, text='')
        self.assertEquals(None, self.instance.register_node('test'))
        self.instance.con.post.assert_called_once_with(
            CONTAINER_MGR_CONFIG['server_url'] + 'api/v1/nodes',
            data=mock.ANY)

    def test_register_node_when_registration_fails(self):
        """
        Verify register_node raises on registration failure.
        """
        self.instance.con = mock.MagicMock()
        self.instance.con.post.return_value = mock.MagicMock(
            status_code=500, text='')
        self.assertRaises(
            ContainerManagerError,
            self.instance.register_node,
            'test')
        self.instance.con.post.assert_called_once_with(
            CONTAINER_MGR_CONFIG['server_url'] + 'api/v1/nodes',
            data=mock.ANY)

    def test_remove_node(self):
        """
        Verify remove_node makes the proper remote call and returns the proper result.
        """
        self.instance.con = mock.MagicMock()
        self.instance.con.delete.return_value = mock.MagicMock(
            status_code=200)
        self.assertEquals(None, self.instance.remove_node('test'))
        self.instance.con.delete.assert_called_once_with(
            CONTAINER_MGR_CONFIG['server_url'] + 'api/v1/nodes/test')

    def test_remove_node_when_removal_fails(self):
        """
        Verify remove_node raises when removal fails.
        """
        self.instance.con = mock.MagicMock()
        self.instance.con.delete.return_value = mock.MagicMock(
            status_code=404)
        self.assertRaises(
            ContainerManagerError,
            self.instance.remove_node,
            'test')
        self.instance.con.delete.assert_called_once_with(
            CONTAINER_MGR_CONFIG['server_url'] + 'api/v1/nodes/test')

    def test_get_node_status(self):
        """
        Verify get_node_status makes the proper remote call.
        """
        data = {'data': 'data', 'status': 'status'}
        for raw, result in ((True, 'status'), (False, data)):
            self.instance.con = mock.MagicMock()
            resp = mock.MagicMock(json=mock.MagicMock(return_value=data))
            self.instance.con.get.return_value = resp
            self.instance.con.get().status_code = 200
            self.assertEquals(
                result, self.instance.get_node_status('test', raw))
            self.instance.con.get.assert_called_with(
                CONTAINER_MGR_CONFIG['server_url'] + 'api/v1/nodes/test')

    def test_get_node_status_on_failure(self):
        """
        Verify get_node_status raises when getting a status fails.
        """
        self.instance.con = mock.MagicMock()
        resp = mock.MagicMock(json=mock.MagicMock(return_value=''))
        self.instance.con.get.return_value = resp
        self.instance.con.get().status_code = 500
        self.assertRaises(
            ContainerManagerError,
            self.instance.get_node_status,
            'test')
        self.instance.con.get.assert_called_with(
            CONTAINER_MGR_CONFIG['server_url'] + 'api/v1/nodes/test')


    def test__fix_part_with_valid_part(self):
        """
        Verify that when a valid part is given it is returned without modification.
        """
        expected = '/test'
        self.assertEquals(
            expected,
            self.instance._fix_part(expected))

    def test__fix_part_with_invalid_part(self):
        """
        Verify that when an invalid part it is fixed.
        """
        self.assertEquals(
            '/test',
            self.instance._fix_part('test'))
