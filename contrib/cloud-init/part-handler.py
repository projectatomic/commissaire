#part-handler
# vi: syntax=python ts=4
#
#  Handles a 'text/x-commissaire-host' part of a cloud-init user data file.
#  Registers the host with a Commissaire server using the given parameters.
#
#  Parameter syntax is simple 'KEY = VALUE' lines.
#
#  Recognized (case-insensitive) keys are:
#
#  COMMISSAIRE_SERVER_HOST
#    The host name of the Commissaire service.
#
#  COMMISSAIRE_SERVER_PORT  (optional)
#    The port number of the Commissaire service.  Defaults to 8000.
#
#  COMMISSAIRE_SERVER_USERNAME  (optional)
#    The user name to use for Commissaire service authentication.
#
#  COMMISSAIRE_SERVER_PASSWORD  (optional)
#    The password to use for Commissaire service authentication.
#
#  COMMISSAIRE_SERVER_SECURE  (optional)
#    Boolean value indicates whether to connect to the Commissaire
#    service using Transport Layer Security (TLS).  Defaults to true.
#
#  COMMISSAIRE_CLUSTER  (optional)
#    The name of the cluster to join.
#
#  ROOT_SSH_KEY_PATH  (optional)
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

import sys
import stat
import os
import os.path
import configparser
import subprocess
import base64

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

    parser = configparser.ConfigParser()

    try:
        payload_with_section = '[DEFAULT]\n' + payload
        parser.read_string(payload_with_section, source=filename)
    except configparser.ParsingError as err:
        print(str(err), file=sys.stderr)
        raise

    keys = parser['DEFAULT']

    if not 'COMMISSAIRE_SERVER_HOST' in keys:
        print('{0}: Missing required key COMMISSAIRE_SERVER_HOST'.
            format(filename), file=sys.stderr)
        return

    host = keys.get('COMMISSAIRE_SERVER_HOST')
    port = keys.get('COMMISSAIRE_SERVER_PORT', 8000)
    user = keys.get('COMMISSAIRE_SERVER_USERNAME')
    pwrd = keys.get('COMMISSAIRE_SERVER_PASSWORD')
    tls = keys.getboolean('COMMISSAIRE_SERVER_SECURE')
    cluster = keys.get('COMMISSAIRE_CLUSTER')
    keyfile = keys.get('ROOT_SSH_KEY_PATH', '/root/.ssh/id_rsa')

    if keyfile:
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

    json = {}

    try:
        with open(keyfile, 'rb') as f:
            b64_bytes = base64.b64encode(f.read())
            json['ssh_priv_key'] = b64_bytes.decode()
    except Exception as ex:
        print(str(ex), file=sys.stderr)
        raise

    if cluster:
        json['cluster'] = cluster

    url = '{0}://{1}:{2}/api/v0/host/'.format(
        'https' if tls else 'http', host, port)

    auth = (user, pwrd) if user and pwrd else None

    resp = requests.put(url, json=json, auth=auth)
    print('Commissaire response: {0} {1}'.format(
        resp.status_code, resp.reason))
