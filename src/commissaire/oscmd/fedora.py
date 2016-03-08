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

    @classmethod
    def restart(cls):
        """
        Fedora restart command.

        :return: The command to execute as a list
        :rtype: list
        """
        return ['systemctl', 'reboot']

    @classmethod
    def upgrade(cls):
        """
        Fedora upgrade command.

        :return: The command to execute as a list
        :rtype: list
        """
        return ['dnf', 'update', '-y']

    @classmethod
    def install_libselinux_python(cls):
        """
        Fedora install libselinux_python command.

        :return: The command to execute as a list
        :rtype: list
        """
        return ['dnf', 'install', '-y', 'libselinux-python']

    @classmethod
    def install_docker(cls):
        """
        Fedora install docker command.

        :return: The command to execute as a list
        :rtype: list
        """
        return ['dnf', 'install', '-y', 'docker']

    @classmethod
    def install_flannel(cls):
        """
        Fedora install flannel command.

        :return: The command to execute as a list
        :rtype: list
        """
        return ['dnf', 'install', '-y', 'flannel']

    @classmethod
    def install_kube(cls):
        """
        Fedora install Kube command.

        :return: The command to execute as a list
        :rtype: list
        """
        return ['dnf', 'install', '-y', 'kubernetes-node']
