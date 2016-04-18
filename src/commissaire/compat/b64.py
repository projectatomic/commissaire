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
Returns the proper signature for base64 decoding based on Python version
"""

import base64 as _patched_b64

from commissaire.compat import __python_version__


if __python_version__ == '2':
    _patched_b64.decodebytes = _patched_b64.decodestring


#: Version of base64 which will work for Python 2 and 3
base64 = _patched_b64
