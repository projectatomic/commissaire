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

from commissaire.handlers.hosts import HostsResource, HostResource
from commissaire.queues import *
from commissaire.authentication import httpauth
from commissaire.middleware import JSONify


# TODO: Move greenlet funcs to their own module
def investigator(q, c):  # pragma: no cover
    import tempfile
    from commissaire.transport import ansibleapi
    logger = logging.getLogger('investigator')
    logger.info('Investigator started')

    get_info = ansibleapi.Transport().get_info

    while True:
        to_investigate, ssh_priv_key = q.get()
        address = to_investigate['address']
        logger.info('Investigating {0}...'.format(address))
        logger.debug('Investigation details: key={0}, data={1}'.format(
            to_investigate, ssh_priv_key))

        f = tempfile.NamedTemporaryFile(prefix='key', delete=False)
        key_file = f.name
        logger.debug(
            'Using {0} as the temporary key location for {1}'.format(
                key_file, address))
        f.write(base64.decodestring(ssh_priv_key))
        logger.debug('Wrote key for {0}'.format(address))
        f.close()

        result, facts = get_info(address, key_file)
        try:
            f.unlink(key_file)
            logger.debug('Removed temporary key file {0}'.format(key_file))
        except:
            logger.warn(
                'Unable to remove the temporary key file: {0}'.format(
                    key_file))
        uri = '/commissaire/hosts/{0}'.format(address)
        data = json.loads(c.get(uri).value)
        data.update(facts)
        data['last_check'] = datetime.datetime.utcnow().isoformat()
        data['status'] = 'bootstrapping'
        logger.info('Facts for {0} retrieved'.format(address))

        c.set(uri, json.dumps(data))
        logging.debug('Investigation update for {0}: {1}'.format(
            address, data))
        logger.info(
            'Finished and stored investigation for {0}'.format(address))

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


def create_app(ds):  # pragma: no cover
    # TODO: Make this configurable
    try:
        http_auth = httpauth.HTTPBasicAuthByEtcd(ds)
    except etcd.EtcdKeyNotFound:
        # TODO: Fall back to empty users file instead
        http_auth = httpauth.HTTPBasicAuthByFile('./conf/users.json')

    app = falcon.API(middleware=[http_auth, JSONify()])

    app.add_route('/api/v0/host/{address}', HostResource(ds, None))
    app.add_route('/api/v0/hosts', HostsResource(ds, None))
    return app


def main():  # pragma: no cover
    import sys
    import urlparse

    # TODO: Use argparse
    try:
        etcd_uri = urlparse.urlparse(sys.argv[1])
    except:
        sys.stdout.write(
            'You must provide an etcd url. EX: http://127.0.0.1:2379\n')
        raise SystemExit(1)

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
        sys.stderr.write('{0}\n'.format(err))
        raise SystemExit(1)

    investigator_thread = gevent.spawn(investigator, INVESTIGATE_QUEUE, ds)
    # watch_thread = gevent.spawn(host_watcher, ROUTER_QUEUE, ds)
    # router_thread = gevent.spawn(router, ROUTER_QUEUE)

    app = create_app(ds)
    try:
        WSGIServer(('127.0.0.1', 8000), app).serve_forever()
    except KeyboardInterrupt:
        pass

    investigator_thread.kill()
    # watch_thread.kill()
    # router_thread.kill()


if __name__ == '__main__':  # pragma: no cover
    main()
