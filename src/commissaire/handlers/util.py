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
import cherrypy
import falcon
import json

from commissaire.queues import INVESTIGATE_QUEUE
from commissaire.handlers.models import Cluster, Host


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


def etcd_cluster_exists(name):
    """
    Returns whether a cluster with the given name exists.

    :param name: Name of a cluster
    :type name: str
    """
    key = etcd_cluster_key(name)

    etcd_resp, error = cherrypy.engine.publish('store-get', key)[0]
    if not error:
        return True
    return False


def etcd_cluster_has_host(name, address):
    """
    Checks if a host address belongs to a cluster with the given name.
    If no such cluster exists, the function raises KeyError.

    :param name: Name of a cluster
    :type name: str
    :param address: Host address
    :type address: str
    """
    cluster = get_cluster_model(name)
    if not cluster:
        raise KeyError

    return address in cluster.hostset


def etcd_cluster_add_host(name, address):
    """
    Adds a host address to a cluster with the given name.
    If no such cluster exists, the function raises KeyError.

    Note the function is idempotent: if the host address is
    already in the cluster, no change occurs.

    :param name: Name of a cluster
    :type name: str
    :param address: Host address to add
    :type address: str
    """
    cluster = get_cluster_model(name)
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

    etcd_resp, _ = cherrypy.engine.publish(
        'store-save',
        cluster.etcd.key,
        cluster.to_json(secure=True),
        prevValue=cluster.etcd.value)[0]


def etcd_cluster_remove_host(name, address):
    """
    Removes a host address from a cluster with the given name.
    If no such cluster exists, the function raises KeyError.

    Note the function is idempotent: if the host address is
    not in the cluster, no change occurs.


    :param name: Name of a cluster
    :type name: str
    :param address: Host address to remove
    :type address: str
    """
    cluster = get_cluster_model(name)
    if not cluster:
        raise KeyError

    # FIXME: Should guard against races here, since we're fetching
    #        the cluster record and writing it back with some parts
    #        unmodified.  Use either locking or a conditional write
    #        with the etcd 'modifiedIndex'.  Deferring for now.

    if address in cluster.hostset:
        cluster.hostset.remove(address)
        cherrypy.engine.publish(
            'store-save',
            cluster.etcd.key,
            cluster.to_json(secure=True))[0]


def get_cluster_model(name):
    """
    Returns a Cluster instance from the etcd record for the given
    cluster name, if it exists, or else None.

    For convenience, the EtcdResult is embedded in the Cluster instance
    as an 'etcd' property.

    :param name: Name of a cluster
    :type name: str
    """
    key = etcd_cluster_key(name)
    etcd_resp, error = cherrypy.engine.publish('store-get', key)[0]

    if error:
        return None

    cluster = Cluster(**json.loads(etcd_resp.value))
    cluster.etcd = etcd_resp
    return cluster


def etcd_host_create(address, ssh_priv_key, cluster_name=None):
    """
    Creates a new host record in etcd and optionally adds the host to
    the specified cluster.  Returns a (status, host) tuple where status
    is the Falcon HTTP status and host is a Host model instance, which
    may be None if an error occurred.

    This function is idempotent so long as the host parameters agree
    with an existing host record and cluster membership.

    :param address: Host address.
    :type address: str
    :param ssh_priv_key: Host's SSH key, base64-encoded.
    :type ssh_priv_key: str
    :param cluster_name: Name of the cluster to join, or None
    :type cluster_name: str or None
    :return: (status, host)
    :rtype: tuple
    """
    key = etcd_host_key(address)
    etcd_resp, error = cherrypy.engine.publish('store-get', key)[0]

    if not error:
        # Check if the request conflicts with the existing host.
        existing_host = Host(**json.loads(etcd_resp.value))
        if existing_host.ssh_priv_key != ssh_priv_key:
            return (falcon.HTTP_409, None)
        if cluster_name:
            try:
                assert etcd_cluster_has_host(cluster_name, address)
            except (AssertionError, KeyError):
                return (falcon.HTTP_409, None)

        # Request is compatible with the existing host, so
        # we're done.  (Not using HTTP_201 since we didn't
        # actually create anything.)
        return (falcon.HTTP_200, existing_host)

    host_creation = {
        'address': address,
        'ssh_priv_key': ssh_priv_key,
        'os': '',
        'status': 'investigating',
        'cpus': -1,
        'memory': -1,
        'space': -1,
        'last_check': None
    }

    # Verify the cluster exists, if given.  Do it now
    # so we can fail before writing anything to etcd.
    if cluster_name:
        if not etcd_cluster_exists(cluster_name):
            return (falcon.HTTP_409, None)

    host = Host(**host_creation)

    new_host, _ = cherrypy.engine.publish(
        'store-save', key, host.to_json(secure=True))[0]

    # Add host to the requested cluster.
    if cluster_name:
        etcd_cluster_add_host(cluster_name, address)

    INVESTIGATE_QUEUE.put((host_creation, ssh_priv_key))

    return (falcon.HTTP_201, Host(**json.loads(new_host.value)))
