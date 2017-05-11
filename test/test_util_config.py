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

import json

import etcd

from unittest import mock

from . import TestCase

import commissaire.storage.etcd

from commissaire.util import config



class Test_ConfigFile(TestCase):
    """
    Tests the config module.
    """

    def test_read_config_file_with_missing_file(self):
        """
        Test the read_config_file function raises when the file is missing.
        """
        with mock.patch('builtins.open', side_effect=IOError):
            self.assertRaises(IOError, config.read_config_file, 'idonotexist')

    def test_read_config_file_with_valid_data(self):
        """
        Test the read_config_file function with valid data.
        """

        # Check handling of storage_handler.
        data = {
            'storage_handlers': [
                {'name': 'commissaire.storage.etcd'},
            ],
        }
        with mock.patch('builtins.open',
                mock.mock_open(read_data=json.dumps(data))) as _open:
            conf = config.read_config_file()
            self.assertIsInstance(conf, dict)
            data['authentication_plugins'] = {}
            self.assertEquals(data, conf)

    def test_read_config_file_with_invalid_data(self):
        """
        Test the read_config_file function within invalid data.
        """

        for data in (12345, 'notadict'):
            with mock.patch('builtins.open',
                    mock.mock_open(read_data=json.dumps(data))) as _open:
                self.assertRaises(TypeError, config.read_config_file)

    def test_read_config_file_with_storge_handler_as_dict(self):
        """
        Verify the read_config_file function turns storage_handlers into a list.
        """
        data = {
            'storage_handlers': {
                'name': 'commissaire.storage.etcd',
            }
        }
        with mock.patch('builtins.open',
                mock.mock_open(read_data=json.dumps(data))) as _open:
            conf = config.read_config_file()
            self.assertIsInstance(conf, dict)
            data['storage_handlers'] = [data['storage_handlers']]
            data['authentication_plugins'] = {}
            self.assertEquals(data, conf)

    def test_read_config_file_with_valid_authentication_plugin(self):
        """
        Verify the read_config_file function parses valid
        authentication_plugin directives.
        """
        plugin_name = 'commissaire_htp.authentication.httpbasicauth'
        data = {
            'authentication_plugins': [{
                'name': plugin_name,
                'users': {},
            }]
        }
        with mock.patch('builtins.open',
                mock.mock_open(read_data=json.dumps(data))) as _open:
            conf = config.read_config_file()
            self.assertIsInstance(conf, dict)
            self.assertTrue(
                plugin_name in conf['authentication_plugins'].keys())
            self.assertEquals(
                data['authentication_plugins'][0]['users'],
                conf['authentication_plugins'][plugin_name]['users'])

    def test_read_config_file_with_invalid_authentication_plugin(self):
        """
        Verify the read_config_file function raises on invalid
        authentication_plugin directives.
        """
        data = {
            'authentication_plugins': [{}]
        }
        with mock.patch('builtins.open',
                mock.mock_open(read_data=json.dumps(data))) as _open:
            self.assertRaises(ValueError, config.read_config_file)

    def test_read_etcd_config_key(self):
        """
        Verify _read_etcd_config_key handles ETCD environment variables.
        """
        environ = {
            'ETCD_MACHINES': 'http://localhost:4001,'
                             'http://etcd.example.com:4001',
            'ETCD_TLSKEY': '/path/to/cert.key',
            'ETCD_TLSPEM': '/path/to/cert.pem',
            'ETCD_CACERT': '/path/to/cacert.pem',
            'ETCD_USERNAME': 'neo',
            'ETCD_PASSWORD': 'theone'
        }

        with mock.patch.dict('os.environ', environ) as environ:
            with mock.patch('etcd.Client') as client_class:
                client = client_class.return_value
                client.read.return_value = '{}'
                config._read_etcd_config_key('test', {})
                client_class.assert_called_with(
                    host=(('localhost', 4001), ('etcd.example.com', 4001)),
                    cert=('/path/to/cert.pem', '/path/to/cert.key'),
                    ca_cert='/path/to/cacert.pem',
                    username='neo',
                    password='theone',
                    protocol='http',
                    allow_reconnect=True)

            # Verify various exceptions are caught.

            with mock.patch('etcd.Client') as client_class:
                client_class.side_effect = etcd.EtcdConnectionFailed
                config._read_etcd_config_key('test', {})

            with mock.patch('etcd.Client') as client_class:
                client = client_class.return_value
                client.get.side_effect = etcd.EtcdKeyNotFound
                config._read_etcd_config_key('test', {})
                client.get.assert_called_once_with(mock.ANY)

            with mock.patch('etcd.Client') as client_class:
                client = client_class.return_value
                client.get.return_value = mock.MagicMock()
                # Make json.loads throw a json.JSONDecodeError
                client.get.return_value.value = '{invalid json}'
                config._read_etcd_config_key('test', {})
                client.get.assert_called_once_with(mock.ANY)

            with mock.patch('etcd.Client') as client_class:
                client = client_class.return_value
                client.get.return_value = mock.MagicMock()
                # Make dict.update throw a TypeError
                client.get.return_value.value = '[1, 2, 3]'
                config._read_etcd_config_key('test', {})
                client.get.assert_called_once_with(mock.ANY)

    def test_import_plugin_with_invalid_module_name(self):
        """
        Verify import_plugin raises on invalid module name
        """
        self.assertRaises(
            config.ConfigurationError,
            config.import_plugin,
            'bogus_module',
            'commissaire.storage',
            commissaire.storage.etcd.PluginClass)

    def test_import_plugin_with_invalid_class(self):
        """
        Verify import_plugin raises on invalid class
        """
        self.assertRaises(
            config.ConfigurationError,
            config.import_plugin,
            'etcd',
            'commissaire.storage',
            int)

    def test_import_plugin_with_builtin_module_name(self):
        """
        Verify import_plugin with built-in module name
        """
        config.import_plugin(
            'etcd',
            'commissaire.storage',
            commissaire.storage.etcd.PluginClass)

    def test_import_plugin_with_external_module_name(self):
        """
        Verify import_plugin with external module name
        """
        config.import_plugin(
            'commissaire.storage.etcd',
            'deliberately.bogus.package',
            commissaire.storage.etcd.PluginClass)
