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
"""
Behave base environment for Commissaire E2E testing.

The following optional arguments can be provided via "-D name=value":

- commissaire-server: The URI of the server to use.
- etcd: The URI of a running etcd to use.
- bus-uri: The URI of a bus service to use.
- use-vagrant: If vagrant is in use. Ignores start-* items.
- start-all-servers: Starts everything (like setting all start-* items).
- start-etcd: If etcd should be started.
- start-redis: If redis should be started. Also sets BUS_URI.
- start-storage-service: If commissaire-storage-service should start.
- start-investigator-service: If commissaire-investigator-service should start.
- start-watcher-service: If commissaire-watcher-service should start.
- start-commissaire-server: If the commissaire-server should start.
- commissaire-server-args: Any extra arguments for starting commissaire-server.
"""

import base64
import etcd
import json
import logging
import os
import random
import shutil
import subprocess
import tempfile
import time

from urllib.parse import urlparse

from commissaire import constants as C

# Fill in with context.ETCD after start_etcd().
STORAGE_CONF_TEMPLATE = """
{{
  "storage_handlers": [
    {{
      "type": "commissaire.storage.etcd",
      "server_url": "{}",
      "models": ["*"]
    }}
  ]
}}
"""


def generate_certificates(context):
    """
    Generates new certificates for testing.
    """
    context.CERT_DIR = tempfile.mkdtemp()
    subprocess.check_call([
        'openssl', 'req', '-x509', '-nodes',
        '-newkey', 'rsa:2048', '-keyout', 'ca.key',
        '-out', 'ca.pem', '-days', '1',
        '-subj', '/CN=test-ca'], cwd=context.CERT_DIR)
    subprocess.check_call([
        'openssl', 'req', '-x509', '-nodes',
        '-newkey', 'rsa:2048', '-keyout', 'self-client.key',
        '-out', 'self-client.pem', '-days', '1',
        '-subj', '/CN=test-client'], cwd=context.CERT_DIR)
    subprocess.check_call([
        'openssl', 'req', '-nodes',
        '-newkey', 'rsa:2048', '-keyout', 'server.key',
        '-out', 'server.req',
        '-subj', '/CN=test-client'], cwd=context.CERT_DIR)
    subprocess.check_call([
        'openssl', 'req', '-nodes',
        '-newkey', 'rsa:2048', '-keyout', 'client.key',
        '-out', 'client.req',
        '-subj', '/CN=test-client'], cwd=context.CERT_DIR)
    subprocess.check_call([
        'openssl', 'req', '-nodes',
        '-newkey', 'rsa:2048', '-keyout', 'other.key',
        '-out', 'other.req',
        '-subj', '/CN=test-other'], cwd=context.CERT_DIR)
    subprocess.check_call([
        'openssl', 'x509', '-req', '-days', '1', '-in', 'server.req',
        '-CA', 'ca.pem', '-CAkey', 'ca.key', '-set_serial', '01',
        '-out', 'server.pem'], cwd=context.CERT_DIR)
    subprocess.check_call([
        'openssl', 'x509', '-req', '-days', '1', '-in', 'client.req',
        '-CA', 'ca.pem', '-CAkey', 'ca.key', '-set_serial', '02',
        '-out', 'client.pem'], cwd=context.CERT_DIR)
    subprocess.check_call([
        'openssl', 'x509', '-req', '-days', '1', '-in', 'other.req',
        '-CA', 'ca.pem', '-CAkey', 'ca.key', '-set_serial', '03',
        '-out', 'other.pem'], cwd=context.CERT_DIR)

    # Turn the server.pem file into a real pem
    with open(os.path.sep.join([
            context.CERT_DIR, 'server.pem']), 'a') as server_fobj:
        with open(os.path.sep.join([
                context.CERT_DIR, 'server.key']), 'r') as key_fobj:
            server_fobj.write(key_fobj.read())


def try_start(func, name, context, args=[], **kwargs):
    """
    Tries up to 3 times to get a success response from func. If the proceess
    can not be started SystemExit is raised.

    :param func: The function to try to start.
    :type func: callable
    :param name: The name of the thing we are trying to start.
    :type name: str
    :param context: The current behave context.
    :type context: behave.runner.Context
    :param args: Any other CLI args that should be passed to the function.
    :type args: list
    :param kwargs: Keyword arguments to pass to func.
    :type kwargs: dict
    :returns: The running processes
    :rtype: subprocess.Popen
    :raises: SystemExit
    """
    for retry in range(1, 4):
        process = func(context, args, **kwargs)
        if process:
            return process
        elif retry == 3:
            print('Could not find a random port to use for '
                  '{}. Exiting...'.format(name))
            raise SystemExit(1)


