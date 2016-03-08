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
Abstraction of commands that change across operating systems.
"""


class OSCmdBase:
    """
    Operating system command abstraction.
    """

    #: The type of Operating System
    os_type = None
    #: Full path to docker configuration file
    docker_config = '/etc/sysconfig/docker'
    #: Full path to the flanneld configuration file
    flanneld_config = '/etc/sysconfig/flanneld'
    #: Full path to kubernetes configuration file
    kubernetes_config = '/etc/kubernetes/config'
    #: Full path to kubernetes kubeconfig file
    kubernetes_kubeconfig = '/var/lib/kubelet/kubeconfig'
    #: Full path to kubelet configuration file
    kubelet_config = '/etc/kubernetes/kubelet'

    #: Docker service name
    docker_service = 'docker'
    #: Flannel service name
    flannel_service = 'flanneld'
    #: Kubernetes kubelet service name
    kubelet_service = 'kubelet'
    #: Kubernetes kube-proxy service name
    kubelet_proxy_service = 'kube-proxy'

    @classmethod
    def restart(cls):
        """
        Restart command. Must be overriden.

        :return: The command to execute as a list
        :rtype: list
        """
        raise NotImplementedError(
            '{0}.restart() must be overriden.'.format(cls.__name__))

    @classmethod
    def upgrade(cls):
        """
        Upgrade command. Must be overriden.

        :return: The command to execute as a list
        :rtype: list
        """
        raise NotImplementedError(
            '{0}.upgrade() must be overriden.'.format(cls.__name__))

    @classmethod
    def install_libselinux_python(cls):
        """
        Install libselinux_python command. Must be overriden.

        :return: The command to execute as a list
        :rtype: list
        """
        raise NotImplementedError(
            '{0}.install_libselinux_python() must be overriden.'.format(
                cls.__name__))

    @classmethod
    def install_docker(cls):
        """
        Install Docker command. Must be overriden.

        :return: The command to execute as a list
        :rtype: list
        """
        raise NotImplementedError(
            '{0}.install_docker() must be overriden.'.format(cls.__name__))

    @classmethod
    def install_flannel(cls):
        """
        Install Flannel command. Must be overriden.

        :return: The command to execute as a list
        :rtype: list
        """
        raise NotImplementedError(
            '{0}.install_flannel() must be overriden.'.format(cls.__name__))

    @classmethod
    def install_kube(cls):
        """
        Install Kube command. Must be overriden.

        :return: The command to execute as a list
        :rtype: list
        """
        raise NotImplementedError(
            '{0}.install_kube() must be overriden.'.format(cls.__name__))


def get_oscmd(os_type):
    """
    Returns the proper OSCmd class based on os_type.

    :param os_type: The type of OS: EX: fedora
    :type os_type: string
    :return: The proper OSCmd class.
    :rtype: commissaire.oscmd.OSCmdBase
    """
    try:
        return getattr(__import__(
            'commissaire.oscmd.{0}'.format(os_type),
            fromlist=['True']), 'OSCmd')
    except ImportError:
        # TODO: Make this a specific exception
        raise Exception('No OSCmd class for {0}'.format(os_type))
