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
Test cases for the commissaire.handlers.hosts module.
"""

import json

import etcd
import falcon

from . import TestCase
from mock import MagicMock
from commissaire.handlers import hosts
from commissaire.middleware import JSONify


class Test_Hosts(TestCase):
    """
    Tests for the Hosts model.
    """

    def test_hosts_creation(self):
        """
        Verify Hosts model.
        """
        # Make sure hosts is required
        self.assertRaises(
            TypeError,
            hosts.Hosts
        )

        # Make sure an empty Hosts is still valid
        hosts_model = hosts.Hosts(hosts=[])
        self.assertEquals(
            '[]',
            hosts_model.to_json())

        # Make sure a Host is accepted as expected
        hosts_model = hosts.Hosts(
            hosts=[hosts.Host(
                ssh_priv_key='dGVzdAo=',
                address='127.0.0.1',
                status='status',
                os='atomic',
                cpus=4,
                memory=12345,
                space=67890,
                last_check='2016-01-07T15:09:29.944101')])
        self.assertEquals(1, len(hosts_model.hosts))
        self.assertEquals(type(str()), type(hosts_model.to_json()))

        # Make sure other instances are not accepted
        hosts_model = hosts.Hosts(hosts=[object()])


class Test_HostsResource(TestCase):
    """
    Tests for the Hosts Resource.
    """
    # TODO: This test could use some work

    ahost = ('{"address": "10.2.0.2",'
             ' "status": "available", "os": "atomic",'
             ' "cpus": 2, "memory": 11989228, "space": 487652,'
             ' "last_check": "2015-12-17T15:48:18.710454"}')

    etcd_host = ('{"address": "10.2.0.2", "ssh_priv_key": "dGVzdAo=",'
                 ' "status": "available", "os": "atomic",'
                 ' "cpus": 2, "memory": 11989228, "space": 487652,'
                 ' "last_check": "2015-12-17T15:48:18.710454"}')

    def before(self):
        self.api = falcon.API(middleware = [JSONify()])
        self.datasource = etcd.Client()
        self.return_value = MagicMock(etcd.EtcdResult)
        self.datasource.get = MagicMock(name='get')
        self.datasource.get.return_value = self.return_value
        self.resource = hosts.HostsResource(self.datasource)
        self.api.add_route('/api/v0/hosts', self.resource)

    def test_hosts_listing(self):
        """
        Verify listing Hosts.
        """
        child = MagicMock(value=self.etcd_host)
        self.return_value._children = [child]
        self.return_value.leaves = self.return_value._children

        body = self.simulate_request('/api/v0/hosts')
        # datasource's get should have been called once
        self.assertEquals(1, self.datasource.get.call_count)
        self.assertEqual(self.srmock.status, falcon.HTTP_200)
        self.assertEqual(
            [json.loads(self.ahost)],
            json.loads(body[0]))

    def test_hosts_listing_with_no_hosts(self):
        """
        Verify listing Hosts when no hosts exists.
        """
        self.return_value._children = []
        self.return_value.leaves = self.return_value._children

        body = self.simulate_request('/api/v0/hosts')
        # datasource's get should have been called once
        self.assertEquals(1, self.datasource.get.call_count)
        self.assertEqual(self.srmock.status, falcon.HTTP_200)
        self.assertEqual({}, json.loads(body[0]))

    def test_hosts_listing_with_no_etcd_result(self):
        """
        Verify listing hosts handles no etcd result properly.
        """
        self.datasource.get.side_effect = etcd.EtcdKeyNotFound

        body = self.simulate_request('/api/v0/hosts')
        # datasource's get should have been called once
        self.assertEquals(1, self.datasource.get.call_count)
        self.assertEqual(self.srmock.status, falcon.HTTP_404)
        self.assertEqual('{}', body[0])


class Test_Host(TestCase):
    """
    Tests for the Host model.
    """

    def test_host_creation(self):
        """
        Verify host model
        """
        # Make sure it requires data
        self.assertRaises(
            TypeError,
            hosts.Host
        )

        # Make sure a Host creates expected results
        host_model = hosts.Host(
            ssh_priv_key='dGVzdAo=',
            address='127.0.0.1',
            status='status',
            os='atomic',
            cpus=4,
            memory=12345,
            space=67890,
            last_check='2016-01-07T15:09:29.944101')
        self.assertEquals(type(str()), type(host_model.to_json()))


class Test_HostResource(TestCase):
    """
    Tests for the Host Resource.
    """
    # TODO: This test could use some work

    ahost = ('{"address": "10.2.0.2",'
             ' "status": "available", "os": "atomic",'
             ' "cpus": 2, "memory": 11989228, "space": 487652,'
             ' "last_check": "2015-12-17T15:48:18.710454"}')

    etcd_host = ('{"address": "10.2.0.2", "ssh_priv_key": "dGVzdAo=",'
                 ' "status": "available", "os": "atomic",'
                 ' "cpus": 2, "memory": 11989228, "space": 487652,'
                 ' "last_check": "2015-12-17T15:48:18.710454"}')

    def before(self):
        self.api = falcon.API(middleware = [JSONify()])
        self.datasource = etcd.Client()
        self.return_value = MagicMock(etcd.EtcdResult)
        self.datasource.get = MagicMock(name='get')
        self.datasource.get.return_value = self.return_value
        self.datasource.delete = MagicMock(name='delete')
        self.datasource.delete.return_value = self.return_value
        self.datasource.set = MagicMock(name='set')
        self.datasource.set.return_value = self.return_value
        self.resource = hosts.HostResource(self.datasource)
        self.api.add_route('/api/v0/host/{address}', self.resource)

    def test_host_retrieve(self):
        """
        Verify retrieving a Host.
        """
        # Verify if the host exists the data is returned
        self.return_value.value = self.etcd_host

        body = self.simulate_request('/api/v0/host/10.2.0.2')
        # datasource's get should have been called once
        self.assertEquals(1, self.datasource.get.call_count)
        self.assertEqual(self.srmock.status, falcon.HTTP_200)
        self.assertEqual(
            json.loads(self.ahost),
            json.loads(body[0]))

        # Verify no host returns the proper result
        self.datasource.get.reset_mock()
        self.datasource.get.side_effect = etcd.EtcdKeyNotFound

        body = self.simulate_request('/api/v0/host/10.9.9.9')
        self.assertEquals(1, self.datasource.get.call_count)
        self.assertEqual(self.srmock.status, falcon.HTTP_404)
        self.assertEqual({}, json.loads(body[0]))

    def test_host_delete(self):
        """
        Verify deleting a Host.
        """

        clusters_return_value = MagicMock(
            etcd.EtcdResult, leaves=[],
            value={'value': None}, _children=[])
        # First call return is etcd_host, second is the clusters_return_value
        self.datasource.get.side_effect = (
            MagicMock(value=self.etcd_host), clusters_return_value)

        # Verify deleting of an existing host works
        body = self.simulate_request('/api/v0/host/10.2.0.2', method='DELETE')
        # datasource's delete should have been called once
        self.assertEquals(1, self.datasource.delete.call_count)
        self.assertEqual(self.srmock.status, falcon.HTTP_410)
        self.assertEqual({}, json.loads(body[0]))

        # Verify deleting of a non existing host returns the proper result
        self.datasource.delete.reset_mock()
        self.datasource.delete.side_effect = etcd.EtcdKeyNotFound
        body = self.simulate_request('/api/v0/host/10.9.9.9', method='DELETE')
        self.assertEquals(1, self.datasource.delete.call_count)
        self.assertEqual(self.srmock.status, falcon.HTTP_404)
        self.assertEqual({}, json.loads(body[0]))

    def test_host_create(self):
        """
        Verify creation of a Host.
        """
        self.datasource.get.side_effect = etcd.EtcdKeyNotFound
        self.return_value.value = self.etcd_host
        data = '{"address": "10.2.0.2", "ssh_priv_key": "dGVzdAo=", "cluster": "testing"}'
        body = self.simulate_request(
            '/api/v0/host/10.2.0.2', method='PUT', body=data)
        # datasource's set should have been called once
        self.assertEquals(1, self.datasource.set.call_count)
        self.assertEqual(self.srmock.status, falcon.HTTP_201)
        self.assertEqual(json.loads(self.ahost), json.loads(body[0]))

        # Make sure that if the host exists creation doesn't happen
        self.datasource.get.side_effect = None
        self.datasource.get.reset_mock()
        self.datasource.set.reset_mock()
        body = self.simulate_request(
            '/api/v0/host/10.2.0.2', method='PUT', body=data)
        # datasource's set should not have been called once
        self.assertEquals(0, self.datasource.set.call_count)
        self.assertEqual(self.srmock.status, falcon.HTTP_409)
        self.assertEqual({}, json.loads(body[0]))