def start_commissaire_server(context, args):
    """
    Starts a new commissaire REST server.
    """
    server_port = str(random.randint(8500, 9000))
    context.SERVER_HTTP = 'http://127.0.0.1:{}'.format(server_port)
    context.SERVER_HTTP_PORT = server_port
    server_cli_args = [
        'commissaire-server',
        '--no-config-file',
        '--bus-uri', context.BUS_URI,
        '--listen-port', str(server_port)]

    server_cli_args += args

    # Add any other commissaire-server-args
    extra_server_http_args = context.config.userdata.get(
        'commissaire-server-args')
    if extra_server_http_args:
        server_cli_args += extra_server_http_args.split(' ')

    print('Running server: {}'.format(' '.join(server_cli_args)))
    server = subprocess.Popen(server_cli_args)
    time.sleep(3)
    server.poll()
    # If the returncode is not set then the server is running
    if server.returncode is None:
        return server


def start_etcd(context, args):
    """Starts an etcd instance."""
    listen_client_port = random.randint(50000, 60000)
    listen_peer_port = listen_client_port + 1
    listen_client_url = 'http://127.0.0.1:{}'.format(
        listen_client_port)
    listen_peer_url = 'http://127.0.0.1:{}'.format(
        listen_peer_port)
    context.ETCD_DATA_DIR = tempfile.mkdtemp()
    context.ETCD = listen_client_url

    # Try up to 3 times to gain usable random ports
    context.PROCESSES['etcd'] = subprocess.Popen(
        ['etcd', '--name', 'commissaireE2E',
         '--initial-cluster',
         'commissaireE2E={}'.format(listen_peer_url),
         '--listen-client-urls', listen_client_url,
         '--advertise-client-urls', listen_client_url,
         '--listen-peer-urls', listen_peer_url,
         '--initial-advertise-peer-urls', listen_peer_url,
         '--data-dir', context.ETCD_DATA_DIR])
    time.sleep(3)
    context.PROCESSES['etcd'].poll()
    # If the returncode is not set then etcd is running
    if context.PROCESSES['etcd'].returncode is None:
        return context.PROCESSES['etcd']


def start_commissaire_service(context, args, **kwargs):
    """Starts a commissaire service."""
    process = subprocess.Popen(
        args + ['--bus-uri', context.BUS_URI], **kwargs)
    time.sleep(1)
    process.poll()

    if process.returncode is None:
        return process


def start_redis(context, args):
    """Starts a redis service."""
    listen_port = str(random.randint(50000, 60000))
    context.BUS_URI = 'redis://127.0.0.1:{}/'.format(listen_port)

    context.PROCESSES['redis'] = subprocess.Popen(
        ['redis-server', '--port', listen_port])
    time.sleep(1)
    context.PROCESSES['redis'].poll()

    # If the returncode is not set then etcd is running
    if context.PROCESSES['redis'].returncode is None:
        return context.PROCESSES['redis']


def stop_process(context, process):
    """
    Kills the running process.
    """
    process.terminate()
    process.wait()


def before_tag(context, tag):
    """
    Special steps before a tagged test runs.
    """
    if tag == 'slow':
        if not context.config.userdata.get('use-vagrant'):
            context.scenario.skip(reason='requires vagrant environment')

    if tag == 'clientcert':
        verifyfile = os.path.join(context.CERT_DIR, 'ca.pem')
        pemfile = os.path.join(context.CERT_DIR, 'server.pem')

        server_http = try_start(
            start_commissaire_server, 'commissaire-server', context, [
                '--authentication-plugin',
                'commissaire_http.authentication.httpauthclientcert:cn=test-client',
                '--tls-pemfile={}'.format(pemfile),
                '--tls-clientverifyfile={}'.format(verifyfile)],
        )
        context.SERVER_HTTP = 'https://localhost:{}'.format(
            context.SERVER_HTTP_PORT)
        context.PROCESSES['ssl_server'] = server_http


def after_tag(context, tag):
    """
    Special steps after a tagged test runs.
    """
    if tag == 'clientcert':
        stop_process(context, context.PROCESSES['ssl_server'])


