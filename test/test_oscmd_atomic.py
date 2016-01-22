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
Test cases for the commissaire.oscmd.atomic module.
"""

from . import TestCase
from commissaire.oscmd import atomic


class Test_Atomic_OSCmd(TestCase):
    """
    Tests for the OSCmd class for Atomic.
    """

    def before(self):
        """
        Sets up a fresh instance of the class before each run.
        """
        self.instance = atomic.OSCmd()

    def test_atomic_oscmd_reboot(self):
        """
        Verify Atomic's OSCmd returns proper data on reboot.
        """
        cmd = self.instance.reboot()
        self.assertEquals(
            list,
            type(cmd))

    def test_atomic_oscmd_base_upgrade(self):
        """
        Verify Atomic's OSCmd returns proper data on upgrade.
        """
        cmd = self.instance.upgrade()
        self.assertEquals(
            list,
            type(cmd))
