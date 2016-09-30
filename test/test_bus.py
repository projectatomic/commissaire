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
Tests for the commissaire.bus module.
"""

import json
import uuid

from unittest import mock

from . import TestCase

from commissaire import bus


ID = str(uuid.uuid4())


class TestCommissaireBusMixin(TestCase):
    """
    Tests for the CommissaireBusMixin
    """

    def test_create_id(self):
        """
        Verify BusMixin.create_id makes a unique identifier.
        """
        uid = bus.BusMixin.create_id()
        # It should be a string
        self.assertIs(str, type(uid))
        # And it should be 36 chars in length (uuid.uuid4())
        self.assertEquals(len(ID), len(uid))


    def test_request(self):
        """
        Verify BusMixin.request can request method calls.
        """
        result_dict = {'jsonrpc': '2.0', 'result': []}

        instance = bus.BusMixin() 
        instance.logger = mock.MagicMock()
        instance.connection = mock.MagicMock()
        instance.producer = mock.MagicMock()
        instance.connection.SimpleQueue().get.return_value = mock.MagicMock(
           payload=json.dumps(result_dict))
        # Reset call count
        instance.connection.SimpleQueue.call_count = 0
        instance._exchange = 'exchange'

        method = 'ping'
        routing_key = 'routing_key.' + method
        params = {}
        queue_opts={'durable': False, 'auto_delete': True}

        # Omit the method to test extracting it from the routing key.
        result = instance.request(routing_key, params=params)
        self.assertEquals(result_dict, result)
        # A new SimpleQueue should have been created
        instance.connection.SimpleQueue.assert_called_once_with(
            mock.ANY,
            queue_opts=queue_opts
        )
        # A jsonrpc message should have been published to the bus
        instance.producer.publish.assert_called_once_with(
            {
                'jsonrpc': '2.0',
                'id': mock.ANY,
                'method': method,
                'params': params,
            },
            routing_key,
            declare=[instance._exchange],
            reply_to=mock.ANY)
        # The simple queue should be used to get a response
        instance.connection.SimpleQueue.__call__(
            ).get.assert_called_once_with(block=True, timeout=mock.ANY)
        # And finally the queue should be closed
        instance.connection.SimpleQueue.__call__(
            ).close.assert_called_once_with()
