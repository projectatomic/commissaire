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
Test cases for the commissaire.authentication module.
"""

import falcon

from . import TestCase
from falcon.testing.helpers import create_environ
from commissaire import authentication


class Test_Authenticator(TestCase):
    """
    Tests for the Authenticator class.
    """

    def before(self):
        """
        Sets up a fresh instance of the class before each run.
        """
        self.authenticator = authentication.Authenticator()

    def test_authenticator_process_request(self):
        """
        Verify Authenticator's process_request calls authenticate.
        """
        self.assertRaises(
            falcon.HTTPForbidden,
            self.authenticator.process_request,
            falcon.Request(create_environ()),
            falcon.Response())
