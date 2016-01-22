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
# along with this program.  If not, see <http://
"""
RHEL commands.
"""

from commissaire.oscmd import OSCmdBase


class OSCmd(OSCmdBase):
    """
    Commmands for RHEL.
    """

    #: The type of Operating System
    os_type = 'rhel'

    def reboot(self):
        """
        RHEL reboot command.

        :return: The command to execute as a list
        :rtype: list
        """
        return ['systemctl', 'reboot']

    def upgrade(self):
        """
        RHEL upgrade command.

        :return: The command to execute as a list
        :rtype: list
        """
        return ['yum', 'update', '-y']
