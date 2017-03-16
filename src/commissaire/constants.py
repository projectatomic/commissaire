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
Constants for Commissaire.
"""

#: Flannel using etcd as it's configuration end
NETWORK_TYPE_FLANNEL_ETCD = 'flannel_etcd'
#: Flannel using a flannel server as it's configuration end
NETWORK_TYPE_FLANNEL_SERVER = 'flannel_server'
#: Network type to use if none is specified
NETWORK_TYPE_DEFAULT = NETWORK_TYPE_FLANNEL_ETCD
#: All network types
NETWORK_TYPES = [NETWORK_TYPE_FLANNEL_ETCD, NETWORK_TYPE_FLANNEL_SERVER]

#: Default network if non is provided
DEFAULT_CLUSTER_NETWORK_JSON = {
    'name': 'default',
    'type': NETWORK_TYPE_DEFAULT,
    'options': {},
}

#: Container Manager type for OpenShift
CONTAINER_MANAGER_OPENSHIFT = 'openshift'
#: Container Manager type to use when a default is required
CONTAINER_MANAGER_DEFAULT = CONTAINER_MANAGER_OPENSHIFT
#: All Container Manager types
CONTAINER_MANAGER_TYPES = [CONTAINER_MANAGER_OPENSHIFT]

# Default etcd configuration
# (server URL provided by store handler)
DEFAULT_ETCD_STORE_HANDLER = {
    'name': 'etcd',
    'models': ['*']
}

# Cluster Status Codes
CLUSTER_STATUS_OK = 'ok'
CLUSTER_STATUS_DEGRADED = 'degraded'
CLUSTER_STATUS_FAILED = 'failed'

# Host Statuses
HOST_STATUS_INVESTIGATING = 'investigating'
HOST_STATUS_BOOTSTRAPPING = 'bootstrapping'
HOST_STATUS_ACTIVE = 'active'
HOST_STATUS_FAILED = 'failed'

# JSONRPC error codes
JSONRPC_ERRORS = {
    'INVALID_JSON': -32700,
    'INVALID_REQUEST': -32600,
    'METHOD_NOT_FOUND': -32601,
    'INVALID_PARAMETERS': -32602,
    'INTERNAL_ERROR': -32603,

    # These map to Exception classes
    'STORAGE_LOOKUP_ERROR': -20000,
    'CONTAINER_MANAGER_ERROR': -20001,

    # Custom codes
    'NOT_FOUND': 404,
    'METHOD_NOT_ALLOWED': '405',
    'CONFLICT': 409,
}

#: Expected date format (isoformat)
DATE_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'
