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

    def restart(self):
        """
        Restart command. Must be overriden.

        :return: The command to execute as a list
        :rtype: list
        """
        raise NotImplementedError('{0}.restart() must be overriden.'.format(
            self.__class__.__name__))

    def upgrade(self):
        """
        Upgrade command. Must be overriden.

        :return: The command to execute as a list
        :rtype: list
        """
        raise NotImplementedError('{0}.upgrade() must be overriden.'.format(
            self.__class__.__name__))


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
            fromlist=[True]), 'OSCmd')
    except ImportError:
        # TODO: Make this a specific exception
        raise Exception('No OSCmd class for {0}'.format(os_type))
