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
import falcon
import etcd
import json

from commissaire.resource import Resource
from commissaire.handlers.models import Cluster, Host, Hosts
import commissaire.handlers.util as util


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
            self.logger.debug('Etcd Response: {0}'.format(hosts_dir))
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
            etcd_resp = self.store.get(util.etcd_host_key(address))
            self.logger.debug('Etcd Response: {0}'.format(etcd_resp))
        except etcd.EtcdKeyNotFound:
            resp.status = falcon.HTTP_404
            return

        resp.status = falcon.HTTP_200
        req.context['model'] = Host(**json.loads(etcd_resp.value))

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
        try:
            # Extract what we need from the input data.
            # Don't treat it as a skeletal host record.
            req_data = req.stream.read()
            req_body = json.loads(req_data.decode())
            ssh_priv_key = req_body['ssh_priv_key']
            # Cluster member is optional.
            cluster_name = req_body.get('cluster', None)
        except (KeyError, ValueError):
            self.logger.info(
                'Bad client PUT request for host {0}: {1}'.
                format(address, req_data))
            resp.status = falcon.HTTP_400
            return

        resp.status, host_model = util.etcd_host_create(
            self.store, address, ssh_priv_key, cluster_name)

        req.context['model'] = host_model

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
            host = self.store.delete(util.etcd_host_key(address))
            resp.status = falcon.HTTP_410
        except etcd.EtcdKeyNotFound:
            resp.status = falcon.HTTP_404

        # Also remove the host from all clusters.
        # Note: We've done all we need to for the host deletion,
        #       so if an error occurs from here just log it and
        #       return.
        try:
            clusters_dir = self.store.get('/commissaire/clusters')
            self.logger.debug('Etcd Response: {0}'.format(clusters_dir))
        except etcd.EtcdKeyNotFound:
            self.logger.warn('Etcd does not have any clusters')
            return
        if len(clusters_dir._children):
            self.logger.info(
                'There are clusters associated with {0}...'.format(address))
            for etcd_resp in clusters_dir.leaves:
                cluster = Cluster(**json.loads(etcd_resp.value))
                if address in cluster.hostset:
                    self.logger.info('Removing {0} from cluster {1}'.format(
                        address, etcd_resp.key.split('/')[-1]))
                    cluster.hostset.remove(address)
                    self.store.set(etcd_resp.key, cluster.to_json(secure=True))


class ImplicitHostResource(Resource):
    """
    Resource to handle direct requests from a Host.
    The host's address is inferred from the falcon.Request.
    """

    def on_put(self, req, resp):
        """
        Handles the creation of a new Host.

        :param req: Request instance that will be passed through.
        :type req: falcon.Request
        :param resp: Response instance that will be passed through.
        :type resp: falcon.Response
        """
        try:
            address = req.env['REMOTE_ADDR']
        except KeyError:
            self.logger.info('Unable to determine host address')
            resp.status = falcon.HTTP_400
            return

        try:
            # Extract what we need from the input data.
            # Don't treat it as a skeletal host record.
            req_data = req.stream.read()
            req_body = json.loads(req_data.decode())
            ssh_priv_key = req_body['ssh_priv_key']
            # Cluster member is optional.
            cluster_name = req_body.get('cluster', None)
        except (KeyError, ValueError):
            self.logger.info(
                'Bad client PUT request for host {0}: {1}'.
                format(address, req_data))
            resp.status = falcon.HTTP_400
            return

        resp.status, host_model = util.etcd_host_create(
            self.store, address, ssh_priv_key, cluster_name)

        req.context['model'] = host_model
