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
The clusterexec job.
"""

import cherrypy
import datetime
import etcd
import json
import logging
import tempfile

from commissaire.transport import ansibleapi
from commissaire.compat.b64 import base64
from commissaire.oscmd import get_oscmd


def clusterexec(cluster_name, command):
    """
    Remote executes a shell commands across a cluster.

    :param store: Data store to place results.
    :type store: etcd.Client
    """
    logger = logging.getLogger('clusterexec')

    # TODO: This is a hack and should really be done elsewhere
    if command == 'upgrade':
        finished_hosts_key = 'upgraded'
        cluster_status = {
            "status": 'in_process',
            "upgrade_to": 'latest',
            "upgraded": [],
            "in_process": [],
            "started_at": datetime.datetime.utcnow().isoformat(),
            "finished_at": None,
        }
    elif command == 'restart':
        finished_hosts_key = 'restarted'
        cluster_status = {
            "status": 'in_process',
            "restarted": [],
            "in_process": [],
            "started_at": datetime.datetime.utcnow().isoformat(),
            "finished_at": None
        }

    end_status = 'finished'

    # Set the initial status in the store
    logger.info('Setting initial status.')
    logger.debug('Status={0}'.format(cluster_status))
    cherrypy.engine.publish(
        'store-save',
        '/commissaire/cluster/{0}/{1}'.format(cluster_name, command),
        json.dumps(cluster_status))[0]

    # Collect all host addresses in the cluster
    etcd_resp, error = cherrypy.engine.publish(
        'store-get', '/commissaire/clusters/{0}'.format(cluster_name))[0]

    if error:
        logger.warn(
            'Unable to continue for {0} due to '
            '{1}: {2}. Returning...'.format(cluster_name, type(error), error))
        return

    cluster_hosts = set(json.loads(etcd_resp.value).get('hostset', []))
    if cluster_hosts:
        logger.debug(
            '{0} hosts in cluster {1}'.format(
                len(cluster_hosts), cluster_name))
    else:
        logger.warn('No hosts in cluster {0}'.format(cluster_name))

    # TODO: Find better way to do this
    a_hosts, error = cherrypy.engine.publish(
        'store-get', '/commissaire/hosts')[0]
    if error:
        logger.warn(
            'No hosts in the cluster. Error: {0}. Exiting clusterexec'.format(
                error))
        return
    for a_host_dict in a_hosts._children:
        a_host = json.loads(a_host_dict['value'])
        if a_host['address'] not in cluster_hosts:
            logger.debug(
                'Skipping {0} as it is not in this cluster.'.format(
                    a_host['address']))
            continue  # Move on to the next one
        oscmd = get_oscmd(a_host['os'])

        command_list = getattr(oscmd, command)()  # Only used for logging
        logger.info('Executing {0} on {1}...'.format(
            command_list, a_host['address']))

        cluster_status['in_process'].append(a_host['address'])
        cherrypy.engine.publish(
            'store-set',
            '/commissaire/cluster/{0}/{1}'.format(cluster_name, command),
            json.dumps(cluster_status))

        # TODO: This is reused, make it reusable
        f = tempfile.NamedTemporaryFile(prefix='key', delete=False)
        key_file = f.name
        logger.debug(
            'Using {0} as the temporary key location for {1}'.format(
                key_file, a_host['address']))
        f.write(base64.decodestring(a_host['ssh_priv_key']))
        logger.debug('Wrote key for {0}'.format(a_host['address']))
        f.close()

        transport = ansibleapi.Transport()
        exe = getattr(transport, command)
        result, facts = exe(
            a_host['address'], key_file, oscmd)
        try:
            f.unlink(key_file)
            logger.debug('Removed temporary key file {0}'.format(key_file))
        except:
            logger.warn(
                'Unable to remove the temporary key file: {0}'.format(
                    key_file))

        # If there was a failure set the end_status and break out
        if result != 0:
            end_status = 'failed'
            break

        cluster_status[finished_hosts_key].append(a_host['address'])
        try:
            idx = cluster_status['in_process'].index(a_host['address'])
            cluster_status['in_process'].pop(idx)
        except ValueError:
            logger.warn('Host {0} was not in_process for {1} {2}'.format(
                a_host['address'], command, cluster_name))

        cherrypy.engine.publish(
            'store-set',
            '/commissaire/cluster/{0}/{1}'.format(cluster_name, command),
            json.dumps(cluster_status))[0]
        logger.info('Finished executing {0} for {1} in {2}'.format(
            command, a_host['address'], cluster_name))

    # Final set of command result
    cluster_status['finished_at'] = datetime.datetime.utcnow().isoformat()
    cluster_status['status'] = end_status

    cherrypy.engine.publish(
        'store-set',
        '/commissaire/cluster/{0}/{1}'.format(cluster_name, command),
        json.dumps(cluster_status))[0]

    logger.info('Clusterexec stopping')