def before_all(context):
    """
    Sets up anything before all tests run.
    """
    # Log everything
    logging.basicConfig(level=logging.DEBUG)

    # start-all-servers sets all start-*'s to True
    if context.config.userdata.get('start-all-servers'):
        context.config.userdata['start-etcd'] = True
        context.config.userdata['start-redis'] = True
        context.config.userdata['start-storage-service'] = True
        context.config.userdata['start-investigator-service'] = True
        context.config.userdata['start-watcher-service'] = True
        context.config.userdata['start-commissaire-server'] = True

    # Holds all spawned processes
    context.PROCESSES = {}

    # Set SERVER via -D server=... or use a default
    context.SERVER_HTTP = context.config.userdata.get(
        'commissaire-server', 'http://127.0.0.1:8000')

    # Set ETCD via -D etcd=... or use a default
    context.ETCD = context.config.userdata.get(
        'etcd', 'http://127.0.0.1:2379')

    # Set BUS_URI via -D bus-uri=... or use a default
    context.BUS_URI = context.config.userdata.get(
        'bus-uri', 'redis://127.0.0.1:6379/')

    generate_certificates(context)
    context.USE_VAGRANT = False

    # Set variables to use Vagrant IPs
    if context.config.userdata.get('use-vagrant'):
        context.SERVER_HTTP = 'http://192.168.152.100:8000'
        context.ETCD = 'http://192.168.152.101:2379'
        context.BUS_URI = 'redis://192.168.152.101:6379'
        context.USE_VAGRANT = True

    # Read and encode SSH key
    with open('features/id_rsa', 'rb') as f:
        b64_bytes = base64.b64encode(f.read())
        context.SSH_PRIV_KEY = b64_bytes.decode()

    # Start etcd up via -D start-etcd=$ANYTHING
    if context.config.userdata.get('start-etcd'):
        if context.USE_VAGRANT:
            print('Using vagrant. Ignoring start-etcd...')
        else:
            if context.config.userdata.get('start-etcd'):
                try_start(start_etcd, 'etcd', context)

    # Connect to the etcd service
    print('Connecting to ETCD...')
    url = urlparse(context.ETCD)
    context.etcd = etcd.Client(host=url.hostname, port=url.port)

    # Set up initial etcd directories (similar to etcd_init.sh)
    make_dirs = ['/commissaire/hosts',
                 '/commissaire/cluster',
                 '/commissaire/clusters',
                 '/commissaire/networks',
                 '/commissaire/status']
    for key in make_dirs:
        try:
            context.etcd.write(key, None, dir=True)
        except etcd.EtcdNotFile:
            pass
    context.etcd.write(
        '/commissaire/networks/default', C.DEFAULT_CLUSTER_NETWORK_JSON)

    context.etcd.write('/commissaire/config/kubetoken', 'test')

    if context.USE_VAGRANT:
        print('Using vagrant. Skipping any requested starts ...')
    else:
        if context.config.userdata.get('start-redis'):
            try_start(start_redis, 'redis', context)

        if context.config.userdata.get('start-storage-service'):
            # Feed the service with a configuration through stdin.
            process = try_start(
                start_commissaire_service, 'commissaire-storage-service',
                context, [
                    'commissaire-storage-service',
                    '--config-file', '-'],
                stdin=subprocess.PIPE,
                universal_newlines=True)
            context.PROCESSES['commissaire-storage-service'] = process
            process.stdin.write(STORAGE_CONF_TEMPLATE.format(context.ETCD))
            process.stdin.close()

        if context.config.userdata.get('start-investigator-service'):
            context.PROCESSES['commissaire-investigator-service'] = try_start(
                start_commissaire_service, 'commissaire-investigator-service',
                context, [
                    'commissaire-investigator-service',
                    '--config-file',
                    '../commissaire-service/conf/investigator.conf'])

        if context.config.userdata.get('start-watcher-service'):
            context.PROCESSES['commissaire-watcher-service'] = try_start(
                start_commissaire_service, 'commissaire-watcher-service',
                context, [
                    'commissaire-watcher-service',
                    '--config-file',
                    '../commissaire-service/conf/watcher.conf'])

        if context.config.userdata.get('start-commissaire-server'):
            context.PROCESSES['commissaire-server'] = try_start(
                start_commissaire_server, 'commissaire-server',
                context, [
                    '--authentication-plugin',
                    'commissaire_http.authentication.httpbasicauth:'
                    'filepath=../commissaire-http/conf/users.json'])


def before_scenario(context, scenario):
    """
    Runs before every scenario.
    """
    # Reset HOST_DATA
    context.HOST_DATA = {
        'address': '',
        'remote_user': 'vagrant',
        'status': C.HOST_STATUS_ACTIVE,
        'os': 'fedora',
        'cpus': 1,
        'memory': 1234,
        'space': 12345,
        'last_check': '',
        'ssh_priv_key': context.SSH_PRIV_KEY,
    }

    # Reset NETWORK_DATA
    context.NETWORK_DATA = {
        'name': 'default',
        'type': 'flannel_etcd',
        'options': {},
    }

    # Wipe etcd state clean
    # XXX Delete individual subdirectories of '/commissaire' so we don't
    #     clobber '/commissaire/config'. Maybe reorganize so we can wipe
    #     state in one shot?  e.g. '/commissaire/state/...'
    delete_dirs = ['/commissaire/hosts',
                   '/commissaire/cluster',
                   '/commissaire/clusters',
                   '/commissaire/networks',
                   '/commissaire/status']
    for key in delete_dirs:
        try:
            context.etcd.delete(key, recursive=True)
        except etcd.EtcdKeyNotFound:
            pass

    # Recreate default network
    context.etcd.write(
        '/commissaire/networks/default',
        '{"name": "default", "type": "flannel_etcd", "options": {}}')


def after_scenario(context, scenario):
    """
    Runs after every scenario.
    """
    # Wait for investigator processes to finish.
    busy_states = (
        C.HOST_STATUS_INVESTIGATING,
        C.HOST_STATUS_BOOTSTRAPPING)
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
    # Stop all processes
    for name, process in context.PROCESSES.items():
        stop_process(context, process)

    # Clean up the CERT_DIR if it exists
    if getattr(context, 'CERT_DIR'):
        shutil.rmtree(context.CERT_DIR)
