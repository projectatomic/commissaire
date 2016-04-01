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
Client CLI for commissaire.
"""

import argparse
import json
import os.path
import platform

import requests

# If we are on Python 2.x use raw_input as input
if platform.python_version_tuple()[0] == 2:
    input = raw_input


class ClientError(Exception):
    """
    Base exception for Client Errors.
    """
    pass


class Client(object):
    """
    Client for commissaire.
    """

    def __init__(self, conf):
        """
        Creates an instance of the Client.

        :param conf: Configuration dict
        :type conf: dict
        :returns: A Client instance
        :rtype: Client
        """
        self.endpoint = conf['endpoint']
        if self.endpoint.endswith('/'):
            self.endpoint = self.endpoint[:-1]
        self._con = requests.Session()
        self._con.headers['Content-Type'] = 'application/json'
        self._con.auth = (conf['username'], conf['password'])

    def _get(self, uri):
        """
        Shorthand for GETing.

        :param uri: The full uri to GET.
        :type uri: str
        :return: None on success, requests.Response on failure.
        :rtype: None or requests.Response
        """
        resp = self._con.get(uri)
        # Allow any 2xx code
        if resp.status_code > 199 and resp.status_code < 300:
            ret = resp.json()
            if ret:
                return ret
            return
        if resp.status_code == 403:
            raise ClientError('Username/Password was incorrect.')
        raise ClientError(
            'Unable to get the object at {0}: {1}'.format(
                uri, resp.status_code))

    def _put(self, uri, data={}):
        """
        Shorthand for PUTting.

        :param uri: The full uri to PUT.
        :type uri: str
        :param data: Optional dictionary to jsonify and PUT.
        :type data: dict
        :return: None on success, requests.Response of failure.
        :rtype: None or requests.Response
        """
        resp = self._con.put(uri, data=json.dumps(data))
        if resp.status_code == 201:
            ret = resp.json()
            if ret:
                return ret
            return ['Created']
        if resp.status_code == 403:
            raise ClientError('Username/Password was incorrect.')
        raise ClientError(
            'Unable to create an object at {0}: {1}'.format(
                uri, resp.status_code))

    def get_cluster(self, name, **kwargs):
        """
        Attempts to get cluster information.

        :param name: The name of the cluster
        :type name: str
        :param kwargs: Any other keyword arguments
        :type kwargs: dict
        """
        return self._get('{0}/api/v0/cluster/{1}'.format(self.endpoint, name))

    def create_cluster(self, name, **kwargs):
        """
        Attempts to create a cluster.

        :param name: The name of the cluster
        :type name: str
        :param kwargs: Any other keyword arguments
        :type kwargs: dict
        """
        uri = '{0}/api/v0/cluster/{1}'.format(self.endpoint, name)
        return self._put(uri)

    def get_restart(self, name, **kwargs):
        """
        Attempts to get a cluster restart.

        :param name: The name of the cluster
        :type name: str
        :param kwargs: Any other keyword arguments
        :type kwargs: dict
        """
        uri = '{0}/api/v0/cluster/{1}/restart'.format(self.endpoint, name)
        return self._get(uri)

    def create_restart(self, name, **kwargs):
        """
        Attempts to create a cluster restart.

        :param name: The name of the cluster
        :type name: str
        :param kwargs: Any other keyword arguments
        :type kwargs: dict
        """
        uri = '{0}/api/v0/cluster/{1}/restart'.format(self.endpoint, name)
        return self._put(uri)

    def get_upgrade(self, name, **kwargs):
        """
        Attempts to retrieve a cluster upgrade.

        :param name: The name of the cluster
        :type name: str
        :param kwargs: Any other keyword arguments
        :type kwargs: dict
        """
        uri = '{0}/api/v0/cluster/{1}/upgrade'.format(self.endpoint, name)
        return self._get(uri)

    def create_upgrade(self, name, **kwargs):
        """
        Attempts to create a cluster upgrade.

        :param name: The name of the cluster
        :type name: str
        :param kwargs: Any other keyword arguments
        :type kwargs: dict
        """
        uri = '{0}/api/v0/cluster/{1}/upgrade'.format(self.endpoint, name)
        return self._put(uri, {'upgrade_to': kwargs['upgrade_to']})

    def list_clusters(self, **kwargs):
        """
        Attempts to list available clusters.

        :param kwargs: Keyword arguments
        :type kwargs: dict
        """
        uri = '{0}/api/v0/clusters'.format(self.endpoint)
        return self._get(uri)

    def list_hosts(self, name, **kwargs):
        """
        Attempts to list all hosts or hosts in particular cluster.

        :param name: The name of the cluster (optional)
        :type name: str or None
        :param kwargs: Any other keyword arguments
        :type kwargs: dict
        """
        if not name:
            uri = '{0}/api/v0/hosts'.format(self.endpoint)
            result = self._get(uri)
            if result:
                result = [host['address'] for host in result]
            return result
        else:
            uri = '{0}/api/v0/cluster/{1}/hosts'.format(self.endpoint, name)
            return self._get(uri)


def main():
    """
    Main script entry point.
    """
    import yaml  # Used for output formatting
    epilog = 'Example: commctl create upgrade -n datacenter1 -u 7.2.2'

    parser = argparse.ArgumentParser(epilog=epilog)
    parser.add_argument(
        '--config', '-c', type=str, default=os.path.realpath(
            os.path.expanduser('~/.commissaire.json')),
        help='Full path to the configuration file.')

    # Create command structure
    sp = parser.add_subparsers(dest='main_command')
    sp.required = True

    get_parser = sp.add_parser('get')
    get_sp = get_parser.add_subparsers(dest='sub_command')
    get_sp.required = True
    cluster_parser = get_sp.add_parser('cluster')
    cluster_parser.required = True
    cluster_parser.add_argument(
        '-n', '--name', required=True, help='Name of the cluster')

    restart_parser = get_sp.add_parser('restart')
    restart_parser.required = True
    restart_parser.add_argument(
        '-n', '--name', required=True, help='Name of the cluster')

    upgrade_parser = get_sp.add_parser('upgrade')
    upgrade_parser.required = True
    upgrade_parser.add_argument(
        '-n', '--name', required=True, help='Name of the cluster')

    create_parser = sp.add_parser('create')
    create_parser.required = True
    create_sp = create_parser.add_subparsers(dest='sub_command')
    create_sp.required = True

    cluster_parser = create_sp.add_parser('cluster')
    cluster_parser.required = True
    cluster_parser.add_argument(
        '-n', '--name', required=True, help='Name of the cluster')

    restart_parser = create_sp.add_parser('restart')
    restart_parser.required = True
    restart_parser.add_argument(
        '-n', '--name', required=True, help='Name of the cluster')

    upgrade_parser = create_sp.add_parser('upgrade')
    upgrade_parser.required = True
    upgrade_parser.add_argument(
        '-n', '--name', required=True, help='Name of the cluster')
    upgrade_parser.add_argument(
        '-u', '--upgrade-to', required=True, help='Version to upgrade to')

    list_parser = sp.add_parser('list')
    list_sp = list_parser.add_subparsers(dest='sub_command')
    list_sp.required = True
    list_sp.add_parser('clusters')
    # No arguments for 'list clusters' at present.

    list_hosts_parser = list_sp.add_parser('hosts')
    list_hosts_parser.add_argument(
        '-n', '--name', required=False,
        help='Name of the cluster (omit to list all hosts)')

    args = parser.parse_args()

    # Set up the configuration
    conf = {}
    try:
        with open(args.config) as cf:
            conf = json.load(cf)
            for required in ('username', 'endpoint'):
                if required not in conf.keys():
                    conf[required] = input(
                        '{0}: '.format(required.capitalize()))

            # Check password on it's own
            if 'password' not in conf.keys():
                import getpass
                conf['password'] = getpass.getpass()
    except IOError:  # pragma no cover
        parser.error(
            'Configuration file {0} could not be opened for reading'.format(
                args.config))
    except ValueError:  # pragma no cover
        parser.error((
            'Unable to parse configuration file. HINT: Make sure to use only '
            'double quotes and the last item should not end with a coma.'))

    client = Client(conf)
    # Execute client command
    try:
        call_result = getattr(client, '{0}_{1}'.format(
            args.main_command, args.sub_command))(**args.__dict__)
        print(yaml.dump(
            call_result, default_flow_style=False,
            Dumper=yaml.SafeDumper, explicit_end=False).strip())
    except requests.exceptions.RequestException as re:
        parser.error(re)
    except ClientError as ce:
        parser.error(ce)


if __name__ == '__main__':  # pragma: no cover
    main()
