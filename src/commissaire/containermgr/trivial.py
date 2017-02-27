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
A trivial container manager.
"""

from commissaire.bus import ContainerManagerError
from commissaire.containermgr import ContainerManagerBase


class TrivialContainerManager(ContainerManagerBase):  # pragma: no cover
    """
    Trivial, memory-only container manager to facilitate end-to-end testing.
    """

    def __init__(self, config):
        """
        Creates an instance of a trivial container manager.

        :param config: Configuration details
        :type config: dict
        """
        super().__init__(config)
        self.nodes = set()

    def node_registered(self, address):
        """
        Checks if a node is registered to the container manager.

        Raises ContainerManagerError if the node is NOT registered.

        :param address: Address of the node
        :type address: str
        :raises: commissaire.containermgr.ContainerManagerError
        """
        if address not in self.nodes:
            message = 'Node {} is not registered'.format(address)
            self.logger.error(message)
            raise ContainerManagerError(message)

    def register_node(self, address):
        """
        Registers a node to the container manager.

        For this trivial container manager, the method is always successful.

        :param address: Address of the node
        :type address: str
        """
        # This method is idempotent.
        self.nodes.add(address)
        self.logger.debug('Registered node {}'.format(address))

    def remove_node(self, address):
        """
        Removes a node from the container manager.

        For this trivial container manager, the method is always successful.

        :param address: Address of the node
        :type address: str
        """
        # This method is idempotent.
        self.nodes.discard(address)
        self.logger.debug('Removed node {}'.format(address))

    def remove_all_nodes(self):
        """
        Remove all nodes from the container manager.

        For this trivial container manager, the method is always successful.
        """
        # This method is idempotent.
        self.nodes.clear()
        self.logger.debug('Removed all nodes')

    def get_node_status(self, address):
        """
        Gets a node's status from the container manager.

        For this trivial container manager, the returned dictionary contains
        two keys: 'node' (the node's address) and 'status' (always 'ok').

        :param address: Address of the node
        :type address: str
        :returns: Status of the node according to the container manager
        :rtype: dict
        :raises: commissaire.containermgr.ContainerManagerError
        """
        if address in self.nodes:
            status = {'node': address, 'status': 'ok'}
            self.logger.debug('Node status: {}'.format(status))
            return status
        else:
            message = 'Node {} is not registered'.format(address)
            self.logger.error(message)
            raise ContainerManagerError(message)


PluginClass = TrivialContainerManager
