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
Test cases for the commissaire.authentication.httpauth module.
"""

import json

import etcd
import falcon

from . import TestCase
from falcon.testing.helpers import create_environ
from mock import MagicMock
from commissaire.handlers import hosts
from commissaire.script import create_app
from commissaire.middleware import JSONify


class Test_Hosts(TestCase):
    """
    Tests for the Hosts model.
    """

    def test_hosts_creation(self):
        """
        Verify hosts model
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

    ahost = ('{"address": "10.2.0.2", "status": "available", "os": "atomic",'
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
        Verify listing hosts.
        """
        child = MagicMock(value=self.ahost)
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
        Verify listing hosts.
        """
        child = MagicMock(value=self.ahost)
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
