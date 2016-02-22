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
patch_all(thread=False, socket=False)

import datetime
import base64
import json
import logging
import logging.config

import etcd
import falcon
import gevent

from gevent.pywsgi import WSGIServer, LoggingLogAdapter

from commissaire.compat.urlparser import urlparse
from commissaire.compat import exception
from commissaire.config import Config, cli_etcd_or_default
from commissaire.handlers.clusters import (
    ClustersResource, ClusterResource,
    ClusterHostsResource, ClusterSingleHostResource,
    ClusterRestartResource, ClusterUpgradeResource)
from commissaire.handlers.hosts import HostsResource, HostResource
from commissaire.handlers.status import StatusResource
from commissaire.queues import INVESTIGATE_QUEUE
from commissaire.jobs import POOLS, PROCS
from commissaire.jobs.investigator import investigator
from commissaire.authentication import httpauth
from commissaire.middleware import JSONify


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


def parse_uri(uri, name):
    """
    Parses and returns a parsed URI.

    :param uri: The URI to parse.
    :type uri: str
    :param name: The name to use for errors.
    :type name: str
    :returns: A parsed URI.
    :rtype: ParseResult
    :raises: Exception
    """
    parsed = urlparse(uri)
    # Verify we have what we need
    if not uri or None in (parsed.port, parsed.hostname, parsed.scheme):
        raise Exception(
            ('You must provide a full {0} URI. '
             'EX: http://127.0.0.1:2379'.format(name)))
    return parsed


def main():  # pragma: no cover
    """
    Main script entry point.
    """
    import argparse

    from multiprocessing import Process

    config = Config()

    epilog = ('Example: ./commissaire -e http://127.0.0.1:2379'
              ' -k http://127.0.0.1:8080')

    parser = argparse.ArgumentParser(epilog=epilog)
    parser.add_argument(
        '--listen-interface', '-i', type=str, help='Interface to listen on')
    parser.add_argument(
        '--listen-port', '-p', type=int, help='Port to listen on')
    parser.add_argument(
        '--etcd-uri', '-e', type=str, required=True,
        help='Full URI for etcd EX: http://127.0.0.1:2379')
    parser.add_argument(
        '--kube-uri', '-k', type=str, required=True,
        help='Full URI for kubernetes EX: http://127.0.0.1:8080')
    args = parser.parse_args()

    try:
        config.etcd['uri'] = parse_uri(args.etcd_uri, 'etcd')
        config.kubernetes['uri'] = parse_uri(args.kube_uri, 'kube')
    except Exception:
        _, ex, _ = exception.raise_if_not(Exception)
        parser.error(ex)

    ds = etcd.Client(
        host=config.etcd['uri'].hostname, port=config.etcd['uri'].port)

    try:
        logging.config.dictConfig(
            json.loads(ds.get('/commissaire/config/logger').value))
        logging.info('Using Etcd for logging configuration.')
    except etcd.EtcdKeyNotFound:
        with open('./conf/logger.json', 'r') as logging_default_cfg:
            logging.config.dictConfig(json.loads(logging_default_cfg.read()))
            logging.warn('No logger configuration in Etcd. Using defaults.')
    except etcd.EtcdConnectionFailed:
        _, ecf, _ = exception.raise_if_not(etcd.EtcdConnectionFailed)
        err = 'Unable to connect to Etcd: {0}. Exiting ...'.format(ecf)
        logging.fatal(err)
        parser.error('{0}\n'.format(err))
        raise SystemExit(1)

    interface = cli_etcd_or_default(
        'listeninterface', args.listen_interface, '0.0.0.0', ds)
    port = cli_etcd_or_default('listenport', args.listen_port, 8000, ds)
    config.etcd['listen'] = urlparse('http://{0}:{1}'.format(
        interface, port))

    try:
        config.kubernetes['token'] = ds.get(
            '/commissaire/config/kubetoken').value
        logging.debug('Config: {0}'.format(config))
        PROCS['investigator'] = Process(
            target=investigator, args=(INVESTIGATE_QUEUE, config, ds))
        PROCS['investigator'].start()
    except etcd.EtcdKeyNotFound:
        parser.error('"/commissaire/config/kubetoken" must be set in etcd!')
    # watch_thread = gevent.spawn(host_watcher, ROUTER_QUEUE, ds)
    # router_thread = gevent.spawn(router, ROUTER_QUEUE)

    app = create_app(ds)
    try:
        access_logger = logging.getLogger('http-access')
        error_logger = logging.getLogger('http-error')
        WSGIServer(
            listener=(interface, int(port)),
            application=app,
            log=LoggingLogAdapter(access_logger, access_logger.level),
            error_log=LoggingLogAdapter(error_logger, error_logger.level),
        ).serve_forever()
    except KeyboardInterrupt:
        pass

    PROCS['investigator'].terminate()
    PROCS['investigator'].join()


if __name__ == '__main__':  # pragma: no cover
    main()
