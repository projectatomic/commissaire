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
Test cases for the commissaire.handlers.clusters module.
"""

import json

import etcd
import falcon

from . import TestCase
from falcon.testing.helpers import create_environ
from mock import MagicMock
from commissaire.handlers import clusters
from commissaire.script import create_app
from commissaire.middleware import JSONify


class Test_Clusters(TestCase):
    """
    Tests for the Clusters model.
    """
    # XXX: Based on Test_Hosts

    def test_clusters_creation(self):
        """
        Verify Clusters model.
        """
        # Make sure clusters is required
        self.assertRaises(
            TypeError,
            clusters.Clusters
        )

        # Make sure an empty Clusters is still valid
        clusters_model = clusters.Clusters(clusters=[])
        self.assertEquals(
            '[]',
            clusters_model.to_json())

        # Make sure a Cluster is accepted as expected
        clusters_model = clusters.Clusters(
            clusters=[clusters.Cluster(
                status='ok',
                hosts={'total': 1,
                       'available': 1,
                       'unavailable': 0})])
        self.assertEquals(1, len(clusters_model.clusters))
        self.assertEquals(type(str()), type(clusters_model.to_json()))

        # Make sure other instances are not accepted
        clusters_model = clusters.Clusters(clusters=[object()])


class Test_ClustersResource(TestCase):
    """
    Tests for the Clusters resource.
    """
    # XXX: Based on Test_HostsResource

    acluster = ('{"status": "ok",'
                ' "hosts": {"total": 1, "available": 1, "unavailable": 0}}')

    def before(self):
        self.api = falcon.API(middleware=[JSONify()])
        self.datasource = etcd.Client()
        self.return_value = MagicMock(etcd.EtcdResult)
        self.datasource.get = MagicMock(name='get')
        self.datasource.get.return_value = self.return_value
        self.resource = clusters.ClustersResource(self.datasource)
        self.api.add_route('/api/v0/clusters', self.resource)

    def test_clusters_listing(self):
        """
        Verify listing clusters.
        """
        child = MagicMock(value=self.acluster)
        self.return_value._children = [child]
        self.return_value.leaves = self.return_value._children

        body = self.simulate_request('/api/v0/clusters')
        # datasource's get should have been called once
        self.assertEquals(1, self.datasource.get.call_count)
        self.assertEqual(self.srmock.status, falcon.HTTP_200)
        self.assertEqual(
            [json.loads(self.acluster)],
            json.loads(body[0]))

    def test_clusters_listing_with_no_hosts(self):
        """
        Verify listing clusters.
        """
        child = MagicMock(value=self.acluster)
        self.return_value._children = []
        self.return_value.leaves = self.return_value._children

        body = self.simulate_request('/api/v0/clusters')
        # datasource's get should have been called once
        self.assertEquals(1, self.datasource.get.call_count)
        self.assertEqual(self.srmock.status, falcon.HTTP_200)
        self.assertEqual({}, json.loads(body[0]))

    def test_clusters_listing_with_no_etcd_result(self):
        """
        Verify listing clusters handles no etcd result properly.
        """
        self.datasource.get.side_effect = etcd.EtcdKeyNotFound

        body = self.simulate_request('/api/v0/clusters')
        # datasource's get should have been called once
        self.assertEquals(1, self.datasource.get.call_count)
        self.assertEqual(self.srmock.status, falcon.HTTP_404)
        self.assertEqual('{}', body[0])
