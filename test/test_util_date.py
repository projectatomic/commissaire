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
Test cases for the commissaire.util.date module.
"""

from unittest import mock

from . import TestCase

from commissaire.util import date


#: datetime instance to use in tests
DT = date.datetime.datetime.utcnow()
#: isoformat of DT used in tests
ISOFORMAT = DT.isoformat()


class Test_now(TestCase):
    """
    Tests the now function.
    """

    def test_now(self):
        """
        Test the now function.
        """
        with mock.patch('datetime.datetime') as _dt:
            _dt.utcnow.return_value = DT
            self.assertEquals(DT, date.now())


class Test_formatted_dt(TestCase):
    """
    Tests the formatted_dt function.
    """

    def test_formatted_dt(self):
        """
        Test the formatted_dt function with no input.
        """
        with mock.patch('datetime.datetime') as _dt:
            _dt.utcnow.return_value = DT
            _dt.strftime.return_value = ISOFORMAT
            self.assertEquals(ISOFORMAT, date.formatted_dt())

    def test_formatted_dt_with_datetime(self):
        """
        Test the formatted_dt function with a datetime.
        """
        with mock.patch('datetime.datetime') as _dt:
            _dt.utcnow.return_value = DT
            _dt.strftime.return_value = ISOFORMAT
            self.assertEquals(ISOFORMAT, date.formatted_dt(DT))
