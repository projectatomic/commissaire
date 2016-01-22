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
Test cases for the commissaire.oscmd module.
"""

from . import TestCase
from commissaire import oscmd


class Test_OSCmdBase(TestCase):
    """
    Tests for the OSCmdBase class.
    """

    def before(self):
        """
        Sets up a fresh instance of the class before each run.
        """
        self.instance = oscmd.OSCmdBase()

    def test_oscmd_base_reboot_raises(self):
        """
        Verify OSCmdBase's raises on reboot.
        """
        self.assertRaises(
            NotImplementedError,
            self.instance.reboot)

    def test_oscmd_base_upgrade_raises(self):
        """
        Verify OSCmdBase's raises on upgrade.
        """
        self.assertRaises(
            NotImplementedError,
            self.instance.upgrade)


class Test_get_oscmd(TestCase):

    def test_get_oscmd_with_valid_os_types(self):
        """
        Verify get_oscmd returns proper modules.
        """
        for os_type in ('atomic', 'fedora', 'rhel'):
            self.assertEquals(
                'commissaire.oscmd.{0}'.format(os_type),
                oscmd.get_oscmd(os_type).__module__)

    def test_get_oscmd_with_invalid_os_types(self):
        """
        Verify get_oscmd errors when the os_type does not exist.
        """

        self.assertRaises(Exception, oscmd.get_oscmd, 'not_a_real_os_type')
