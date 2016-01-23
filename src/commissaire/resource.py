# Copyright (C) 2016  Red Hat, Inc
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
Basic Resource for commissaire.
"""

import logging


class Resource:
    """
    Parent class for all commissaire Resources.
    """

    def __init__(self, store, queue=None, **kwargs):
        """
        Creates a new Resource instance.

        :param store: The etcd client to for storing/retrieving data.
        :type store: etcd.Client
        :param queue: Optional queue to use with the Resource instance.
        :type queue: gevent.queue.Queue
        :param kwargs: All other keyword arguemtns.
        :type kwargs: dict
        :returns: A new Resource instance.
        :rtype: commissaire.resource.Resource
        """
        self.store = store
        self.queue = queue
        self.logger = logging.getLogger('resources')
