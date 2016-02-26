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
    """

    #: The type of Operating System
    os_type = 'atomic'

    def restart(self):
        """
        Atomic restart command.

        :return: The command to execute as a list
        :rtype: list
        """
        return ['systemctl', 'reboot']

    def upgrade(self):
        """
        Atomic upgrade command.

        :return: The command to execute as a list
        :rtype: list
        """
        return ['rpm-ostree', 'upgrade']

    def install_libselinux_python(self):
        """
        Atomic install libselinux_python command.

        :return: The command to execute as a list
        :rtype: list
        """
        return ['true']

    def install_docker(self):
        """
        Atomic install docker command.

        :return: The command to execute as a list
        :rtype: list
        """
        return ['true']

    def start_docker(self):
        """
        Atomic start docker command..

        :return: The command to execute as a list
        :rtype: list
        """
        return ['systemctl', 'start', 'docker']

    def install_flannel(self):
        """
        Atomic install flannel command.

        :return: The command to execute as a list
        :rtype: list
        """
        return ['true']

    def start_flannel(self):
        """
        Atomic start flannel command..

        :return: The command to execute as a list
        :rtype: list
        """
        return ['systemctl', 'start', 'flanneld']

    def install_kube(self):
        """
        Atomic install Kube command.

        :return: The command to execute as a list
        :rtype: list
        """
        return ['true']

    def start_kube(self):
        """
        Atomic start kube command.

        :return: The command to execute as a list
        :rtype: list
        """
        return ['systemctl', 'start', 'kubelet']

    def start_kube_proxy(self):
        """
        Atomic start Kube Proxy command.

        :return: The command to execute as a list
        :rtype: list
        """
        return ['systemctl', 'start', 'kube-proxy']
