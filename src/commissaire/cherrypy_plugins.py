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
CherryPy plugin for storing objects.
"""

import sys

import etcd

from cherrypy.process import plugins


class CherryPyStorePlugin(plugins.SimplePlugin):

    def __init__(self, bus, store_kwargs):
        """
        Creates a new instance of the CherryPyStorePlugin.

        :param bus: The CherryPy bus.
        :type bus: cherrypy.process.wspbus.Bus
        :param store_kwargs: Keyword arguments used to make the Client.
        :type store_kwargs: dict
        """
        plugins.SimplePlugin.__init__(self, bus)
        self.store_kwargs = store_kwargs
        self.store = None

    def _get_store(self):
        """
        Returns an instance of the store. If one has not been created this call
        will also create the client using the self.store_kwargs.

        :returns: The store.
        :rtype: etcd.Client
        """
        if not self.store:
            self.store = etcd.Client(**self.store_kwargs)
        return self.store

    def start(self):
        """
        Starts the plugin.
        """
        self.bus.log('Starting up Store access')
        self.bus.subscribe("store-save", self.store_save)
        self.bus.subscribe("store-get", self.store_get)

    def stop(self):
        """
        Stops the plugin.
        """
        self.bus.log('Stopping down Store access')
        self.bus.unsubscribe("store-save", self.store_save)
        self.bus.unsubscribe("store-get", self.store_get)

    def store_save(self, key, json_entity, **kwargs):
        """
        Saves json to the store.

        :param key: The key to associate the data with.
        :type key: str
        :param json_entity: The json data to save.
        :type json_entity: str
        :param kwargs: All other keyword-args to pass to client
        :type kwargs: dict
        :returns: The stores response and any errors that may have occured
        :rtype: tuple(etcd.EtcdResult, Exception)
        """
        try:
            store = self._get_store()
            return (store.write(key, json_entity, **kwargs), None)
        except:
            _, exc, _ = sys.exc_info()
            return ([], exc)

    def store_get(self, key):
        """
        Retrieves json from the store.

        :param key: The key to associate the data with.
        :type key: str
        :returns: The stores response and any errors that may have occured
        :rtype: tuple(etcd.EtcdResult, Exception)
        """
        try:
            store = self._get_store()
            return (store.get(key), None)
        except:
            _, exc, _ = sys.exc_info()
            return ([], exc)
