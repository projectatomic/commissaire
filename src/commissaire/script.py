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
import os

import etcd
import falcon
import gevent

from gevent.pywsgi import WSGIServer, LoggingLogAdapter, socket

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


def create_app(
        store,
        users_paths=('/etc/commissaire/users.json', './conf/users.json')):
    """
    Creates a new WSGI compliant commissaire application.

    :param store: The etcd client to for storing/retrieving data.
    :type store: etcd.Client
    :param users_paths: Path(s) to where the users.json can be found.
    :type users_paths: str or iterable
    :returns: The commissaire application.
    :rtype: falcon.API
    """
    try:
        http_auth = httpauth.HTTPBasicAuthByEtcd(store)
    except etcd.EtcdKeyNotFound:
        if not hasattr(users_paths, '__iter__'):
            users_paths = [users_paths]
        http_auth = None
        for user_path in users_paths:
            if os.path.isfile(user_path):
                http_auth = httpauth.HTTPBasicAuthByFile(user_path)
        if http_auth is None:
            raise Exception('User configuration must be set in Etcd '
                            'or on the file system ({0}).'.format(users_paths))

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
    parser.add_argument(
        '--tls-keyfile', type=str, required=False,
        help='Full path to the TLS keyfile')
    parser.add_argument(
        '--tls-certfile', type=str, required=False,
        help='Full path to the TLS certfile')

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
        found_logger_config = False
        for logger_path in (
                '/etc/commissaire/logger.json', './conf/logger.json'):
            if os.path.isfile(logger_path):
                with open(logger_path, 'r') as logging_default_cfg:
                    logging.config.dictConfig(
                        json.loads(logging_default_cfg.read()))
                    found_logger_config = True
                logging.warn('No logger configuration in Etcd. Using defaults '
                             'at {0}'.format(logger_path))
        if not found_logger_config:
            parser.error(
                'Unable to find any logging configuration. Exiting ...')
    except etcd.EtcdConnectionFailed:
        _, ecf, _ = exception.raise_if_not(etcd.EtcdConnectionFailed)
        err = 'Unable to connect to Etcd: {0}. Exiting ...'.format(ecf)
        logging.fatal(err)
        parser.error('{0}\n'.format(err))
        raise SystemExit(1)

    # TLS options
    ssl_args = {}
    tls_keyfile = cli_etcd_or_default(
        'tlskeyfile', args.tls_keyfile, None, ds)
    tls_certfile = cli_etcd_or_default(
        'tlscertfile', args.tls_certfile, None, ds)
    if tls_keyfile is not None and tls_certfile is not None:
        ssl_args = {
            'keyfile': tls_keyfile,
            'certfile': tls_certfile,
        }
        logging.info('TLS will be enabled.')
    elif tls_keyfile is not None or tls_certfile is not None:
        parser.error(
            'Both a keyfile and certfile must be given for TLS. Exiting ...')

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

    app = create_app(ds)
    try:
        access_logger = logging.getLogger('http-access')
        error_logger = logging.getLogger('http-error')
        kwargs = {
            'listener': (interface, int(port)),
            'application': app,
            'log': LoggingLogAdapter(access_logger, access_logger.level),
            'error_log': LoggingLogAdapter(error_logger, error_logger.level),
        }
        kwargs.update(ssl_args)
        logging.debug('WSGIServer args: {0}'.format(kwargs))

        server = WSGIServer(**kwargs)

        # Catch SIGTERM and stop the server.
        gevent.signal.signal(
            gevent.signal._signal.SIGTERM, lambda s, f: server.stop())
        server.serve_forever()
    except socket.error:
        _, ex, _ = exception.raise_if_not(socket.error)
        logging.fatal(ex)
    except KeyboardInterrupt:
        pass

    PROCS['investigator'].terminate()
    PROCS['investigator'].join()


if __name__ == '__main__':  # pragma: no cover
    main()
