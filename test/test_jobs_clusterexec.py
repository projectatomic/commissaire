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
Test cases for the commissaire.jobs.clusterexec module.
"""

import etcd
import mock

from . import TestCase
from commissaire.jobs.clusterexec import clusterexec
from mock import MagicMock


class Test_JobsClusterExec(TestCase):
    """
    Tests for the clusterexec job.
    """

    etcd_host = ('{"address": "10.2.0.2", "ssh_priv_key": "dGVzdAo=",'
                 ' "status": "available", "os": "atomic",'
                 ' "cpus": 2, "memory": 11989228, "space": 487652,'
                 ' "last_check": "2015-12-17T15:48:18.710454", '
                 '"cluster": "default"}')

    def test_clusterexec(self):
        """
        Verify the clusterexec.
        """
        for cmd in ('restart', 'upgrade'):
            with mock.patch('commissaire.transport.ansibleapi.Transport') as _tp:
                getattr(_tp(), cmd).return_value = (0, {})

                child = {'value': self.etcd_host}
                return_value = MagicMock(_children=[child])
                return_value.leaves = return_value._children

                store = etcd.Client()
                store.get = MagicMock('get')
                store.get.return_value = return_value
                store.set = MagicMock('set')

                clusterexec('default', cmd, store)

                self.assertEquals(1, store.get.call_count)
                # We should have 4 sets for 1 host
                self.assertEquals(4, store.set.call_count)

    def test_clusterexec_stops_on_failure(self):
        """
        Verify the clusterexec will stop on first failure.
        """
        for cmd in ('restart', 'upgrade'):
            with mock.patch('commissaire.transport.ansibleapi.Transport') as _tp:
                getattr(_tp(), cmd).return_value = (1, {})

                child = {'value': self.etcd_host}
                return_value = MagicMock(_children=[child])
                return_value.leaves = return_value._children

                store = etcd.Client()
                store.get = MagicMock('get')
                store.get.return_value = return_value
                store.set = MagicMock('set')

                clusterexec('default', cmd, store)

                self.assertEquals(1, store.get.call_count)
                # We should have 4 sets for 1 host
                self.assertEquals(3, store.set.call_count)
