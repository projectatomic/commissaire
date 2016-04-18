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
Test cases for the commissaire.compat.exception module.
"""

from . import TestCase
from commissaire.compat import exception


class Test_raise_if_not(TestCase):
    """
    Tests for the commissaire.compat.exception.raise_if_not function.
    """

    def test_raise_if_not(self):
        """
        Verify raise_if_not raises only when it should.
        """
        # Verify raised when not whitelisted
        for x in (ValueError, [ValueError, KeyError]):
            self.assertRaises(TypeError, exception.raise_if_not, x)

        # Verify we get exception information when it is whitelisted
        for x in (ValueError, [ValueError, KeyError]):
            try:
                raise ValueError('test')
            except:
                exc_type, exc, _ = exception.raise_if_not(x)
                self.assertEquals(exc_type, ValueError)
                self.assertTrue(isinstance(exc, ValueError))
                self.assertEquals('test', exc.args[0])
