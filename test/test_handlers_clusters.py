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
from mock import MagicMock
from commissaire.handlers import clusters
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
        Verify listing Clusters.
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

    def test_clusters_listing_with_no_clusters(self):
        """
        Verify listing Clusters when no clusters exist.
        """
        self.return_value._children = []
        self.return_value.leaves = self.return_value._children

        body = self.simulate_request('/api/v0/clusters')
        # datasource's get should have been called once
        self.assertEquals(1, self.datasource.get.call_count)
        self.assertEqual(self.srmock.status, falcon.HTTP_200)
        self.assertEqual({}, json.loads(body[0]))

    def test_clusters_listing_with_no_etcd_result(self):
        """
        Verify listing Clusters handles no etcd result properly.
        """
        self.datasource.get.side_effect = etcd.EtcdKeyNotFound

        body = self.simulate_request('/api/v0/clusters')
        # datasource's get should have been called once
        self.assertEquals(1, self.datasource.get.call_count)
        self.assertEqual(self.srmock.status, falcon.HTTP_404)
        self.assertEqual('{}', body[0])


class Test_Cluster(TestCase):
    """
    Tests for the Cluster model.
    """
    # XXX: Based on Test_Host

    def test_cluster_creation(self):
        """
        Verify cluster model.
        """
        # Make sure it requires data
        self.assertRaises(
            TypeError,
            clusters.Cluster)

        # Make sure a Cluster creates expected results
        cluster_model = clusters.Cluster(status='OK')
        self.assertEquals(type(str()), type(cluster_model.to_json()))
        self.assertIn('total', cluster_model.hosts)
        self.assertIn('available', cluster_model.hosts)
        self.assertIn('unavailable', cluster_model.hosts)


class Test_ClusterResource(TestCase):
    """
    Tests for the Cluster resource.
    """
    # Based on Test_HostResource

    acluster = ('{"status": "ok",'
                ' "hosts": {"total": 1,'
                '           "available": 1,'
                '           "unavailable":0}}')

    etcd_cluster = '{"status": "ok"}'

    def before(self):
        self.api = falcon.API(middleware=[JSONify()])
        self.datasource = etcd.Client()
        self.return_value = MagicMock(etcd.EtcdResult)
        self.datasource.get = MagicMock(name='get')
        self.datasource.get.return_value = self.return_value
        self.datasource.delete = MagicMock(name='delete')
        self.datasource.delete.return_value = self.return_value
        self.resource = clusters.ClusterResource(self.datasource)
        self.api.add_route('/api/v0/cluster/{name}', self.resource)

    def test_cluster_retrieve(self):
        """
        Verify retrieving a cluster.
        """
        # Verify if the cluster exists the data is returned
        self.return_value.value = self.etcd_cluster

        body = self.simulate_request('/api/v0/cluster/development')
        # datasource's get should have been called once
        self.assertEquals(1, self.datasource.get.call_count)
        self.assertEqual(self.srmock.status, falcon.HTTP_200)
        self.assertEqual(
            json.loads(self.acluster),
            json.loads(body[0]))

        # Verify no cluster returns the proper result
        self.datasource.get.reset_mock()
        self.datasource.get.side_effect = etcd.EtcdKeyNotFound

        body = self.simulate_request('/api/v0/cluster/bogus')
        self.assertEquals(1, self.datasource.get.call_count)
        self.assertEqual(self.srmock.status, falcon.HTTP_404)
        self.assertEqual({}, json.loads(body[0]))
