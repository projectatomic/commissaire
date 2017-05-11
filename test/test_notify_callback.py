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
Tests for the commissaire.storage.client.NotifyCallback decorator class.
"""

from unittest import mock

from . import TestCase

import commissaire.models as models

from commissaire.storage.client import (
    NotifyCallback, NOTIFY_EVENT_CREATED)

class TestCommissaireNotifyCallback(TestCase):
    """
    Tests for the NotifyCallback class.
    """

    def setUp(self):
        """
        Set up a skeletal notification.
        """
        self.body = {
            'event': 'created',
            'class': 'Host',
            'model': {'address': '127.0.0.1'}
        }
        self.message = mock.MagicMock()
        self.event = None
        self.model = None

    @NotifyCallback
    def callback(self, event, model, message):
        self.event = event
        self.model = model

    def test_valid_callback(self):
        """
        Test NotifyCallback with valid arguments.
        """
        print('body: {}'.format(self.body))
        self.callback(self.body, self.message)
        self.assertEquals(self.event, 'created')
        self.assertIsInstance(self.model, models.Host)

    def test_bad_event(self):
        """
        Test NotifyCallback with a bad event name.
        """
        self.body['event'] = 'bogus'
        self.callback(self.body, self.message)
        self.assertIsNone(self.event)
        self.assertIsNone(self.model)

    def test_bad_class(self):
        """
        Test NotifyCallback with a bad class name.
        """
        self.body['class'] = 'BogusModelClass'
        self.callback(self.body, self.message)
        self.assertIsNone(self.event)
        self.assertIsNone(self.model)

    def test_bad_model(self):
        """
        Test NotifyCallback with a bad model dict.
        """
        del self.body['model']['address']
        self.callback(self.body, self.message)
        self.assertIsNone(self.event)
        self.assertIsNone(self.model)
