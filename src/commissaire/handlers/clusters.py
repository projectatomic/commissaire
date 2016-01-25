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
Cluster(s) handlers.
"""

import falcon
import etcd
import json

from commissaire.model import Model
from commissaire.resource import Resource


class Cluster(Model):
    """
    Representation of a Cluster.
    """
    _json_type = dict
    _attributes = ('status',)

    def __init__(self, **kwargs):
        Model.__init__(self, **kwargs)
        # Hosts is always calculated, not stored in etcd.
        self.hosts = {'total': 0,
                      'available': 0,
                      'unavailable': 0}

    # FIXME Generalize and move to Model?
    def to_json_with_hosts(self):
        data = {}
        for key in self._attributes:
            data[key] = getattr(self, key)
        data['hosts'] = self.hosts
        return json.dumps(data)


class Clusters(Model):
    """
    Representation of a group of one or more Clusters.
    """
    _json_type = list
    _attributes = ('clusters',)


class ClustersResource(Resource):
    """
    Resource for working with Clusters.
    """

    def on_get(self, req, resp):
        """
        Handles GET requests for Clusters.

        :param req: Request instance that will be passed through.
        :type req: falcon.Request
        :param resp: Response instance that will be passed through.
        :type resp: falcon.Response
        """
        try:
            clusters_dir = self.store.get('/commissaire/clusters/')
        except etcd.EtcdKeyNotFound:
            self.logger.warn(
                'Etcd does not have any clusters. Returning [] and 404.')
            resp.status = falcon.HTTP_404
            req.context['model'] = None
            return
        results = []
        # Don't let an empty clusters directory through
        if len(clusters_dir._children):
            for cluster in clusters_dir.leaves:
                results.append(Cluster(**json.loads(cluster.value)))
            resp.status = falcon.HTTP_200
            req.context['model'] = Clusters(clusters=results)
        else:
            self.logger.debug(
                'Etcd has a clusters directory but no content.')
            resp.status = falcon.HTTP_200
            req.context['model'] = None


class ClusterResource(Resource):
    """
    Resource for working with a single Cluster.
    """

    def _calculate_hosts(self, cluster):
        try:
            etcd_resp = self.store.get('/commissaire/hosts')
        except etcd.EtcdKeyNotFound:
            self.logger.warn(
                'Etcd does not have any hosts. '
                'Cannot determine cluster stats.')
            return

        available = unavailable = 0
        total = len(etcd_resp.node.children)
        for child in etcd_resp.node.children:
            host = Host(**json.loads(child.value))
            if host.status == 'active':
                available += 1
            else:
                unavailable += 1

        cluster.hosts['total'] = total
        cluster.hosts['available'] = available
        cluster.hosts['unavailable'] = unavailable

    def on_get(self, req, resp, name):
        """
        Handles retrieval of an existing Cluster.

        :param req: Request instance that will be passed through.
        :type req: falcon.Request
        :param resp: Response instance that will be passed through.
        :type resp: falcon.Response
        :param name: The name of the Cluster being requested.
        :type name: str
        """
        key = '/commissaire/clusters/{0}'.format(name)
        try:
            etcd_resp = self.store.get(key)
        except etcd.EtcdKeyNotFound:
            resp.status = falcon.HTTP_404
            return

        cluster = Cluster(**json.loads(etcd_resp.value))
        self._calculate_hosts(cluster)
        # Have to set resp.body explicitly to include Hosts.
        resp.body = cluster.to_json_with_hosts()
        resp.status = falcon.HTTP_200

    def on_put(self, req, resp, name):
        """
        Handles the creation of a new Cluster.

        :param req: Request instance that will be passed through.
        :type req: falcon.Request
        :param resp: Response instance that will be passed through.
        :type resp: falcon.Response
        :param name: The name of the Cluster being created.
        :type name: str
        """
        # PUT is idempotent, and since there's no body to this request,
        # there's nothing to conflict with.  The request should always
        # succeed, even if we didn't actually do anything.
        key = '/commissaire/clusters/{0}'.format(name)
        try:
            etcd_resp = self.store.get(key)
        except etcd.EtcdKeyNotFound:
            cluster = Cluster(status='ok')
            etcd_resp = self.store_set(key, cluster.to_json(secure=True))
        cluster = Cluster(**json.loads(etcd_resp.value))
        self._calculate_hosts(cluster)
        # Have to set resp.body explictly to include Hosts.
        resp.body = cluster.to_json_with_hosts()
        resp.status = falcon.HTTP_201

    def on_delete(self, req, resp, name):
        """
        Handles the deletion of a Cluster.

        :param req: Request instance that will be passed through.
        :type req: falcon.Request
        :param resp: Response instance that will be passed through.
        :type resp: falcon.Response
        :param name: The name of the Cluster being deleted.
        :type name: str
        """
        key = '/commissaire/clusters/{0}'.format(name)
        resp.body = '{}'
        try:
            cluster = self.store.delete(key)
            resp.status = falcon.HTTP_410
        except etcd.EtcdKeyNotFound:
            resp.status = falcon.HTTP_404
