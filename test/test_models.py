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
        instance = models.Cluster.new()
        for key, value in models.Cluster._attribute_defaults.items():
            self.assertEquals(value, getattr(instance, key))

    def test_to_json(self):
        """
        Verify to_json returns a sanitized json string.
        """
        instance = models.Host.new(ssh_priv_key='secret')
        # ssh_priv_key should be hidden unless secure is True
        self.assertNotIn(
            'ssh_priv_key',
            json.loads(instance.to_json()))
        self.assertIn(
            'ssh_priv_key',
            json.loads(instance.to_json(secure=True)))

    def test_to_dict(self):
        """
        Verify to_dict returns a sanitized json string.
        """
        instance = models.Host.new(ssh_priv_key='secret')
        # ssh_priv_key should be hidden unless secure is True
        self.assertNotIn(
            'ssh_priv_key',
            instance.to_dict())
        self.assertIn(
            'ssh_priv_key',
            instance.to_dict(secure=True))


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

class TestClusterModel(_TypeValidationTest):
    """
    Extra tests for the Cluster model.
    """
    model = models.Cluster
    valid_types = C.CLUSTER_TYPES


class TestNetworkModel(_TypeValidationTest):
    """
    Extra tests for the Network model.
    """
    model = models.Network
    valid_types = C.NETWORK_TYPES
