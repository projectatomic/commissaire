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

import cherrypy
import datetime
import json
import logging
import os
import sys
import tempfile

from time import sleep

from commissaire.compat.b64 import base64
from commissaire.containermgr.kubernetes import KubeContainerManager
from commissaire.oscmd import get_oscmd
from commissaire.transport import ansibleapi


def clean_up_key(key_file):
    """
    Remove the key file.

    :param key_file: Full path to the key_file
    :type key_file: str
    """
    logger = logging.getLogger('investigator')
    try:
        os.unlink(key_file)
        logger.debug('Removed temporary key file {0}'.format(key_file))
    except:
        exc_type, exc_msg, tb = sys.exc_info()
        logger.warn(
            'Unable to remove the temporary key file: '
            '{0}. Exception:{1}'.format(key_file, exc_msg))


def investigator(queue, config, run_once=False):
    """
    Investigates new hosts to retrieve and store facts.

    :param queue: Queue to pull work from.
    :type queue: Queue.Queue
    :param config: Configuration information.
    :type config: commissaire.config.Config
    """
    logger = logging.getLogger('investigator')
    logger.info('Investigator started')

    while True:
        # Statuses follow:
        # http://commissaire.readthedocs.org/en/latest/enums.html#host-statuses
        transport = ansibleapi.Transport()
        to_investigate, ssh_priv_key = queue.get()
        address = to_investigate['address']
        logger.info('{0} is now in investigating.'.format(address))
        logger.debug('Investigation details: key={0}, data={1}'.format(
            to_investigate, ssh_priv_key))

        f = tempfile.NamedTemporaryFile(prefix='key', delete=False)
        key_file = f.name
        logger.debug(
            'Using {0} as the temporary key location for {1}'.format(
                key_file, address))
        f.write(base64.decodestring(ssh_priv_key))
        logger.info('Wrote key for {0}'.format(address))
        f.close()

        key = '/commissaire/hosts/{0}'.format(address)
        etcd_resp, error = cherrypy.engine.publish('store-get', key)[0]
        if error:
            logger.warn(
                'Unable to continue for {0} due to '
                '{1}: {2}. Returning...'.format(address, type(error), error))
            clean_up_key(key_file)
            continue

        data = json.loads(etcd_resp.value)

        try:
            result, facts = transport.get_info(address, key_file)
            data.update(facts)
            data['last_check'] = datetime.datetime.utcnow().isoformat()
            data['status'] = 'bootstrapping'
            logger.info('Facts for {0} retrieved'.format(address))
            logger.debug('Data: {0}'.format(data))
        except:
            exc_type, exc_msg, tb = sys.exc_info()
            logger.warn('Getting info failed for {0}: {1}'.format(
                address, exc_msg))
            data['status'] = 'failed'
            cherrypy.engine.publish('store-save', key, json.dumps(data))[0]
            clean_up_key(key_file)
            if run_once:
                break
            continue

        cherrypy.engine.publish('store-save', key, json.dumps(data))[0]
        logger.info(
            'Finished and stored investigation data for {0}'.format(address))
        logger.debug('Finished investigation update for {0}: {1}'.format(
            address, data))

        logger.info('{0} is now in bootstrapping'.format(address))
        oscmd = get_oscmd(data['os'])
        try:
            result, facts = transport.bootstrap(
                address, key_file, config, oscmd)
            data['status'] = 'inactive'
            cherrypy.engine.publish('store-save', key, json.dumps(data))[0]
        except:
            exc_type, exc_msg, tb = sys.exc_info()
            logger.warn('Unable to start bootstraping for {0}: {1}'.format(
                address, exc_msg))
            data['status'] = 'disassociated'
            cherrypy.engine.publish('store-save', key, json.dumps(data))[0]
            clean_up_key(key_file)
            if run_once:
                break
            continue

        # Verify association with the container manager
        try:
            container_mgr = KubeContainerManager(config)
            # Try 3 times waiting 5 seconds each time before giving up
            for cnt in range(0, 3):
                if container_mgr.node_registered(address):
                    logger.info(
                        '{0} has been registered with the container manager.')
                    data['status'] = 'active'
                    break
                if cnt == 3:
                    msg = 'Could not register with the container manager'
                    logger.warn(msg)
                    raise Exception(msg)
                logger.debug(
                    '{0} has not been registered with the container manager. '
                    'Checking again in 5 seconds...'.format(address))
                sleep(5)
        except:
            _, exc_msg, _ = sys.exc_info()
            logger.warn(
                'Unable to finish bootstrap for {0} while associating with '
                'the container manager: {1}'.format(address, exc_msg))
            data['status'] = 'inactive'

        cherrypy.engine.publish('store-save', key, json.dumps(data))[0]
        logger.info(
            'Finished bootstrapping for {0}'.format(address))
        logging.debug('Finished bootstrapping for {0}: {1}'.format(
            address, data))

        clean_up_key(key_file)
        if run_once:
            logger.info('Exiting due to run_once request.')
            break

    logger.info('Investigator stopping')
