# Copyright (C) 2016  Red Hat, Inc
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import etcd
import json
import platform
import random
import subprocess
import tempfile
import time

# XXX Reproducing commissaire.compat.urlparser because I can't seem to
#     import it from here.
if platform.python_version()[0] == '2':
    from urlparse import urlparse as _urlparse
else:
    from urllib.parse import urlparse as _urlparse
urlparse = _urlparse


def before_all(context):
    """
    Sets up anything before all tests run.
    """
    # Set SERVER via -D server=... or use a default
    context.SERVER = context.config.userdata.get(
        'server', 'http://127.0.0.1:8000')

    # Set ETCD via -D etcd=... or use a default
    context.ETCD = context.config.userdata.get(
        'etcd', 'http://127.0.0.1:2379')

    # Start etcd up via -D start-etcd=$ANYTHING
    if context.config.userdata.get('start-etcd', None):
        for retry in range(1, 4):
            listen_client_port = random.randint(50000, 60000)
            listen_peer_port = listen_client_port + 1
            listen_client_url = 'http://127.0.0.1:{0}'.format(
                listen_client_port)
            listen_peer_url = 'http://127.0.0.1:{0}'.format(listen_peer_port)
            context.ETCD_DATA_DIR = tempfile.mkdtemp()
            context.ETCD = listen_client_url

            # Try up to 3 times to gain usable random ports
            context.ETCD_PROCESS = subprocess.Popen(
                ['etcd', '--name', 'commissaireE2E',
                 '--initial-cluster',
                 'commissaireE2E={0}'.format(listen_peer_url),
                 '--listen-client-urls', listen_client_url,
                 '--advertise-client-urls', listen_client_url,
                 '--listen-peer-urls', listen_peer_url,
                 '--initial-advertise-peer-urls', listen_peer_url,
                 '--data-dir', context.ETCD_DATA_DIR])
            time.sleep(3)
            context.ETCD_PROCESS.poll()
            # If the returncode is not set then etcd is running
            if context.ETCD_PROCESS.returncode is None:
                break
            if retry == 3:
                print("Could not find a random port to use for "
                      "etcd. Exiting...")
                raise SystemExit(1)

    # Connect to the etcd service
    url = urlparse(context.ETCD)
    context.etcd = etcd.Client(host=url.hostname, port=url.port)
    context.etcd.write('/commissaire/config/kubetoken', 'test')

    # Start the server up via -D start-server=$ANYTHING
    if context.config.userdata.get('start-server', None):
        for retry in range(1, 4):
            server_port = random.randint(8500, 9000)
            context.SERVER = 'http://127.0.0.1:{0}'.format(server_port)
            # TODO: add kubernetes URL to options
            server_cli_args = [
                'python', 'src/commissaire/script.py',
                '--authentication-plugin',
                'commissaire.authentication.httpauthbyfile',
                '--authentication-plugin-kwargs',
                'filepath=conf/users.json',
                '-e', context.ETCD, '-k', 'http://127.0.0.1:8080',
                '--listen-port', str(server_port)]

            # Add any other server-args
            extra_server_args = context.config.userdata.get(
                'server-args', None)
            if extra_server_args:
                server_cli_args += extra_server_args.split(' ')

            print("Running server: {0}".format(" ".join(server_cli_args)))
            context.SERVER_PROCESS = subprocess.Popen(server_cli_args)
            time.sleep(3)
            context.SERVER_PROCESS.poll()
            # If the returncode is not set then etcd is running
            if context.SERVER_PROCESS.returncode is None:
                break
            if retry == 3:
                print("Could not find a random port to use for "
                      "commissaire. Exiting...")
                raise SystemExit(1)


def before_scenario(context, scenario):
    """
    Runs before every scenario.
    """
    # Reset HOST_DATA
    context.HOST_DATA = {
        "address": "",
        "status": "active",
        "os": "fedora",
        "cpus": 1,
        "memory": 1234,
        "space": 12345,
        "last_check": "",
        "ssh_priv_key": "",
    }

    # Wipe etcd state clean
    # XXX Delete individual subdirectories of '/commissaire' so we don't
    #     clobber '/commissaire/config'. Maybe reorganize so we can wipe
    #     state in one shot?  e.g. '/commissaire/state/...'
    delete_dirs = ['/commissaire/hosts',
                   '/commissaire/cluster',
                   '/commissaire/clusters']
    for dir in delete_dirs:
        try:
            context.etcd.delete(dir, recursive=True)
        except etcd.EtcdKeyNotFound:
            pass


def after_scenario(context, scenario):
    """
    Runs after every scenario.
    """
    # Wait for investigator processes to finish.
    busy_states = ('investigating', 'bootstrapping')
    try:
        etcd_resp = context.etcd.read('/commissaire/hosts', recursive=True)
        for child in etcd_resp._children:
            resp_data = etcd.EtcdResult(node=child)
            host_data = json.loads(resp_data.value)
            while host_data.get('status') in busy_states:
                context.etcd.watch(resp_data.key)
                resp_data = context.etcd.get(resp_data.key)
                host_data = json.loads(resp_data.value)
    except etcd.EtcdKeyNotFound:
        pass


def after_all(context):
    """
    Run after everything finishes.
    """
    if hasattr(context, 'ETCD_PROCESS'):
        context.ETCD_PROCESS.kill()
    if hasattr(context, 'SERVER_PROCESS'):
        context.SERVER_PROCESS.terminate()
        context.SERVER_PROCESS.wait()
