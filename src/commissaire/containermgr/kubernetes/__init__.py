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
The kubernetes container manager package.
"""

import requests

from urllib.parse import urljoin as _urljoin

from commissaire import constants as C
from commissaire.containermgr import ContainerManagerBase


class ContainerManager(ContainerManagerBase):
    """
    Kubernetes container manager implementation.
    """

    cluster_type = C.CLUSTER_TYPE_KUBERNETES

    def __init__(self, config):
        """
        Creates an instance of the Kubernetes Container Manager.

        :param config: Configuration details
        :type config: dict
        """
        ContainerManagerBase.__init__(self, config)
        self.con = requests.Session()
        token = config.get('token', None)
        if token:
            self.con.headers["Authorization"] = "Bearer {0}".format(token)
            self.logger.info('Using bearer token')
            self.logger.debug('Bearer token: {0}'.format(token))

        certificate_path = config.get('certificate_path')
        certificate_key_path = config.get('certificate_key_path')
        if certificate_path and certificate_key_path:
            self.con.cert = (certificate_path, certificate_key_path)
            self.logger.info(
                'Using client side certificate. Certificate path: {0} '
                'Certificate Key Path: {1}'.format(
                    certificate_path, certificate_key_path))

        # TODO: Verify TLS!!!
        self.con.verify = False
        self.base_uri = urljoin(config['server_url'], '/api/v1')
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

    def get_host_status(self, address, raw=False):
        """
        Returns the node status.

        :param address: The address of the host to check.
        :type address: str
        :param raw: If the result should be limited to its own status.
        :type raw: bool
        :returns: The response back from kubernetes.
        :rtype: requests.Response
        """
        part = '/nodes/{0}'.format(address)
        resp = self._get(part)
        data = resp.json()
        if raw:
            data = data['status']
        return (resp.status_code, data)

#: Friendly name for the class
KubeContainerManager = ContainerManager
