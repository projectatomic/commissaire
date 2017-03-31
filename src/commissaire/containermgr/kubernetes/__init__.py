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

import json
import requests

from urllib.parse import urljoin, urlparse

from commissaire.bus import ContainerManagerError
from commissaire.containermgr import ContainerManagerBase
from commissaire.util.config import ConfigurationError


class KubeContainerManager(ContainerManagerBase):
    """
    Kubernetes container manager implementation.
    """

    def __init__(self, config):
        """
        Creates an instance of the Kubernetes Container Manager.

        :param config: Configuration details
        :type config: dict
        """
        ContainerManagerBase.__init__(self, config)
        self.__class__.check_config(config)
        self.con = requests.Session()
        token = config.get('token', None)
        if token:
            self.con.headers['Authorization'] = 'Bearer {}'.format(token)
            self.logger.info('Using bearer token')
            self.logger.debug('Bearer token: %s', token)

        certificate_path = config.get('certificate_path')
        certificate_key_path = config.get('certificate_key_path')
        if certificate_path and certificate_key_path:
            self.con.cert = (certificate_path, certificate_key_path)
            self.logger.info(
                'Using client side certificate. Certificate path: %s '
                'Certificate Key Path: %s',
                certificate_path, certificate_key_path)

        # TODO: Verify TLS!!!
        self.con.verify = False
        self.base_uri = urljoin(config['server_url'], '/api/v1')
        self.logger.info(
            'Kubernetes Container Manager created: %s', self.base_uri)
        self.logger.debug(
            'Kubernetes Container Manager: %s', self.__dict__)

    @classmethod
    def check_config(cls, config):
        """
        Examines the configuration parameters for an ContainerManager
        and throws a ConfigurationError if any parameters are invalid.

        :param cls: ContainerManager class.
        :type cls: class
        :param config: Configuration dictionary to check.
        :type config: dict
        :returns: True if configuration is valid
        :rtype: bool
        :raises: commissaire.util.config.ConfigurationError
        """
        try:
            url = urlparse(config['server_url'])
        except KeyError:
            raise ConfigurationError(
                'server_url is a required configuration item')

        if (bool(config.get('certificate_path')) ^
                bool(config.get('certificate_key_path'))):
            raise ConfigurationError(
                'Both "certificate_path" and "certificate_key_path" '
                'must be provided to use a client side certificate')
        if config.get('certificate_path'):
            if url.scheme != 'https':
                raise ConfigurationError(
                    'Server URL scheme must be "https" when using client '
                    'side certificates (got "{}")'.format(url.scheme))

    def _fix_part(self, part):
        """
        Ensures the URI part starts with a slash.

        :param part: The URI part. EG: /nodes
        :type part: str
        :returns: The part in the proper format.
        :rtype: str
        """
        if not part.startswith('/'):
            self.logger.debug(
                'Part given without starting slash. Adding...')
            part = '/{}'.format(part)

        return part

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
        part = self._fix_part(part)
        self.logger.debug('Executing GET for %s', part)
        resp = self.con.get(
            '{}{}'.format(self.base_uri, part), *args, **kwargs)
        self.logger.debug(
            'Response for %s. Status: %s', part, resp.status_code)
        return resp

    def _delete(self, part, *args, **kwargs):
        """
        Delete data from the Kubernetes apiserver.

        :param part: The URI part. EG: /nodes
        :type part: str
        ::param payload: Data to send with the DELETE.
        :type payload: dict
        :param args: All other non-keyword arguments.
        :type args: tuple
        :param kwargs: All other keyword arguments.
        :type kwargs: dict
        :returns: requests.Response
        """
        part = self._fix_part(part)
        self.logger.debug('Executing DELETE for %s.', part)
        resp = self.con.delete(
            '{}{}'.format(self.base_uri, part), *args, **kwargs)
        self.logger.debug(
            'Response for %s. Status: %s', part, resp.status_code)
        return resp

    def _put(self, part, payload, *args, **kwargs):
        """
        Put data to the Kubernetes apiserver.

        :param part: The URI part. EG: /nodes
        :type part: str
        ::param payload: Data to send with the PUT.
        :type payload: dict
        :param args: All other non-keyword arguments.
        :type args: tuple
        :param kwargs: All other keyword arguments.
        :type kwargs: dict
        :returns: requests.Response
        """
        part = self._fix_part(part)
        payload_str = json.dumps(payload)
        self.logger.debug(
            'Executing PUT for %s. Payload=%s', part, payload_str)
        resp = self.con.put(
            '{}{}'.format(self.base_uri, part),
            data=payload_str, *args, **kwargs)
        self.logger.debug(
            'Response for %s. Status: %s', part, resp.status_code)
        return resp

    def _post(self, part, payload, *args, **kwargs):
        """
        Post data to the Kubernetes apiserver.

        :param part: The URI part. EG: /nodes
        :type part: str
        ::param payload: Data to send with the POST.
        :type payload: dict
        :param args: All other non-keyword arguments.
        :type args: tuple
        :param kwargs: All other keyword arguments.
        :type kwargs: dict
        :returns: requests.Response
        """
        part = self._fix_part(part)
        payload_str = json.dumps(payload)
        self.logger.debug(
            'Executing POST for %s. Payload=%s', part, payload_str)
        resp = self.con.post(
            '{}{}'.format(self.base_uri, part),
            data=payload_str, *args, **kwargs)
        self.logger.debug(
            'Response for %s. Status: %s', part, resp.status_code)
        return resp

    def register_node(self, name):
        """
        Registers a node to the Kubernetes Container Manager.

        :param name: The name of the node.
        :type name: str
        :raises: commissaire.bus.ContainerManagerError
        """
        part = '/nodes'

        payload = {
            "kind": "Node",
            "apiVersion": "v1",
            "metadata": {
                "name": name,
            }
        }

        resp = self._post(part, payload)
        if resp.status_code != 201:
            error_msg = (
                'Non-created response when trying to register the node {}. '
                'Status: "{}", Data: "{}"'.format(
                    name, resp.status_code, resp.text))
            self.logger.error(error_msg)
            raise ContainerManagerError(error_msg, resp.status_code)

    def remove_node(self, name):
        """
        Removes a node from the Kubernetes Container Manager.

        :param name: The name of the node.
        :type name: str
        :raises: commissaire.bus.ContainerManagerError
        """
        part = '/nodes/{}'.format(name)

        resp = self._delete(part)
        if resp.status_code != 200:
            error_msg = (
                'Unexpected response when trying to remove the node {}. '
                'Status: {}, Data: {}'.format(
                    name, resp.status_code, resp.text))
            self.logger.error(error_msg)
            raise ContainerManagerError(error_msg, resp.status_code)

    def remove_all_nodes(self):
        """
        Removes all nodes from the Kubernetes Container Manager.

        :raises: commissaire.bus.ContainerManagerError
        """
        resp = self._delete('/nodes')
        if resp.status_code != 200:
            error_msg = (
                'Unexpected response when trying to remove all nodes. '
                'Status: {}, Data: {}'.format(
                    resp.status_code, resp.text))
            self.logger.error(error_msg)
            raise ContainerManagerError(error_msg, resp.status_code)

    def node_registered(self, name):
        """
        Checks is a node was registered.

        :param name: The name of the node.
        :type name: str
        :raises: commissaire.bus.ContainerManagerError
        """
        part = '/nodes/{}'.format(name)
        resp = self._get(part)
        if resp.status_code != 200:
            error_msg = 'Node {} is not registered. Status: {}'.format(
                name, resp.status_code)
            self.logger.error(error_msg)
            raise ContainerManagerError(error_msg, resp.status_code)

    def get_node_status(self, name, raw=False):
        """
        Returns the node status.

        :param name: The name of the node.
        :type name: str
        :param raw: If the result should be limited to its own status.
        :type raw: bool
        :returns: The response back from kubernetes.
        :rtype: dict
        :raises: commissaire.bus.ContainerManagerError
        """
        part = '/nodes/{}'.format(name)
        resp = self._get(part)
        if resp.status_code != 200:
            error_msg = (
                'No status for {} returned. Status: {}'.format(
                    name, resp.status_code))
            self.logger.error(error_msg)
            raise ContainerManagerError(error_msg, resp.status_code)

        data = resp.json()
        if raw:
            data = data['status']
        return data


PluginClass = KubeContainerManager
