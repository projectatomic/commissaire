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
"""

from gevent.monkey import patch_all
patch_all()

import datetime
import base64
import json
import logging
import logging.config

import etcd
import falcon
import gevent

from gevent.pywsgi import WSGIServer

from commissaire.handlers.clusters import (
    ClustersResource, ClusterResource,
    ClusterHostsResource, ClusterSingleHostResource,
    ClusterRestartResource, ClusterUpgradeResource)
from commissaire.handlers.hosts import HostsResource, HostResource
from commissaire.handlers.status import StatusResource
from commissaire.queues import INVESTIGATE_QUEUE
from commissaire.jobs import POOLS
from commissaire.jobs.investigator import investigator
from commissaire.authentication import httpauth
from commissaire.middleware import JSONify


# TODO: Move greenlet funcs to their own module


'''
def host_watcher(q, c):  # pragma: no cover
    logger = logging.getLogger('watcher')
    next_idx = None
    logger.info('Starting watcher from latest index')
    while True:
        try:
            change = c.watch('/testing/hosts/', index=next_idx, recursive=True)
            logger.debug('Got change {0}'.format(change))
            next_idx = change.etcd_index + 1
            logger.debug('Last index: {0}. Next index: {1}'.format(
                change.etcd_index, next_idx))
            q.put(change)
        except etcd.EtcdWatchTimedOut:
            logger.debug('Etcd timeout. re-watching...')


# TODO: multiprocess?
def router(q):  # pragma: no cover
    logger = logging.getLogger('router')
    logger.info('Starting router')
    while True:
        sent_to = 0
        change = q.get()
        logger.debug('Got change {0}'.format(change))
        for all_q in QUEUES['ALL']:
            sent_to += 1
            all_q.put(change)

        logger.debug('Change for {0} is a "{1}"'.format(
            change.etcd_index, change.action))
        if change.action == 'delete':
            address = json.loads(change._prev_node.value)['address']
        else:
            try:
                data = json.loads(change.value)
                address = data['address']
            except TypeError:
                logger.debug('Empty value. Setting to "{0}".')
                data = {}

        if address in QUEUES.keys():
            for found_q in QUEUES[address]:
                sent_to += 1
                found_q.put(change)
                logging.debug('Sent change for {0} to queue for {1}'.format(
                    change.etcd_index, address))

        logger.info('Sent change for {0} to {1} queues.'.format(
            change.etcd_index, sent_to))

'''


def create_app(store):
    """
    Creates a new WSGI compliant commissaire application.

    :param store: The etcd client to for storing/retrieving data.
    :type store: etcd.Client
    :returns: The commissaire application.
    :rtype: falcon.API
    """
    # TODO: Make this configurable
    try:
        http_auth = httpauth.HTTPBasicAuthByEtcd(store)
    except etcd.EtcdKeyNotFound:
        # TODO: Fall back to empty users file instead
        http_auth = httpauth.HTTPBasicAuthByFile('./conf/users.json')

    app = falcon.API(middleware=[http_auth, JSONify()])

    app.add_route('/api/v0/status', StatusResource(store, None))
    app.add_route('/api/v0/cluster/{name}', ClusterResource(store, None))
    app.add_route(
        '/api/v0/cluster/{name}/hosts',
        ClusterHostsResource(store, None))
    app.add_route(
        '/api/v0/cluster/{name}/hosts/{address}',
        ClusterSingleHostResource(store, None))
    app.add_route(
        '/api/v0/cluster/{name}/restart',
        ClusterRestartResource(store, None))
    app.add_route(
        '/api/v0/cluster/{name}/upgrade',
        ClusterUpgradeResource(store, None))
    app.add_route('/api/v0/clusters', ClustersResource(store, None))
    app.add_route('/api/v0/host/{address}', HostResource(store, None))
    app.add_route('/api/v0/hosts', HostsResource(store, None))
    return app


def cli_etcd_or_default(name, cli, default, ds):
    """
    Returns the value for an option in the following order:
    CLI switch, etcd value, default.

    :param name: The name of the switch/etcd key.
    :type name: str
    :param cli: The argparse value.
    :type cli: list
    :param default: The default value if CLI and etcd have no values.
    :param ds: Etcd client
    :type ds: etcd.Client
    """
    result = None
    if cli:
        result = cli[0]
        logging.info('Using CLI for {0} configuration.'.format(name))
    else:
        try:
            result = ds.get('/commissaire/config/{0}'.format(name)).value
            logging.info('Using Etcd for {0} configuration.'.format(name))
        except etcd.EtcdKeyNotFound:
            logging.info(
                'No CLI or etcd defined for {0}.'
                ' Using default of {1}.'.format(name, default))
            result = default
    return result


def main():  # pragma: no cover
    """
    Main script entry point.
    """
    import argparse
    import urlparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--listen-interface', '-i', type=str, help='Interface to listen on')
    parser.add_argument(
        '--listen-port', '-p', type=int, help='Port to listen on')
    parser.add_argument(
        'etcd_uri', type=str, nargs=1, help='Full URI for etcd')
    args = parser.parse_args()

    try:
        etcd_uri = urlparse.urlparse(args.etcd_uri[0])
        # Verify we have what we need
        if None in (etcd_uri.port, etcd_uri.hostname, etcd_uri.scheme):
            raise Exception
    except:
        parser.error(
            'You must provide a full etcd URI. EX: http://127.0.0.1:2379')

    ds = etcd.Client(host=etcd_uri.hostname, port=etcd_uri.port)

    try:
        logging.config.dictConfig(
            json.loads(ds.get('/commissaire/config/logger').value))
        logging.info('Using Etcd for logging configuration.')
    except etcd.EtcdKeyNotFound:
        with open('./conf/logger.json', 'r') as logging_default_cfg:
            logging.config.dictConfig(json.loads(logging_default_cfg.read()))
            logging.warn('No logger configuration in Etcd. Using defaults.')
    except etcd.EtcdConnectionFailed as ecf:
        err = 'Unable to connect to Etcd: {0}. Exiting ...'.format(ecf)
        logging.fatal(err)
        parser.error('{0}\n'.format(err))
        raise SystemExit(1)

    interface = cli_etcd_or_default(
        'listeninterface', args.listen_interface, '0.0.0.0', ds)
    port = cli_etcd_or_default('listenport', args.listen_port, 8000, ds)

    POOLS['investigator'].spawn(investigator, INVESTIGATE_QUEUE, ds)
    # watch_thread = gevent.spawn(host_watcher, ROUTER_QUEUE, ds)
    # router_thread = gevent.spawn(router, ROUTER_QUEUE)

    app = create_app(ds)
    try:
        WSGIServer((interface, int(port)), app).serve_forever()
    except KeyboardInterrupt:
        pass

    POOLS['investigator'].kill()
    # watch_thread.kill()
    # router_thread.kill()


if __name__ == '__main__':  # pragma: no cover
    main()
