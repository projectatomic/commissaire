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
Test cases for the commissaire.oscmd module.
"""

from mock import MagicMock

from . import TestCase
from commissaire.compat.urlparser import urlparse
from commissaire.config import Config
from commissaire.containermgr.kubernetes import KubeContainerManager


class Test_KubeContainerManager(TestCase):
    """
    Tests for the KubeContainerManager class.
    """

    def test_node_registered(self):
        """
        Verify that KuberContainerManager().node_registered() works as expected.
        """
        config = Config(
            etcd={
                'uri': urlparse('http://127.0.0.1:2379'),
            },
            kubernetes={
                'uri': urlparse('http://127.0.0.1:8080'),
                'token': 'token',
            }
        )
        kube_container_mgr = KubeContainerManager(config)
        # First call should return True. The rest should be False.
        kube_container_mgr.con = MagicMock()
        kube_container_mgr.con.get = MagicMock(side_effect=(
            MagicMock(status_code=200),
            MagicMock(status_code=404),
            MagicMock(status_code=500)))

        self.assertTrue(kube_container_mgr.node_registered('test'))
        self.assertFalse(kube_container_mgr.node_registered('test'))
        self.assertFalse(kube_container_mgr.node_registered('test'))
