# Copyright (C) 2017  Red Hat, Inc
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
Tests for the commissaire.storage.notify.StorageNotify class.
"""

from unittest import mock

from . import TestCase

import commissaire.models as models

from commissaire.storage.notify import StorageNotify

class TestCommissaireStorageNotify(TestCase):
    """
    Tests for the StorageNotify class.
    """

    def setUp(self):
        """
        Set up a StorageNotify instance
        """
        self.notify = StorageNotify()
        self.notify.logger = mock.MagicMock()
        self.notify._producer = None

        self.model = models.Host.new(address='127.0.0.1')
        self.body = {
            'class': self.model.__class__.__name__,
            'model': self.model.to_dict_safe()
        }

    def get_routing_key(self):
        """
        Returns a routing key appropriate for the current body
        """
        return 'notify.storage.{}.{}'.format(
            self.body['class'], self.body['event'])

    def test_created(self):
        """
        Test created() method with a producer
        """
        self.body['event'] = 'created'
        self.notify._producer = mock.MagicMock()
        self.notify.created(self.model)
        self.notify._producer.publish.assert_called_once_with(
            self.body, self.get_routing_key(), mock.ANY)

    def test_created_not_connected(self):
        """
        Test created() method without a producer
        """
        self.body['event'] = 'created'
        self.notify.created(self.model)
        self.notify.logger.warn.assert_called_once_with(
            mock.ANY, self.get_routing_key())

    def test_deleted(self):
        """
        Test deleted() method with a producer
        """
        self.body['event'] = 'deleted'
        self.notify._producer = mock.MagicMock()
        self.notify.deleted(self.model)
        self.notify._producer.publish.assert_called_once_with(
            self.body, self.get_routing_key(), mock.ANY)

    def test_deleted_not_connected(self):
        """
        Test deleted() method without a producer
        """
        self.body['event'] = 'deleted'
        self.notify.deleted(self.model)
        self.notify.logger.warn.assert_called_once_with(
            mock.ANY, self.get_routing_key())

    def test_updated(self):
        """
        Test updated() method with a producer
        """
        self.body['event'] = 'updated'
        self.notify._producer = mock.MagicMock()
        self.notify.updated(self.model)
        self.notify._producer.publish.assert_called_once_with(
            self.body, self.get_routing_key(), mock.ANY)

    def test_updated_not_connected(self):
        """
        Test updated() method without a producer
        """
        self.body['event'] = 'updated'
        self.notify.updated(self.model)
        self.notify.logger.warn.assert_called_once_with(
            mock.ANY, self.get_routing_key())
