# Copyright (C) 2016  Red Hat, Inc
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
Utilities for SSH.
"""

import base64
import os
import sys
import tempfile


class TemporarySSHKey:
    """
    An abstraction for temporary ssh keys.
    """

    def __init__(self, host, logger):
        """
        Initializes an instance of the TemporarySSHKey class.

        :param host: Host to grab key data from.
        :type host: commissaire.handlers.models.Host
        :param logger: Logger to utilize.
        :type logger: logging.Logger
        """
        self._host = host
        self.logger = logger
        self.path = None

    def create(self):
        """
        Creates the temporary key.
        """
        with tempfile.NamedTemporaryFile(prefix='key', delete=False) as f:
            self.path = f.name
            self.logger.debug(
                'Using %s as the temporary key location for %s',
                self.path, self._host.address)
            input_bytes = bytes(self._host.ssh_priv_key, 'utf8')
            f.write(base64.decodestring(input_bytes))
            f.flush()
            self.logger.info('Wrote key for %s', self._host.address)

    def remove(self):
        """
        Removes the temporary key file.
        """
        try:
            os.unlink(self.path)
            self.logger.debug(
                'Removed temporary key file %s', self.path)
        except:
            exc_type, exc_msg, tb = sys.exc_info()
            self.logger.warn(
                'Unable to remove the temporary key file: '
                '%s. Exception: %s', self.path, exc_msg)

    def __enter__(self):
        """
        Executed upon the start of the context manager.
        """
        self.create()
        return self

    def __exit__(self, type, value, traceback):
        """
        Executed upon the exit of the context manager.
        """
        self.remove()
