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
Tests for the commissaire.storage module.
"""

import logging
import json

from unittest import mock

from . import TestCase

from commissaire import storage
from commissaire.models import Host, Cluster


class TestCommissaireStorage_get_uniform_model_type(TestCase):
    """
    Tests for the get_uniform_type function.
    """

    def test_get_uniform_model_type_with_valid_types(self):
        """
        Verify get_uniform_model_type works when types are the same.
        """
        self.assertEquals(
            Host,
            storage.get_uniform_model_type([
                Host.new(address='127.0.0.1'),
                Host.new(address='127.0.0.2')]))

    def test_get_uniform_model_type_with_multiple_types(self):
        """
        Verify get_uniform_model_type raises when types are not the same.
        """
        self.assertRaises(
            TypeError,
            storage.get_uniform_model_type,
            [Host.new(address='127.0.0.1'),
             Cluster.new(name='test')])

    def test_get_uniform_model_type_with_invalid_types(self):
        """
        Verify get_uniform_model_type raises when types are invalid.
        """
        self.assertRaises(
            TypeError,
            storage.get_uniform_model_type,
            [object()])
