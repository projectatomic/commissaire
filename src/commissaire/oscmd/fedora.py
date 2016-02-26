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
Fedora commands.
"""

from commissaire.oscmd import OSCmdBase


class OSCmd(OSCmdBase):
    """
    Commmands for Fedora.
    """

    #: The type of Operating System
    os_type = 'fedora'

    def restart(self):
        """
        Fedora restart command.

        :return: The command to execute as a list
        :rtype: list
        """
        return ['systemctl', 'reboot']

    def upgrade(self):
        """
        Fedora upgrade command.

        :return: The command to execute as a list
        :rtype: list
        """
        return ['dnf', 'update', '-y']

    def install_libselinux_python(self):
        """
        Fedora install libselinux_python command.

        :return: The command to execute as a list
        :rtype: list
        """
        return ['dnf', 'install', '-y', 'libselinux-python']

    def install_docker(self):
        """
        Fedora install docker command.

        :return: The command to execute as a list
        :rtype: list
        """
        return ['dnf', 'install', '-y', 'docker']

    def install_flannel(self):
        """
        Fedora install flannel command.

        :return: The command to execute as a list
        :rtype: list
        """
        return ['dnf', 'install', '-y', 'flannel']

    def install_kube(self):
        """
        Fedora install Kube command.

        :return: The command to execute as a list
        :rtype: list
        """
        return ['dnf', 'install', '-y', 'kubernetes-node']
