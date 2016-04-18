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


@given('we have a host at {host}')
def impl(context, host):
    data = dict(context.HOST_DATA)
    data['address'] = host
    request = requests.put(
        context.SERVER + '/api/v0/host/{0}'.format(host),
        auth=(VALID_USERNAME, VALID_PASSWORD),
        data=json.dumps(data))
    assert_status_code(request.status_code, 201)


@given('we have deleted host {host}')
def impl(context, host):
    request = requests.delete(
        context.SERVER + '/api/v0/host/{0}'.format(host),
        auth=(VALID_USERNAME, VALID_PASSWORD))
    assert_status_code(request.status_code, 410)


@when('we list all hosts')
def impl(context):
    context.request = requests.get(
        context.SERVER + '/api/v0/hosts',
        auth=(context.username, context.password))


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


@then('commissaire will return {kind} host')
def impl(context, kind):
    if kind == 'the single':
        print(context.request.json())
        assert context.request.json().get('address') == context.host
    elif kind == 'no':
        assert_status_code(context.request.status_code, 404)
