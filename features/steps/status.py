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

import os
import requests
from requests.exceptions import SSLError

from behave import *


@when('we get status')
def impl(context):
    verify=False
    if context.SERVER.startswith("https"):
        verify=os.path.join(context.CERT_DIR, "ca.pem")

    try:
        context.request = requests.get(
            context.SERVER + '/api/v0/status',
            auth=context.auth,
            verify=verify,
            cert=getattr(context, "cert", None))
    except SSLError, e:
        context.request_ssl_error = e

@then('commissaire will return status')
def impl(context):
    results = context.request.json()
    print(results.keys())
    for key in ('investigator', 'etcd'):
        assert key in results.keys()

@then('commissaire ssl will error')
def impl(context):
    assert context.request_ssl_error
