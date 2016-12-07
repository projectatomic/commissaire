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

import json
import time
import requests

from behave import *

from steps import (
    assert_status_code,
    VALID_USERNAME, VALID_PASSWORD)


@given('we set the key to bogus data')
def impl(context):
    context.HOST_DATA['ssh_priv_key'] = 'bogus'


@given('we set the cluster name to {cluster}')
def impl(context, cluster):
    context.HOST_DATA['cluster'] = cluster


@given('a host already exists at {host}')
def impl(context, host):
    data = dict(context.HOST_DATA)
    data['address'] = host
    context.etcd.set(
        '/commissaire/hosts/{0}'.format(host),
        json.dumps(data))


@given('we have a host at {host}')
def impl(context, host):
    data = dict(context.HOST_DATA)
    data['address'] = host
    request = requests.put(
        context.SERVER + '/api/v0/host/{0}'.format(host),
        auth=(VALID_USERNAME, VALID_PASSWORD),
        data=json.dumps(data))
    assert_status_code(request.status_code, 201)

    # Poll until the host is finished bootstrapping.
    # We can't watch an etcd key because the host record
    # is only written to etcd after a successful bootstrap.
    busy_states = ('investigating', 'bootstrapping')
    status_is_busy = True
    while status_is_busy:
        time.sleep(1)
        request = requests.get(
            context.SERVER + '/api/v0/host/{0}'.format(host),
            auth=(VALID_USERNAME, VALID_PASSWORD))
        assert_status_code(request.status_code, 200)
        data = request.json()
        status_is_busy = data['status'] in busy_states


@given('we have deleted host {host}')
def impl(context, host):
    request = requests.delete(
        context.SERVER + '/api/v0/host/{0}'.format(host),
        auth=(VALID_USERNAME, VALID_PASSWORD))
    assert_status_code(request.status_code, 200)


@when('we list all hosts')
def impl(context):
    context.request = requests.get(
        context.SERVER + '/api/v0/hosts',
        auth=(context.username, context.password))


@when('we get host status for {host}')
def impl(context, host):
    context.host = host
    context.request = requests.get(
        context.SERVER + '/api/v0/host/{0}/status'.format(context.host),
        auth=context.auth)


@when('we {operation} the host {host}')
def impl(context, operation, host):
    context.host = host
    if operation == 'get':
        context.request = requests.get(
            context.SERVER + '/api/v0/host/{0}'.format(context.host),
            auth=context.auth)
    elif operation == 'create':
        context.HOST_DATA['address'] = context.host
        context.request = requests.put(
            context.SERVER + '/api/v0/host/{0}'.format(context.host),
            data=json.dumps(context.HOST_DATA),
            auth=context.auth)
    elif operation == 'delete':
        context.request = requests.delete(
            context.SERVER + '/api/v0/host/{0}'.format(context.host),
            auth=context.auth)


@when('we get host credentials for {host}')
def impl(context, host):
    context.host = host
    context.request = requests.get(
        context.SERVER + '/api/v0/host/{0}/creds'.format(context.host),
        auth=context.auth)


@then('commissaire will return the host status')
def impl(context):
    data = context.request.json()
    assert 'type' in data.keys()
    assert 'host' in data.keys()
    assert 'container_manager' in data.keys()


@then('commissaire will return the host credentials')
def impl(context):
    data = context.request.json()
    assert 'ssh_priv_key' in data.keys()
    assert 'remote_user' in data.keys()


@then('commissaire will return {kind} host')
def impl(context, kind):
    if kind == 'the single':
        print(context.request.json())
        assert context.request.json().get('address') == context.host
    elif kind == 'no':
        assert_status_code(context.request.status_code, 404)
