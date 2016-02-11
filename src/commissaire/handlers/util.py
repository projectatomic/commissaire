# Copyright (C) 2016  Red Hat, Inc
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
Resource utilities.
"""

import etcd
import json

from commissaire.handlers.models import Cluster


def etcd_host_key(address):
    """
    Returns the etcd key for the given host address.

    :param address: Address of a host
    :type address: str
    """
    return '/commissaire/hosts/{0}'.format(address)


def etcd_cluster_key(name):
    """
    Returns the etcd key for the given cluster name.

    :param name: Name of a cluster
    :type name: str
    """
    return '/commissaire/clusters/{0}'.format(name)


def etcd_cluster_exists(resource, name):
    """
    Returns whether a cluster with the given name exists.

    :param resource: A Resource instance
    :type resource: commissaire.resource.Resource
    :param name: Name of a cluster
    :type name: str
    """
    key = etcd_cluster_key(name)
    try:
        resource.store.get(key)
        return True
    except etcd.EtcdKeyNotFound:
        return False


def etcd_cluster_has_host(resource, name, address):
    """
    Checks if a host address belongs to a cluster with the given name.
    If no such cluster exists, the function raises KeyError.

    :param resource: A Resource instance
    :type resource: commissaire.resource.Resource
    :param name: Name of a cluster
    :type name: str
    :param address: Host address
    :type address: str
    """
    cluster = get_cluster_model(resource, name)
    if not cluster:
        raise KeyError

    return address in cluster.hostset


def etcd_cluster_add_host(resource, name, address):
    """
    Adds a host address to a cluster with the given name.
    If no such cluster exists, the function raises KeyError.

    Note the function is idempotent: if the host address is
    already in the cluster, no change occurs.

    :param resource: A Resource instance
    :type resource: commissaire.resource.Resource
    :param name: Name of a cluster
    :type name: str
    :param address: Host address to add
    :type address: str
    """
    cluster = get_cluster_model(resource, name)
    if not cluster:
        raise KeyError

    # FIXME: Need input validation.
    #        - Does the host exist at /commissaire/hosts/{IP}?
    #        - Does the host already belong to another cluster?

    # FIXME: Should guard against races here, since we're fetching
    #        the cluster record and writing it back with some parts
    #        unmodified.  Use either locking or a conditional write
    #        with the etcd 'modifiedIndex'.  Deferring for now.

    if address not in cluster.hostset:
        cluster.hostset.append(address)
        resource.store.set(cluster.etcd.key, cluster.to_json(secure=True))


def etcd_cluster_remove_host(resource, name, address):
    """
    Removes a host address from a cluster with the given name.
    If no such cluster exists, the function raises KeyError.

    Note the function is idempotent: if the host address is
    not in the cluster, no change occurs.

    :param resource: A Resource instance
    :type resource: commissaire.resource.Resource
    :param name: Name of a cluster
    :type name: str
    :param address: Host address to remove
    :type address: str
    """
    cluster = get_cluster_model(resource, name)
    if not cluster:
        raise KeyError

    # FIXME: Should guard against races here, since we're fetching
    #        the cluster record and writing it back with some parts
    #        unmodified.  Use either locking or a conditional write
    #        with the etcd 'modifiedIndex'.  Deferring for now.

    if address in cluster.hostset:
        cluster.hostset.remove(address)
        resource.store.set(cluster.etcd.key, cluster.to_json(secure=True))


def get_cluster_model(resource, name):
    """
    Returns a Cluster instance from the etcd record for the given
    cluster name, if it exists, or else None.

    For convenience, the EtcdResult is embedded in the Cluster instance
    as an 'etcd' property.

    :param resource: A Resource instance
    :type resource: commissaire.resource.Resource
    :param name: Name of a cluster
    :type name: str
    """
    key = etcd_cluster_key(name)
    try:
        etcd_resp = resource.store.get(key)
        resource.logger.info(
            'Request for cluster {0}.'.format(name))
        resource.logger.debug('{0}'.format(etcd_resp))
    except etcd.EtcdKeyNotFound:
        resource.logger.info(
            'Request for non-existent cluster {0}.'.format(name))
        return None
    cluster = Cluster(**json.loads(etcd_resp.value))
    cluster.etcd = etcd_resp
    return cluster
