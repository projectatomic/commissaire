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
The container manager package.
"""

import logging


class ContainerManagerBase(object):  # pragma: no cover
    """
    Base class for all container managers.
    """

    def __init__(self):
        """
        Creates a new instance of the ContainerManagerBase.
        """
        self.logger = logging.getLogger('containermgr')

    def node_registered(self, name):
        """
        Checks is a node was registered.

        :param name: The name of the node.
        :type name: str
        :returns: True if registered, otherwise False
        :rtype: bool
        """
        raise NotImplementedError(
            'ContainerManagerBase().node_registered() must be overridden.')
