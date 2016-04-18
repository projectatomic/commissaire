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


@given('we have a cluster named {cluster}')
def impl(context, cluster):
    request = requests.put(
        context.SERVER + '/api/v0/cluster/{0}'.format(cluster),
        auth=(VALID_USERNAME, VALID_PASSWORD))
    assert_status_code(request.status_code, 201)


@given('we have added host {host} to cluster {cluster}')
def impl(context, host, cluster):
    request = requests.put(
        context.SERVER + '/api/v0/cluster/{0}/hosts/{1}'.format(cluster, host),
        auth=(VALID_USERNAME, VALID_PASSWORD))
    assert_status_code(request.status_code, 200)


@given('we have removed host {host} from cluster {cluster}')
def impl(context, host, cluster):
    request = requests.delete(
        context.SERVER + '/api/v0/cluster/{0}/hosts/{1}'.format(cluster, host),
        auth=(VALID_USERNAME, VALID_PASSWORD))
    assert_status_code(request.status_code, 200)


@when('we check for host {host} in the cluster {cluster}')
def impl(context, host, cluster):
    context.cluster = cluster
    context.request = requests.get(
        context.SERVER + '/api/v0/cluster/{0}/hosts/{1}'.format(cluster, host),
        auth=context.auth)


@when('we add host {host} to the cluster {cluster}')
def impl(context, host, cluster):
    context.cluster = cluster
    context.request = requests.put(
        context.SERVER + '/api/v0/cluster/{0}/hosts/{1}'.format(cluster, host),
        auth=context.auth)


@when('we remove host {host} from the cluster {cluster}')
def impl(context, host, cluster):
    context.cluster = cluster
    context.request = requests.delete(
        context.SERVER + '/api/v0/cluster/{0}/hosts/{1}'.format(cluster, host),
        auth=context.auth)


@when('we set the host list for cluster {cluster} to {json}')
def impl(context, cluster, json):
    context.cluster = cluster
    context.request = requests.put(
        context.SERVER + '/api/v0/cluster/{0}/hosts'.format(cluster),
        json=eval(json),
        auth=context.auth)


@when('we {operation} the cluster {cluster}')
def impl(context, operation, cluster):
    context.cluster = cluster
    if operation == 'get':
        context.request = requests.get(
            context.SERVER + '/api/v0/cluster/{0}'.format(cluster),
            auth=context.auth)
    elif operation == 'create':
        context.request = requests.put(
            context.SERVER + '/api/v0/cluster/{0}'.format(cluster),
            auth=context.auth)
    elif operation == 'delete':
        context.request = requests.delete(
            context.SERVER + '/api/v0/cluster/{0}'.format(cluster),
            auth=context.auth)
    elif operation == 'get hosts in':
        context.request = requests.get(
            context.SERVER + '/api/v0/cluster/{0}/hosts'.format(cluster),
            auth=context.auth)
    else:
        raise NotImplementedError


@when('we initiate {async_operation} of cluster {cluster}')
def impl(context, async_operation, cluster):
    context.cluster = cluster
    if async_operation == 'an upgrade':
        context.request = requests.put(
            context.SERVER + '/api/v0/cluster/{0}/upgrade'.format(cluster),
            auth=context.auth,
            json={"upgrade_to": "7.2.1"})
    elif async_operation == 'a restart':
        context.request = requests.put(
            context.SERVER + '/api/v0/cluster/{0}/restart'.format(cluster),
            auth=context.auth)
    else:
        raise NotImplementedError


@when('we list all clusters')
def impl(context):
    context.request = requests.get(
        context.SERVER + '/api/v0/clusters', auth=context.auth)


@then('the provided cluster status is {status}')
def impl(context, status):
    json = context.request.json()
    assert json['status'] == status, \
        'Expected status {0}, got {1}'.format(status, json['status'])


@then('the provided cluster {what} hosts is {expected}')
def impl(context, what, expected):
    json = context.request.json()
    assert json['hosts'][what] == int(expected), \
        'Expected {0} {1} hosts, got {2}'.format(
            expected, what, json['hosts'][what])


@then('the host {host} will be in the cluster {cluster}')
def impl(context, host, cluster):
    request = requests.get(
        context.SERVER + '/api/v0/cluster/{0}/hosts/{1}'.format(cluster, host),
        auth=(VALID_USERNAME, VALID_PASSWORD))
    assert_status_code(request.status_code, 200)


@then('the host {host} will not be in the cluster {cluster}')
def impl(context, host, cluster):
    request = requests.get(
        context.SERVER + '/api/v0/cluster/{0}/hosts/{1}'.format(cluster, host),
        auth=(VALID_USERNAME, VALID_PASSWORD))
    assert_status_code(request.status_code, 404)


@then('commissaire will provide {async_operation} status')
def impl(context, async_operation):
    json = context.request.json()
    if async_operation == 'upgrade':
        expected_keys = set(('status', 'upgrade_to', 'upgraded',
                             'in_process', 'started_at', 'finished_at'))
    elif async_operation == 'restart':
        expected_keys = set(('status', 'restarted', 'in_process',
                             'started_at', 'finished_at'))
    actual_keys = set(json.keys())
    assert actual_keys == expected_keys, \
           'Expected keys {0}, got {1}'.format(expected_keys, actual_keys)


@then('the provided status is {status}')
def impl(context, status):
    json = context.request.json()
    actual_status = json.get('status')
    assert actual_status == status, \
           'Expected status {0}, got {1}'.format(status, actual_status)
