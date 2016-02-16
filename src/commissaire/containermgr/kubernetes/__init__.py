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
The kubernetes container manager package.
"""

import requests

from commissaire.containermgr import ContainerManagerBase


class ContainerManager(ContainerManagerBase):
    """
    Kubernetes container manager implementation.
    """

    def __init__(self, config):
        """
        Creates an instance of the Kubernetes Container Manager.

        :param config: Configuration information.
        :type config: commissaire.config.Config
        """
        ContainerManagerBase.__init__(self)
        self.host = config.kubernetes['uri'].hostname
        self.port = config.kubernetes['uri'].port
        self.con = requests.Session()
        token = config.kubernetes['token']
        self.con.headers["Authorization"] = "Bearer {0}".format(token)
        # TODO: Verify TLS!!!
        self.con.verify = False
        self.base_uri = 'http://{0}:{1}/api/v1'.format(
            self.host, self.port)
        self.logger.info('Kubernetes Container Manager created: {0}'.format(
            self.base_uri))
        self.logger.debug(
            'Kubernetes Container Manager: {0}'.format(self.__dict__))

    def _get(self, part, *args, **kwargs):
        """
        Get information from the Kubernetes apiserver.

        :param part: The URI part. EG: /nodes
        :type part: sdtr
        :param args: All other non-keyword arguments.
        :type args: tuple
        :param kwargs: All other keyword arguments.
        :type kwargs: dict
        :returns: requests.Response
        """
        # Fix part if it doesn't start with a slash
        if not part.startswith('/'):
            self.logger.debug(
                'Part given without starting slash. Adding...')
            part = '/{0}'.format(part)

        self.logger.debug('Executing GET for {0}'.format(part))
        resp = self.con.get(
            '{0}{1}'.format(self.base_uri, part), *args, **kwargs)
        self.logger.debug('Response for {0}. Status: {1}'.format(
            part, resp.status_code))
        return resp

    def node_registered(self, name):
        """
        Checks is a node was registered.

        :param name: The name of the node.
        :type name: str
        :returns: True if registered, otherwise False
        :rtype: bool
        """
        part = '/nodes/{0}'.format(name)
        resp = self._get(part)
        # TODO: Stronger checking would be better
        if resp.status_code == 200:
            return True
        return False


#: Friendly name for the class
KubeContainerManager = ContainerManager
