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
Test cases for the commissaire.cherrypy_plugins module.
"""

import mock

from . import TestCase
from commissaire import cherrypy_plugins


class Test_CherryPyStorePlugin(TestCase):
    """
    Tests for the CherryPyStorePlugin class.
    """

    #: Topics that should be registered
    topics = ('store-get', 'store-save')

    def before(self):
        """
        Called before every test.
        """
        self.bus = mock.MagicMock()
        self.store_kwargs = {}
        self.plugin = cherrypy_plugins.CherryPyStorePlugin(
            self.bus, self.store_kwargs)

    def after(self):
        """
        Called after every test.
        """
        self.bus = None
        self.plugin = None

    def test_cherrypy_store_plugin_creation(self):
        """
        Verify that the creation of the plugin works as it should.
        """
        with mock.patch('etcd.Client') as _store:
            # Store should be None
            self.assertEquals(None, self.plugin.store)
            # The Store should not have been called in any way
            self.assertEquals(0, _store().call_count)

    def test_cherrypy_store_plugin__get_store(self):
        """
        Verify _get_store properly obtains a store instance.
        """
        with mock.patch('etcd.Client') as _store:
            store = self.plugin._get_store()
            # We should have a store created with our kwargs
            _store.assert_called_once_with(**self.store_kwargs)
            # The returned stoer should be exactly the same
            self.assertEquals(store, _store())
            self.assertEquals(store, self.plugin.store)

    def test_cherrypy_store_plugin_start(self):
        """
        Verify start() subscribes the proper topics.
        """
        self.plugin.start()
        # subscribe should be called a specific number of times
        self.assertEquals(len(self.topics), self.bus.subscribe.call_count)
        # Each subscription should have it's own call to register a callback
        for topic in self.topics:
            self.bus.subscribe.assert_any_call(topic, mock.ANY)

    def test_cherrypy_store_plugin_stop(self):
        """
        Verify stop() unsubscribes the proper topics.
        """
        self.plugin.stop()
        # unsubscribe should be called a specific number of times
        self.assertEquals(len(self.topics), self.bus.unsubscribe.call_count)
        # Each unsubscription should have it's own call
        # to deregister a callback
        for topic in self.topics:
            self.bus.unsubscribe.assert_any_call(topic, mock.ANY)

    def test_cherrypy_store_save(self):
        """
        Verify store_save handles data properly.
        """
        key = '/test'
        data = "{}"
        with mock.patch('etcd.Client') as _store:
            store = _store()
            expected_result = mock.MagicMock('etcd.EtcdResult')
            store.write.return_value = expected_result
            result = self.plugin.store_save(key, data)
            # The store should be called to set the data
            store.write.assert_called_once_with(key, data)
            # The result should be a tuple
            self.assertEquals((expected_result, None), result)

    def test_cherrypy_store_save_error(self):
        """
        Verify store_save handles errors properly.
        """
        key = '/test'
        data = "{}"
        with mock.patch('etcd.Client') as _store:
            store = _store()
            expected_result = Exception()
            store.write.side_effect = expected_result
            result = self.plugin.store_save(key, data)
            # The store should be called to set the data
            store.write.assert_called_once_with(key, data)
            # The result should be a tuple
            self.assertEquals(([], expected_result), result)

    def test_cherrypy_store_get(self):
        """
        Verify store_get returns data properly.
        """
        key = '/test'
        with mock.patch('etcd.Client') as _store:
            store = _store()
            expected_result = mock.MagicMock('etcd.EtcdResult')
            store.get.return_value = expected_result
            result = self.plugin.store_get(key)
            # The store should be called to get the data
            store.get.assert_called_once_with(key)
            # The result should be a tuple
            self.assertEquals((expected_result, None), result)

    def test_cherrypy_store_get_error(self):
        """
        Verify store_get returns errors properly.
        """
        key = '/test'
        with mock.patch('etcd.Client') as _store:
            store = _store()
            expected_result = Exception()
            store.get.side_effect = expected_result
            result = self.plugin.store_get(key)
            # The store should be called to get the data
            store.get.assert_called_once_with(key)
            # The result should be a tuple
            self.assertEquals(([], expected_result), result)
