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
Tests for util.ssh package.
"""

import logging
import os

from unittest import mock

from . import TestCase
from .constants import HOST, make_new
from commissaire.util.ssh import TemporarySSHKey


TEST_HOST = make_new(HOST)


class Test_TemporarySSHKey(TestCase):
    """
    Tests for the TemporarySSHKey class.
    """

    def test_temporarysshkey__init(self):
        """
        Verify init of TemporarySSHKey sets up the instances.
        """
        key = TemporarySSHKey(TEST_HOST, logging.getLogger())
        # There should be no path yet
        self.assertEquals(None, key.path)

    def test_temporarysshkey_create(self):
        """
        Verify create of TemporarySSHKey creates a new key.
        """
        key = TemporarySSHKey(TEST_HOST, logging.getLogger())
        key.create()
        self.assertTrue(os.path.isfile(key.path))
        os.unlink(key.path)

    def test_temporarysshkey_remove(self):
        """
        Verify TemporarySSHKey.remove successfully removes keys.
        """
        key = TemporarySSHKey(TEST_HOST, logging.getLogger())
        key.create()
        self.assertTrue(os.path.isfile(key.path))
        key.remove()
        self.assertFalse(os.path.isfile(key.path))

    def test_temporarysshkey_contextmanager(self):
        """
        Verify TemporarySSHKey can be used as a context manager.
        """
        with TemporarySSHKey(TEST_HOST, logging.getLogger()) as key:
            self.assertTrue(os.path.isfile(key.path))
        self.assertFalse(os.path.isfile(key.path))

    def test_temporarysshkey_remove_failure(self):
        """
        Verify TemporarySSHKey.remove reacts properly to failure.
        """
        mock_logger = mock.MagicMock(logging.Logger('test'))
        key = TemporarySSHKey(TEST_HOST, mock_logger)
        key.create()
        with mock.patch('os.unlink') as _unlink:
            _unlink.side_effect = Exception
            self.assertTrue(os.path.isfile(key.path))
            key.remove()
            self.assertTrue(os.path.isfile(key.path))
            # We should have a warning in the log
            mock_logger.warn.assert_called_once_with(mock.ANY)
        # Clean up the file
        key.remove()
