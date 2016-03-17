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
Test cases for the commissaire.handlers.status module.
"""

import json
import mock

import etcd
import falcon

from . import TestCase
from mock import MagicMock
from commissaire.handlers import status
from commissaire.middleware import JSONify
from commissaire.jobs import PROCS


class Test_Status(TestCase):
    """
    Tests for the Status model.
    """

    def test_status_creation(self):
        """
        Verify Status model.
        """
        # Make sure status has required inputs
        self.assertRaises(
            TypeError,
            status.Status
        )

        # Make sure a Cluster is accepted as expected
        status_model = status.Status(
            etcd={}, investigator={})
        self.assertEquals(type(str()), type(status_model.to_json()))


class Test_StatusResource(TestCase):
    """
    Tests for the Status resource.
    """
    astatus = ('{"etcd": {"status": "OK"}, "investigator": {"status": '
               '"OK", "info": {"size": 1, "in_use": 1, "errors": []}}}')

    def before(self):
        self.api = falcon.API(middleware=[JSONify()])
        self.datasource = etcd.Client()
        self.return_value = MagicMock(etcd.EtcdResult)
        self.datasource.get = MagicMock(name='get')
        self.datasource.get.return_value = self.return_value
        self.resource = status.StatusResource(self.datasource)
        self.api.add_route('/api/v0/status', self.resource)

    def test_status_retrieve(self):
        """
        Verify retrieving Status.
        """
        with mock.patch('cherrypy.engine.publish') as _publish:
            child = MagicMock(value='')
            self.return_value._children = [child]
            self.return_value.leaves = self.return_value._children
            _publish.return_value = [[self.return_value, None]]

            for proc in ('investigator', ):
                PROCS[proc] = MagicMock(
                    'multiprocessing.Process',
                    is_alive=MagicMock(return_value=True),
                )

            body = self.simulate_request('/api/v0/status')
            self.assertEqual(self.srmock.status, falcon.HTTP_200)
            self.assertEqual(
                json.loads(self.astatus),
                json.loads(body[0]))
