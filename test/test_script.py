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
Test cases for the commissaire.script module.
"""

import falcon
import etcd

from . import TestCase
from argparse import Namespace
from mock import MagicMock
from commissaire import script


class Test_CreateApp(TestCase):
    """
    Tests for the create_app function.
    """

    def test_create_app(self):
        """
        Verify cli_etcd_or_default works with cli input.
        """
        store = MagicMock(get=MagicMock(side_effect=etcd.EtcdKeyNotFound))
        app = script.create_app(store)
        self.assertTrue(isinstance(app, falcon.API))
        self.assertEquals(2, len(app._middleware))


class Test_CliEtcdOrDefault(TestCase):
    """
    Tests for the cli_etcd_or_default function.
    """

    def test_cli_etcd_or_default_with_cli_input(self):
        """
        Verify cli_etcd_or_default works with cli input.
        """
        cli = Namespace(test=['test'])
        ds = MagicMock(get=MagicMock(side_effect=etcd.EtcdKeyNotFound))
        self.assertEquals(
            'test',
            script.cli_etcd_or_default('test', cli.test, 'default', ds))

    def test_cli_etcd_or_default_with_default_fallback(self):
        """
        Verify cli_etcd_or_default falls to default with no other input.
        """
        cli = Namespace(test=None)
        ds = MagicMock(get=MagicMock(side_effect=etcd.EtcdKeyNotFound))
        self.assertEquals(
            'default',
            script.cli_etcd_or_default('test', cli.test, 'default', ds))

    def test_cli_etcd_or_default_with_etcd_result(self):
        """
        Verify cli_etcd_or_default uses etcd result when present.
        """
        cli = Namespace(test=None)
        ds = MagicMock(
            get=MagicMock(return_value=MagicMock(value='frometcd')))
        self.assertEquals(
            'frometcd',
            script.cli_etcd_or_default('test', cli.test, 'default', ds))
