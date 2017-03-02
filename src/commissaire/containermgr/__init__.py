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

    def __init__(self, config):
        """
        Creates a new instance of the ContainerManagerBase.

        :param config: Configuration details
        :type config: dict
        """
        self.logger = logging.getLogger('containermgr')

    def node_registered(self, address):
        """
        Checks if a node is registered to the container manager.

        Raises ContainerManagerError if the node is NOT registered.

        :param address: Address of the node
        :type address: str
        :raises: commissaire.bus.ContainerManagerError
        """
        raise NotImplementedError(
            'ContainerManagerBase().node_registered() must be overridden.')

    def register_node(self, address):
        """
        Registers a node to the container manager.

        :param address: Address of the node
        :type address: str
        :raises: commissaire.bus.ContainerManagerError
        """
        raise NotImplementedError(
            'ContainerManagerBase().register_node() must be overridden.')

    def remove_node(self, address):
        """
        Removes a node from the container manager.

        :param address: Address of the node
        :type address: str
        :raises: commissaire.bus.ContainerManagerError
        """
        raise NotImplementedError(
            'ContainerManagerBase().remove_node() must be overridden.')

    def remove_all_nodes(self):
        """
        Removes all nodes from the container manager.

        :raises: commissaire.bus.ContainerManagerError
        """
        raise NotImplementedError(
            'ContainerManagerBase().remove_all_nodes() must be overridden.')

    def get_node_status(self, address):
        """
        Gets a node's status from the container manager.

        :param address: Address of the node
        :type address: str
        :returns: Status of the node according to the container manager
        :rtype: dict
        :raises: commissaire.bus.ContainerManagerError
        """
        raise NotImplementedError(
            'ContainerManagerBase().get_node_status() must be overridden.')
