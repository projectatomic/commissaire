# Copyright (C) 2017  Red Hat, Inc
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
import uuid

from behave import *

from steps import (
    assert_status_code,
    VALID_USERNAME, VALID_PASSWORD)


@given('we have a trivial container manager')
def impl(context):
    data = {'name': 'trivial', 'type': 'trivial', 'options': {}}
    request = requests.put(
        context.SERVER_HTTP + '/api/v0/containermanager/trivial',
        auth=(VALID_USERNAME, VALID_PASSWORD),
        data=json.dumps(data))
    assert_status_code(request.status_code, 201)

@then('the host status will include container manager details')
def impl(context):
    container_manager_status = context.request.json().get('container_manager')
    assert type(container_manager_status) is dict
    assert len(container_manager_status) > 0

@then('the host status will not include container manager details')
def impl(context):
    container_manager_status = context.request.json().get('container_manager')
    assert type(container_manager_status) is dict
    assert len(container_manager_status) == 0
