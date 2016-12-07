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
import os
import requests

from behave import *


VALID_USERNAME = 'a'
VALID_PASSWORD = 'a'


def assert_status_code(actual, expected):
    assert actual == expected, \
        'Expected status code {0}, got {1}'.format(expected, actual)


@given('we are anonymous')
def impl(context):
    context.username = None
    context.password = None
    context.auth = (context.username, context.password)


@given('we have a valid username and password')
def impl(context):
    context.username = VALID_USERNAME
    context.password = VALID_PASSWORD
    context.auth = (context.username, context.password)

@given('we have {cert} as a client certificate')
def impl(context, cert):
    context.auth = None
    context.cert = (
        os.path.join(context.CERT_DIR, "{}.pem".format(cert)),
        os.path.join(context.CERT_DIR, "{}.key".format(cert))
    )

@then('commissaire will {access} access')
def impl(context, access):
    if access == 'allow':
        assert context.request.status_code != 403
    else:
        assert context.request.status_code == 403


@then('commissaire will note {status}')
def impl(context, status):
    code = None
    if status == 'a bad request':
        code = 400
    elif status == 'it\'s not found':
        code = 404
    elif status == 'a conflict':
        code = 409
    elif status == 'it\'s gone':
        code = 410
    elif status == 'success':
        code = 200
    elif status == 'creation':
        code = 201
    assert_status_code(context.request.status_code, code)


@then('commissaire will provide a {atype}')
def impl(context, atype):
    the_type = None
    if atype == 'list':
        the_type = list
    elif atype == 'dict':
        the_type = dict
    json = context.request.json()
    assert isinstance(json, the_type), \
        'Expected {0} to be a {1}'.format(json, str(the_type))


@then('the provided data is {expected}')
def impl(context, expected):
    json = context.request.json()
    assert json == eval(expected), \
        'Expected {0}, got {1}'.format(expected, json)
