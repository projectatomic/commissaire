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

import json
import logging
import logging.config

import etcd
import falcon
import gevent

from gevent.queue import Queue, Empty
from gevent.pywsgi import WSGIServer

from commissaire.handlers.hosts import HostsResource, HostResource
from commissaire.authentication.httpauth import HTTPAuthByFile


ROUTER_QUEUE = Queue()
QUEUES = {
    "ALL": [Queue(), Queue()],
    "10.2.0.2": [Queue()],
}


def host_watcher(q, c):
    logger = logging.getLogger('watcher')
    next_idx = None
    logger.info('Starting watcher from latest index')
    while True:
        try:
            change = c.watch('/testing/hosts/', index=next_idx, recursive=True)
            logger.debug('Got change {}'.format(change))
            next_idx = change.etcd_index + 1
            logger.debug('Last index: {}. Next index: {}'.format(
                change.etcd_index, next_idx))
            q.put(change)
        except etcd.EtcdWatchTimedOut:
            logger.debug('Etcd timeout. re-watching...')


# TODO: multiprocess?
def router(q):
    logger = logging.getLogger('router')
    logger.info('Starting router')
    while True:
        sent_to = 0
        change = q.get()
        logger.debug('Got change {}'.format(change))
        for all_q in QUEUES['ALL']:
            sent_to += 1
            all_q.put(change)

        logger.debug('Change for {} is a "{}"'.format(
            change.etcd_index, change.action))
        if change.action == 'delete':
            address = json.loads(change._prev_node.value)['address']
        else:
            try:
                data = json.loads(change.value)
                address = data['address']
            except TypeError:
                logger.debug('Empty value. Setting to "{}".')
                data = {}

        if address in QUEUES.keys():
            for found_q in QUEUES[address]:
                sent_to += 1
                found_q.put(change)
                logging.debug('Sent change for {} to queue for {}'.format(
                    change.etcd_index, address))

        logger.info('Sent change for {} to {} queues.'.format(
            change.etcd_index, sent_to))


def main():
    import yaml
    from commissaire.middleware import JSONify
    # TODO: make the loading configurable
    logging.config.dictConfig(yaml.safe_load(open('./conf/logger.yaml', 'r')))

    ds = etcd.Client(port=2379)

    watch_thread = gevent.spawn(host_watcher, ROUTER_QUEUE, ds)
    router_thread = gevent.spawn(router, ROUTER_QUEUE)

    # TODO: make the loading configurable
    http_auth = HTTPAuthByFile('./conf/users.txt')
    app = falcon.API(middleware=[http_auth, JSONify()])

    # app.add_route('/streaming', HelloApp())
    app.add_route('/api/v0/hosts/{address}', HostResource(ds))
    app.add_route('/api/v0/hosts', HostsResource(ds, ROUTER_QUEUE))
    try:
        WSGIServer(('127.0.0.1', 8000), app).serve_forever()
    except KeyboardInterrupt:
        pass

    watch_thread.kill()
    router_thread.kill()


if __name__ == '__main__':
    main()
