# Copyright (C) 2016  Red Hat, Inc
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import requests

def expected_status(r, code):
    if r.status_code == code:
        print("SUCCESS!")
    else:
        print("FAILURE {0} != {1}".format(code, r.status_code))


print("=> Listing Hosts Without Auth (Should Fail)")
r = requests.get('http://127.0.0.1:8000/api/v0/hosts')
print(r.json())
expected_status(r, 403)

print("=> Listing Hosts With Auth")
r = requests.get('http://127.0.0.1:8000/api/v0/hosts', auth=('a', 'a'))
print(r.json())
expected_status(r, 200)

print("=> Listing Existing Host 10.0.0.1")
r = requests.get(
    'http://127.0.0.1:8000/api/v0/host/10.0.0.1', auth=('a', 'a'))
print(r.json())
expected_status(r, 200)

print("=> Listing Non Existing Host 10.0.0.2")
r = requests.get(
    'http://127.0.0.1:8000/api/v0/hosts/10.0.0.2', auth=('a', 'a'))
print(r.json())
expected_status(r, 404)

print("=> Creating Host 10.2.0.2")
r = requests.put(
    'http://127.0.0.1:8000/api/v0/host/10.2.0.2',
    auth=('a', 'a'),
    json={
        "address": "10.2.0.2",
        "ssh_priv_key": "dGVzdAo=",
    })
print(r.json())
expected_status(r, 201)

print("=> Creating Host Again 10.2.0.2 (Should Fail)")
r = requests.put(
    'http://127.0.0.1:8000/api/v0/host/10.2.0.2',
    auth=('a', 'a'),
    json={
        "address": "10.2.0.2",
        "status": "available",
        "os": "atomic",
        "cpus": 2,
        "memory": 11989228,
        "space": 487652,
        "last_check": "2015-12-17T15:48:18.710454"})
print(r.json())
expected_status(r, 409)

print("=> Deleting Host 10.2.0.2")
r = requests.delete(
    'http://127.0.0.1:8000/api/v0/host/10.2.0.2',
    auth=('a', 'a'))
print(r.json())
expected_status(r, 410)

print("=> Getting Status Without Auth (Should Fail)")
r = requests.get('http://127.0.0.1:8000/api/v0/status')
print(r.json())
expected_status(r, 403)

print("=> Getting Status")
r = requests.get('http://127.0.0.1:8000/api/v0/status', auth=('a', 'a'))
print(r.json())
expected_status(r, 200)