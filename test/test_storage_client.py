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
Tests for the commissaire.storage.storage module.
"""

import logging
import json

from unittest import mock

from . import TestCase

from commissaire.bus import BusMixin, RemoteProcedureCallError
from commissaire.models import Host, Hosts, ValidationError
from commissaire.storage.client import StorageClient

#: Message ID
ID = '123'
#: Minimal host dictionary
MINI_HOST_DICT = {
    'address': '127.0.0.1'
}
#: Minimal host instance
MINI_HOST = Host.new(**MINI_HOST_DICT)
#: Full host dictionary
FULL_HOST_DICT = {
    'address': '127.0.0.1',
    'status': 'groovy',
    'os': 'amiga',
    'cpus': 1,
    'memory': 32768,
    'space': 0,
    'last_check': '',
    'source': ''
}
#: Full host instance
FULL_HOST = Host.new(**FULL_HOST_DICT)


class TestCommissaireStorageClient(TestCase):
    """
    Tests for the StorageClient class.
    """

    def test_get(self):
        """
        Verify StorageClient.get with a valid model.
        """
        storage = StorageClient(mock.MagicMock())
        storage.bus_mixin.logger = mock.MagicMock()
        storage.bus_mixin.request.return_value = {
            'jsonrpc': '2.0',
            'id': ID,
            'result': FULL_HOST_DICT
        }
        model = storage.get(MINI_HOST)
        storage.bus_mixin.request.assert_called_once_with(
            'storage.get', params={
                'model_type_name': MINI_HOST.__class__.__name__,
                'model_json_data': MINI_HOST.to_dict()
            }
        )
        self.assertIsInstance(model, Host)
        self.assertEqual(model.to_dict_safe(), FULL_HOST_DICT)

    def test_get_rpc_error(self):
        """
        Verify StorageClient.get re-raises RemoteProcedureCallError.
        """
        storage = StorageClient(mock.MagicMock())
        storage.bus_mixin.logger = mock.MagicMock()
        storage.bus_mixin.request.side_effect = RemoteProcedureCallError('test')
        self.assertRaises(RemoteProcedureCallError, storage.get, MINI_HOST)
        storage.bus_mixin.request.assert_called_once_with(
            'storage.get', params={
                'model_type_name': MINI_HOST.__class__.__name__,
                'model_json_data': MINI_HOST.to_dict()
            }
        )

    def test_save(self):
        """
        Verify StorageClient.save with a valid model.
        """
        storage = StorageClient(mock.MagicMock())
        storage.bus_mixin.logger = mock.MagicMock()
        storage.bus_mixin.request.return_value = {
            'jsonrpc': '2.0',
            'id': ID,
            'result': FULL_HOST_DICT
        }
        model = storage.save(FULL_HOST)
        storage.bus_mixin.request.assert_called_once_with(
            'storage.save', params={
                'model_type_name': FULL_HOST.__class__.__name__,
                'model_json_data': FULL_HOST.to_dict()
            }
        )
        self.assertIsInstance(model, Host)
        self.assertEqual(model.to_dict_safe(), FULL_HOST_DICT)

    def test_save_rpc_error(self):
        """
        Verify StorageClient.save re-raises RemoteProcedureCallError.
        """
        storage = StorageClient(mock.MagicMock())
        storage.bus_mixin.logger = mock.MagicMock()
        storage.bus_mixin.request.side_effect = RemoteProcedureCallError('test')
        self.assertRaises(RemoteProcedureCallError, storage.save, FULL_HOST)
        storage.bus_mixin.request.assert_called_once_with(
            'storage.save', params={
                'model_type_name': FULL_HOST.__class__.__name__,
                'model_json_data': FULL_HOST.to_dict()
            }
        )

    def test_save_invalid(self):
        """
        Verify StorageClient.save rejects an invalid model.
        """
        storage = StorageClient(mock.MagicMock())
        storage.bus_mixin.logger = mock.MagicMock()
        storage.bus_mixin.request.side_effect = ValidationError('test')
        bad_host = Host.new(**FULL_HOST_DICT)
        bad_host.address = None
        self.assertRaises(ValidationError, storage.save, bad_host)
        storage.bus_mixin.request.assert_not_called()

    def test_delete(self):
        """
        Verify StorageClient.delete with a valid model.
        """
        storage = StorageClient(mock.MagicMock())
        storage.bus_mixin.logger = mock.MagicMock()
        storage.delete(MINI_HOST)
        storage.bus_mixin.request.assert_called_once_with(
            'storage.delete', params={
                'model_type_name': MINI_HOST.__class__.__name__,
                'model_json_data': MINI_HOST.to_dict()
            }
        )

    def test_delete_rpc_error(self):
        """
        Verify StorageClient.delete re-raises RemoteProcedureCallError.
        """
        storage = StorageClient(mock.MagicMock())
        storage.bus_mixin.logger = mock.MagicMock()
        storage.bus_mixin.request.side_effect = RemoteProcedureCallError('test')
        self.assertRaises(RemoteProcedureCallError, storage.delete, MINI_HOST)
        storage.bus_mixin.request.assert_called_once_with(
            'storage.delete', params={
                'model_type_name': MINI_HOST.__class__.__name__,
                'model_json_data': MINI_HOST.to_dict()
            }
        )

    def test_list(self):
        """
        Verify StorageClient.list returns valid models.
        """
        storage = StorageClient(mock.MagicMock())
        storage.bus_mixin.logger = mock.MagicMock()
        storage.bus_mixin.request.return_value = {
            'jsonrpc': '2.0',
            'id': ID,
            'result': [FULL_HOST_DICT]
        }
        model = storage.list(Hosts)
        storage.bus_mixin.request.assert_called_once_with(
            'storage.list', params={
                'model_type_name': 'Hosts'
            }
        )
        self.assertIsInstance(model, Hosts)
        self.assertEqual(len(model.hosts), 1)
        self.assertIsInstance(model.hosts[0], Host)
        self.assertEqual(model.hosts[0].to_dict_safe(), FULL_HOST_DICT)

    def test_list_rpc_error(self):
        """
        Verify StorageClient.list re-raises RemoteProcedureCallError.
        """
        storage = StorageClient(mock.MagicMock())
        storage.bus_mixin.logger = mock.MagicMock()
        storage.bus_mixin.request.side_effect = RemoteProcedureCallError('test')
        self.assertRaises(RemoteProcedureCallError, storage.list, Hosts)
        storage.bus_mixin.request.assert_called_once_with(
            'storage.list', params={
                'model_type_name': 'Hosts'
            }
        )

    def test_list_invalid(self):
        """
        Verify StorageClient.list rejects an invalid list element.
        """
        storage = StorageClient(mock.MagicMock())
        storage.bus_mixin.logger = mock.MagicMock()
        storage.bus_mixin.request.return_value = {
            'jsonrpc': '2.0',
            'id': ID,
            'result': [{'address': None}]
        }
        self.assertRaises(ValidationError, storage.list, Hosts)
        storage.bus_mixin.request.assert_called_once_with(
            'storage.list', params={
                'model_type_name': 'Hosts'
            }
        )
