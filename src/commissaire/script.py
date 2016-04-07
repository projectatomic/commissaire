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

import cherrypy
import json
import logging
import logging.config
import os

import etcd
import falcon

from commissaire.compat.urlparser import urlparse
from commissaire.compat import exception
from commissaire.config import Config, cli_etcd_or_default
from commissaire.handlers.clusters import (
    ClustersResource, ClusterResource,
    ClusterHostsResource, ClusterSingleHostResource,
    ClusterRestartResource, ClusterUpgradeResource)
from commissaire.handlers.hosts import (
    HostsResource, HostResource, ImplicitHostResource)
from commissaire.handlers.status import StatusResource
from commissaire.queues import INVESTIGATE_QUEUE
from commissaire.jobs import PROCS
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
        http_auth = httpauth.HTTPBasicAuthByEtcd()
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
    app.add_route('/api/v0/host', ImplicitHostResource(store, None))
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
    from commissaire.cherrypy_plugins import CherryPyStorePlugin
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
        '--etcd-cert-path', '-C', type=str, required=False,
        help='Full path to the client side certificate.')
    parser.add_argument(
        '--etcd-cert-key-path', '-K', type=str, required=False,
        help='Full path to the client side certificate key.')
    parser.add_argument(
        '--etcd-ca-path', '-A', type=str, required=False,
        help='Full path to the CA file.')
    parser.add_argument(
        '--kube-uri', '-k', type=str, required=True,
        help='Full URI for kubernetes EX: http://127.0.0.1:8080')
    parser.add_argument(
        '--tls-keyfile', type=str, required=False,
        help='Full path to the TLS keyfile for the commissaire server')
    parser.add_argument(
        '--tls-certfile', type=str, required=False,
        help='Full path to the TLS certfile for the commissaire server')

    args = parser.parse_args()

    try:
        config.etcd['uri'] = parse_uri(args.etcd_uri, 'etcd')
        config.kubernetes['uri'] = parse_uri(args.kube_uri, 'kube')
    except Exception:
        _, ex, _ = exception.raise_if_not(Exception)
        parser.error(ex)

    store_kwargs = {
        'host': config.etcd['uri'].hostname,
        'port': config.etcd['uri'].port,
        'protocol': config.etcd['uri'].scheme,
    }

    if bool(args.etcd_ca_path):
        config.etcd['certificate_ca_path'] = args.etcd_ca_path

    # We need all args to use a client side cert for etcd
    if bool(args.etcd_cert_path) ^ bool(args.etcd_cert_key_path):
        parser.error(
            'Both etcd-cert-path and etcd-cert-key-path must be '
            'provided to use a client side certificate with etcd.')
    elif bool(args.etcd_cert_path):
        if config.etcd['uri'].scheme != 'https':
            parser.error('An https URI is required when using '
                         'client side certificates.')
        store_kwargs['cert'] = (args.etcd_cert_path, args.etcd_cert_key_path)
        config.etcd['certificate_path'] = args.etcd_cert_path
        config.etcd['certificate_key_path'] = args.etcd_cert_key_path
        logging.info('Using client side certificate for etcd.')

    ds = etcd.Client(**store_kwargs)

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
    tls_keyfile = cli_etcd_or_default(
        'tlskeyfile', args.tls_keyfile, None, ds)
    tls_certfile = cli_etcd_or_default(
        'tlscertfile', args.tls_certfile, None, ds)

    interface = cli_etcd_or_default(
        'listeninterface', args.listen_interface, '0.0.0.0', ds)
    port = cli_etcd_or_default('listenport', args.listen_port, 8000, ds)

    # Pull options for accessing kubernetes
    try:
        config.kubernetes['token'] = ds.get(
            '/commissaire/config/kubetoken').value
        logging.info('Using kubetoken for kubernetes.')
    except etcd.EtcdKeyNotFound:
        logging.debug('No kubetoken set.')
    try:
        config.kubernetes['certificate_path'] = ds.get(
            '/commissaire/config/kube_certificate_path').value
        config.kubernetes['certificate_key_path'] = ds.get(
            '/commissaire/config/kube_certificate_key_path').value
        logging.info('Using client side certificate for kubernetes.')
    except etcd.EtcdKeyNotFound:
        logging.debug('No kubernetes client side certificate set.')

    # Add our config instance to the cherrypy global config so we can use it's
    # values elsewhere
    # TODO: Technically this should be in the cherrypy.request.app.config
    # but it looks like that isn't accessable with WSGI based apps
    cherrypy.config['commissaire.config'] = config

    logging.debug('Config: {0}'.format(config))

    cherrypy.server.unsubscribe()
    # Disable autoreloading and use our logger
    cherrypy.config.update({'log.screen': False,
                            'log.access_file': '',
                            'log.error_file': '',
                            'engine.autoreload.on': False})

    server = cherrypy._cpserver.Server()
    server.socket_host = interface
    server.socket_port = int(port)
    server.thread_pool = 10

    if bool(tls_keyfile) ^ bool(tls_certfile):
        parser.error(
            'Both a keyfile and certfile must be '
            'given for commissaire server TLS. Exiting ...')
    if tls_keyfile and tls_certfile:
        server.ssl_module = 'builtin'
        server.ssl_certificate = tls_certfile
        server.ssl_private_key = tls_keyfile
        logging.info('Commissaire server TLS will be enabled.')
    server.subscribe()

    # Add our plugins
    CherryPyStorePlugin(cherrypy.engine, store_kwargs).subscribe()
    # NOTE: Anything that requires etcd should start AFTER
    # the engine is started
    cherrypy.engine.start()

    # Start processes
    PROCS['investigator'] = Process(
        target=investigator, args=(INVESTIGATE_QUEUE, config))
    PROCS['investigator'].start()

    # Make and mount the app
    app = create_app(ds)
    cherrypy.tree.graft(app, "/")
    # Server forever
    cherrypy.engine.block()

    PROCS['investigator'].terminate()
    PROCS['investigator'].join()


if __name__ == '__main__':  # pragma: no cover
    main()
