#part-handler
# vi: syntax=python ts=4
#
#  Handles a 'text/x-commissaire-host' part of a cloud-init user data file.
#  Registers the host with a Commissaire server using the given parameters.
#
#  Data format is a JSON object with the following members:
#
#  "endpoint"
#    Base URI of the Commissaire service.
#
#  "username"  (optional)
#    The user name to use for Commissaire service authentication.
#
#  "password"  (optional)
#    The password to use for Commissaire service authentication.
#
#  "cluster"  (optional)
#    The name of the cluster to join.
#
#  "root_ssh_key_path"  (optional)
#    The private SSH key file for the root account of this host.
#    Defaults to '/root/.ssh/id_rsa' and, if necessary, generates
#    a public/private key pair with no passphrase.
#
#
# TO CREATE A USER-DATA FILE
# ::::::::::::::::::::::::::
#
# The user-data file must use MIME multipart/mixed format.  You can generate
# such a file with the "make-mime.py" script in cloud-init's tools directory:
#
# http://bazaar.launchpad.net/~cloud-init-dev/cloud-init/trunk/view/head:/tools/make-mime.py
#
# Suppose the text/cloud-config data are in the file 'config.txt' and the
# text/x-commissaire-host parameters are in the file 'commissaire.txt',
# then to generate a user-data file that embeds this script:
#
#    $ python make-mime.py \
#             --attach config.txt:cloud-config \
#             --attach part-handler.py:part-handler \
#             --attach commissaire.txt:x-commissaire-host \
#             > user-data
#
# Alternatively, you can instruct cloud-init to download this part handler
# script from a URL at boot time by attaching a text/x-include-url file:
#
#    $ python make-mime.py \
#             --attach config.txt:cloud-config \
#             --attach include.txt:x-include-url \
#             --attach commissaire.txt:x-commissaire-host \
#             > user-data
#
# Whether the part handler is included by way of direct embedding or a URL,
# it must appear in the multipart file BEFORE the text/x-commissaire-host
# part so cloud-init knows how to handle the text/x-commissaire-host part.
#

from __future__ import print_function

import sys
import stat
import os
import os.path
import subprocess
import base64
import json

# 3rd party module
import requests

MIME_TYPE = 'text/x-commissaire-host'

def list_types():
    return [MIME_TYPE]

def handle_part(data, ctype, filename, payload):
    if ctype == '__begin__':
        return

    if ctype == '__end__':
        return

    # Re-raise any exceptions so they get logged, but also print a
    # useful message before doing so to help ascertain the problem.

    try:
        config = json.loads(payload)
        assert type(config) is dict
    except (AssertionError, ValueError):
        print('{0}: {1} data must be a JSON object'.format(filename, ctype),
              file=sys.stderr)
        return

    if 'endpoint' not in config:
        print('{0}: Missing required "endpoint" URI'.format(filename),
              file=sys.stderr)
        return

    endpoint = config.get('endpoint')
    username = config.get('username')
    password = config.get('password')
    cluster = config.get('cluster')
    keyfile = config.get('root_ssh_key_path', '/root/.ssh/id_rsa')

    if not os.path.isfile(keyfile):
        try:
            subprocess.check_call(
                ['/usr/bin/ssh-keygen', '-q', '-N', '',
                 '-t', 'rsa', '-f', keyfile])
        except FileNotFoundError:
            print('Missing /usr/bin/ssh-keygen', file=sys.stderr)
            raise
        except subprocess.CalledProcessError as ex:
            print(str(ex), file=sys.stderr)
            raise

    try:
        authorized_keys = '/root/.ssh/authorized_keys'
        with open(keyfile + '.pub') as inpf:
            # If creating a new file, set mode to 0600.
            fd = os.open(authorized_keys,
                         os.O_WRONLY | os.O_APPEND | os.O_CREAT,
                         stat.S_IRUSR | stat.S_IWUSR)
            with os.fdopen(fd, 'a') as outf:
                outf.writelines(inpf.readlines())
    except Exception as ex:
        print(str(ex), file=sys.stderr)
        raise

    body = {}

    try:
        with open(keyfile, 'rb') as f:
            b64_bytes = base64.b64encode(f.read())
            body['ssh_priv_key'] = b64_bytes.decode()
    except Exception as ex:
        print(str(ex), file=sys.stderr)
        raise

    if cluster:
        body['cluster'] = cluster

    uri = '{0}/api/v0/host'.format(endpoint)
    auth = (username, password) if username and password else None

    resp = requests.put(uri, json=body, auth=auth)
    print('Commissaire response: {0} {1}'.format(
        resp.status_code, resp.reason))
