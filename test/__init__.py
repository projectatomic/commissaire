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

import os
import unittest

from commissaire.models import Model

# Keep this list synchronized with oscmd modules.
available_os_types = ('fedora', 'redhat', 'rhel', 'centos')

def get_fixture_file_path(filename):
    """
    Attempts to return the path to a fixture file.

    :param filename: The name of the file to look for.
    :type filename: str
    :returns: Full path to the file
    :rtype: str
    :raises: Exception
    """
    for x in ('.', '..'):
        try:
            a_path = os.path.sep.join((x, filename))
            os.stat(a_path)
            return os.path.realpath(a_path)
        except:
            pass
    raise Exception(
        'Can not find path for config: {0}'.format(filename))


class TestCase(unittest.TestCase):
    """
    Parent class for all unittests.
    """
    pass


class TestModel(Model):
    """
    Simple model type for use in test cases.
    """
    _json_type = dict
    _attribute_map = {
        'foo': {'type': str}
    }
    _attribute_defaults = {'foo': ''}
    _primary_key = 'foo'
