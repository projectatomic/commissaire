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
Constants for test cases.
"""

import copy
import json

from commissaire.models import Host, HostCreds


def make_new(instance):
    """
    Returns a new deep copy of an instance.
    """
    return copy.deepcopy(instance)


#: Response JSON for a single host
HOST_JSON = (
    '{"address": "10.2.0.2",'
    ' "status": "available", "os": "fedora",'
    ' "cpus": 2, "memory": 11989228, "space": 487652,'
    ' "last_check": "2015-12-17T15:48:18.710454"}')
#: Host model for most tests
HOST = Host.new(
    **json.loads(HOST_JSON))
#: HostCreds model for most tests
HOST_CREDS = HostCreds.new(
    address=HOST.address,
    ssh_priv_key='dGVzdAo=',
    remote_user='root'
)
