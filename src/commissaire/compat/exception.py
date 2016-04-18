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
Cross version exception grabber.
"""

import inspect
import sys


def raise_if_not(errors):
    """
    Re-raises an exception if it is not explicitly OK'd.

    :param errors: A single or list of Exception classes to catch.
    :type errors: Exception or list
    :returns: The output of sys.exc_info
    :rtype: tuple(type, Exception, Traceback)
    :rasies: Exception
    """
    exc_type, exc, tb = sys.exc_info()

    if inspect.isclass(errors):
        errors = [errors]

    for catch in errors:
        if issubclass(exc_type, catch):
            return exc_type, exc, tb

    raise exc
