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
Host(s) handlers.

"""
import datetime
import falcon
import etcd
import json

from commissaire.model import Model
from commissaire.queues import INVESTIGATE_QUEUE
from commissaire.resource import Resource


class Host(Model):
    """
    Representation of a Host.
    """
    _json_type = dict
    _attributes = (
        'address', 'status', 'os', 'cpus', 'memory',
        'space', 'last_check', 'ssh_priv_key')
    _hidden_attributes = ('ssh_priv_key', )


class Hosts(Model):
    """
    Representation of a group of one or more Hosts.
    """
    _json_type = list
    _attributes = ('hosts', )


class HostsResource(Resource):
    """
    Resource for working with Hosts.
    """

    def on_get(self, req, resp):
        """
        Handles GET requests for Hosts.

        :param req: Request instance that will be passed through.
        :type req: falcon.Request
        :param resp: Response instance that will be passed through.
        :type resp: falcon.Response
        """
        try:
            hosts_dir = self.store.get('/commissaire/hosts/')
        except etcd.EtcdKeyNotFound:
            self.logger.warn(
                'Etcd does not have any hosts. Returning [] and 404.')
            resp.status = falcon.HTTP_404
            req.context['model'] = None
            return
        results = []
        # Don't let an empty host directory through
        if len(hosts_dir._children):
            for host in hosts_dir.leaves:
                results.append(Host(**json.loads(host.value)))
            resp.status = falcon.HTTP_200
            req.context['model'] = Hosts(hosts=results)
        else:
            self.logger.debug(
                'Etcd has a hosts directory but no content.')
            resp.status = falcon.HTTP_200
            req.context['model'] = None


class HostResource(Resource):
    """
    Resource for working with a single Host.
    """

    def on_get(self, req, resp, address):
        """
        Handles retrieval of an existing Host.

        :param req: Request instance that will be passed through.
        :type req: falcon.Request
        :param resp: Response instance that will be passed through.
        :type resp: falcon.Response
        :param address: The address of the Host being requested.
        :type address: str
        """
        # TODO: Verify input
        try:
            host = self.store.get('/commissaire/hosts/{0}'.format(address))
        except etcd.EtcdKeyNotFound:
            resp.status = falcon.HTTP_404
            return

        resp.status = falcon.HTTP_200
        host.address = address
        req.context['model'] = Host(**json.loads(host.value))

    def on_put(self, req, resp, address):
        """
        Handles the creation of a new Host.

        :param req: Request instance that will be passed through.
        :type req: falcon.Request
        :param resp: Response instance that will be passed through.
        :type resp: falcon.Response
        :param address: The address of the Host being requested.
        :type address: str
        """
        # TODO: Verify input
        try:
            host = self.store.get('/commissaire/hosts/{0}'.format(address))
            resp.status = falcon.HTTP_409
            return
        except etcd.EtcdKeyNotFound:
            data = req.stream.read().decode()
            host_creation = json.loads(data)
            ssh_priv_key = host_creation['ssh_priv_key']
            host_creation['address'] = address
            host_creation['os'] = ''
            host_creation['status'] = 'investigating'
            host_creation['cpus'] = -1
            host_creation['memory'] = -1
            host_creation['space'] = -1
            host_creation['ssh_priv_key'] = ssh_priv_key
            host_creation['last_check'] = None
            host = Host(**host_creation)
            new_host = self.store.set(
                '/commissaire/hosts/{0}'.format(
                    address), host.to_json(secure=True))
            INVESTIGATE_QUEUE.put((host_creation, ssh_priv_key))
            resp.status = falcon.HTTP_201
            req.context['model'] = Host(**json.loads(new_host.value))

    def on_delete(self, req, resp, address):
        """
        Handles the Deletion of a Host.

        :param req: Request instance that will be passed through.
        :type req: falcon.Request
        :param resp: Response instance that will be passed through.
        :type resp: falcon.Response
        :param address: The address of the Host being requested.
        :type address: str
        """
        resp.body = '{}'
        try:
            host = self.store.delete(
                '/commissaire/hosts/{0}'.format(address))
            resp.status = falcon.HTTP_410
        except etcd.EtcdKeyNotFound:
            resp.status = falcon.HTTP_404
