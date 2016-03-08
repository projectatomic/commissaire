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
Atomic commands.
"""

from commissaire.oscmd import OSCmdBase


class OSCmd(OSCmdBase):
    """
    Commmands for Atomic.

    .. note::

       install_* methods return true since Atomic already has these
       packages as part of the OS and does not allow installing packages.

    .. todo::

       TODO: skip install_* commands for atomic via ansible playbook.
    """

    #: The type of Operating System
    os_type = 'atomic'

    @classmethod
    def restart(cls):
        """
        Atomic restart command.

        :return: The command to execute as a list
        :rtype: list
        """
        return ['systemctl', 'reboot']

    @classmethod
    def upgrade(cls):
        """
        Atomic upgrade command.

        :return: The command to execute as a list
        :rtype: list
        """
        return ['rpm-ostree', 'upgrade']

    @classmethod
    def install_libselinux_python(cls):
        """
        Faux Atomic install libselinux_python command.

        :return: The command to execute as a list
        :rtype: list
        """
        return ['true']

    @classmethod
    def install_docker(cls):
        """
        Faux Atomic install docker command.

        :return: The command to execute as a list
        :rtype: list
        """
        return ['true']

    @classmethod
    def install_flannel(cls):
        """
        Faux Atomic install flannel command.

        :return: The command to execute as a list
        :rtype: list
        """
        return ['true']

    @classmethod
    def install_kube(cls):
        """
        Faux Atomic install Kube command.

        :return: The command to execute as a list
        :rtype: list
        """
        return ['true']
