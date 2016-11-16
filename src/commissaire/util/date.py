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
Date/Time related utilities.
"""

import datetime

from commissaire import constants as C


def now():
    """
    Returns the date and time right now.

    :returns: The date and time right now.
    :rtype: datetime.datetime
    """
    return datetime.datetime.utcnow()


def formatted_dt(dt=None):
    """
    Returns the date and time in the format expected by all components.

    :param dt: Optional datetime to format.
    :type dt: datetime.datetime
    :returns: The date and time in the expected format.
    :rtype: str
    """
    if dt is None:
        dt = now()
    return datetime.datetime.strftime(dt, C.DATE_FORMAT)
