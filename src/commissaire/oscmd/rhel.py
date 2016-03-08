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

from commissaire.oscmd.fedora import OSCmd as OSCmdBase


class OSCmd(OSCmdBase):
    """
    Commmands for RHEL.
    """

    #: The type of Operating System
    os_type = 'rhel'

    @classmethod
    def upgrade(cls):
        """
        RHEL upgrade command.

        :return: The command to execute as a list
        :rtype: list
        """
        return ['yum', 'update', '-y']

    @classmethod
    def install_libselinux_python(cls):
        """
        RHEL install libselinux_python command.

        :return: The command to execute as a list
        :rtype: list
        """
        return ['yum', 'install', '-y', 'libselinux-python']

    @classmethod
    def install_docker(cls):
        """
        RHEL install Docker command.

        :return: The command to execute as a list
        :rtype: list
        """
        return ['yum', 'install', '-y', 'docker']

    @classmethod
    def install_kube(cls):
        """
        RHEL start Kube command.

        :return: The command to execute as a list
        :rtype: list
        """
        return ['yum', 'install', '-y', 'kubernetes-node']

    @classmethod
    def install_flannel(cls):
        """
        Atomic install flannel command.

        :return: The command to execute as a list
        :rtype: list
        """
        return ['yum', 'install', '-y', 'flannel']
