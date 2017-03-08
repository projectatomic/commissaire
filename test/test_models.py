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
Tests for the commissaire.models module.
"""

import json

from unittest import mock

from . import TestCase

from commissaire import constants as C
from commissaire import models


class TestModel(TestCase):
    """
    Tests for the commissaire.models.Model using a subclass.
    """

    def test_new(self):
        """
        Verify using new on a model creates a default instance.
        """
        instance = models.Cluster.new(name='honeynut')
        for key, value in models.Cluster._attribute_defaults.items():
            self.assertEquals(value, getattr(instance, key))

    def test_to_json(self):
        """
        Verify to_json returns a complete json string.
        """
        instance = models.Host.new(
            address='127.0.0.1',
            ssh_priv_key='secret')
        self.assertIn(
            'ssh_priv_key',
            json.loads(instance.to_json()))

    def test_to_json_with_expose(self):
        """
        Verify to_json returns additional exposed items in the json string.
        """
        instance = models.Cluster.new(name='test')
        self.assertIn(
            'hosts',
            json.loads(instance.to_json(expose=['hosts'])))

    def test_to_json_safe(self):
        """
        Verify to_json_safe returns a sanitized json string.
        """
        instance = models.Host.new(
            address='127.0.0.1',
            ssh_priv_key='secret')
        self.assertNotIn(
            'ssh_priv_key',
            json.loads(instance.to_json_safe()))

    def test_to_json_safe_with_expose(self):
        """
        Verify to_json_safe returns additional exposed items in the json string.
        """
        instance = models.Cluster.new(name='test')
        self.assertIn(
            'hosts',
            json.loads(instance.to_json_safe(expose=['hosts'])))

    def test_to_dict(self):
        """
        Verify to_dict returns a complete dict.
        """
        instance = models.Host.new(
            address='127.0.0.1',
            ssh_priv_key='secret')
        self.assertIn(
            'ssh_priv_key',
            instance.to_dict())

    def test_to_dict_safe(self):
        """
        Verify to_dict_safe returns a sanitized dict.
        """
        instance = models.Host.new(
            address='127.0.0.1',
            ssh_priv_key='secret')
        self.assertNotIn(
            'ssh_priv_key',
            instance.to_dict_safe())

    def test__coerce(self):
        """
        Verify _coerce casts fields when the data is castable.
        """
        address = 123
        instance = models.Host.new(address=address)
        instance._coerce()
        self.assertEquals(str(address), instance.address)

    def test__coerce_failure(self):
        """
        Verify _coerce raises when a field can not be cast.
        """
        hosts = 123
        instance = models.Hosts.new(hosts=hosts)
        self.assertRaises(
            models.CoercionError,
            instance._coerce)


class _TypeValidationTest(TestCase):
    """
    Mixin to test models that need to do type testing.
    """

    #: The model to test
    model = None
    #: Keyword arguments to pass to the Model.new() method
    model_kwargs = {'name': 'test'}
    #: Valid types
    valid_types = []

    def test__validate_with_valid_types(self):
        """
        Ensure that _validate allows all known valid types.
        """
        local_kwargs = self.model_kwargs.copy()
        for valid_type in self.valid_types:
            local_kwargs['type'] = valid_type
            instance = self.model.new(**local_kwargs)
            self.assertIsNone(instance._validate())

    def test__validate_with_invalid_types(self):
        """
        Ensure that _validate enforces type rules.
        """
        local_kwargs = self.model_kwargs.copy()
        local_kwargs['type'] = 'idonotexist'
        instance = self.model.new(**local_kwargs)

        self.assertRaises(
            models.ValidationError,
            instance._validate,
        )


class TestNetworkModel(_TypeValidationTest):
    """
    Extra tests for the Network model.
    """
    model = models.Network
    valid_types = C.NETWORK_TYPES


class TestContainerManagerModel(_TypeValidationTest):
    """
    Extra tests for the ContainerManagerConfig model.
    """
    model = models.ContainerManagerConfig
    valid_types = C.CONTAINER_MANAGER_TYPES
