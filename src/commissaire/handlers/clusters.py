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
    _attributes = (
        'status', 'hosts')


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
