# Copyright (C) 2016  Red Hat, Inc
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
Test cases for the commissaire.jobs.clusterexec module.
"""

import contextlib
import etcd
import mock
import cherrypy

from . import TestCase
from commissaire.jobs.clusterexec import clusterexec
from commissaire.config import Config
from commissaire.compat.urlparser import urlparse
from mock import MagicMock


cherrypy.config['commissaire.config'] = Config(
    etcd={'uri': urlparse('http://127.0.0.1:2379')})


class Test_JobsClusterExec(TestCase):
    """
    Tests for the clusterexec job.
    """

    etcd_host = ('{"address": "10.2.0.2", "ssh_priv_key": "dGVzdAo=",'
                 ' "status": "available", "os": "atomic",'
                 ' "cpus": 2, "memory": 11989228, "space": 487652,'
                 ' "last_check": "2015-12-17T15:48:18.710454", '
                 '"cluster": "default"}')

    etcd_cluster = '{"status": "ok", "hostset": ["10.2.0.2"]}'

    def test_clusterexec(self):
        """
        Verify the clusterexec.
        """
        for cmd in ('restart', 'upgrade'):
            with contextlib.nested(
                    mock.patch('cherrypy.engine.publish'),
                    mock.patch('commissaire.transport.ansibleapi.Transport'),
                    mock.patch('etcd.Client')) as (_publish, _tp, _store):
                getattr(_tp(), cmd).return_value = (0, {})

                child = {'value': self.etcd_host}
                return_value = MagicMock(_children=[child])
                return_value.leaves = return_value._children

                # store = _store()
                # store.get = MagicMock('get')
                # store.get.side_effect = (
                _publish.side_effect = (
                    [[MagicMock(value=self.etcd_cluster), None]],
                    [[MagicMock(value=self.etcd_cluster), None]],
                    [[return_value, None]],
                    [[return_value, None]],
                    [[return_value, None]],
                    [[return_value, None]],
                    [[return_value, None]],
                )

                clusterexec('default', cmd)

                # One for the cluster, one for the host
                self.assertEquals(6, _publish.call_count)
'''
    def test_clusterexec_stops_on_failure(self):
        """
        Verify the clusterexec will stop on first failure.
        """
        for cmd in ('restart', 'upgrade'):
            with contextlib.nested(
                    mock.patch('cherrypy.engine.publish'),
                    mock.patch('commissaire.transport.ansibleapi.Transport'),
                    mock.patch('etcd.Client')) as (_publish, _tp, _store):
                getattr(_tp(), cmd).return_value = (1, {})

                child = {'value': self.etcd_host}
                return_value = MagicMock(_children=[child])
                return_value.leaves = return_value._children

                store = _store()
                store.get = MagicMock('get')
                store.get.side_effect = (
                    MagicMock(value=self.etcd_cluster), return_value)
                store.set = MagicMock('set')

                clusterexec('default', cmd)

                # One for the cluster, one for the host
                self.assertEquals(2, store.get.call_count)
                # We should have 4 sets for 1 host
                self.assertEquals(3, store.set.call_count)
'''