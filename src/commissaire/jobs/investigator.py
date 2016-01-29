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
The investigator job.
"""

import datetime
import json
import logging
import tempfile

from commissaire.transport import ansibleapi
from commissaire.compat.b64 import base64


def investigator(queue, store, run_once=False):
    """
    Investigates new hosts to retrieve and store facts.

    :param queue: Queue to pull work from.
    :type queue: gevent.queue.Queue
    :param store: Data store to place results.
    :type store: etcd.Client
    """
    # TODO: Add coverage and testing.
    logger = logging.getLogger('investigator')
    logger.info('Investigator started')

    transport = ansibleapi.Transport()
    while True:
        to_investigate, ssh_priv_key = queue.get()
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

        key = '/commissaire/hosts/{0}'.format(address)
        data = json.loads(store.get(key).value)

        try:
            result, facts = transport.get_info(address, key_file)
            data.update(facts)
            data['last_check'] = datetime.datetime.utcnow().isoformat()
            data['status'] = 'bootstrapping'
            logger.info('Facts for {0} retrieved'.format(address))
        except:
            logger.warn('Getting info failed for {0}'.format(address))
            data['status'] = 'failed'
        finally:
            try:
                f.unlink(key_file)
                logger.debug('Removed temporary key file {0}'.format(key_file))
            except:
                logger.warn(
                    'Unable to remove the temporary key file: {0}'.format(
                        key_file))
        store.set(key, json.dumps(data))
        logging.debug('Finished investigation update for {0}: {1}'.format(
            address, data))
        logger.info(
            'Finished and stored investigation data for {0}'.format(address))

        if run_once:
            logger.info('Exiting due to run_once request.')
            break

    logger.info('Investigator stopping')
