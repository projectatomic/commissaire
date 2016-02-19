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

# XXX These tests are obsoleted by equivalent Behave tests in /features.
#     New test cases will be added there, not here.

import sys
import requests

SERVER = 'http://127.0.0.1:8000'
AUTH = ('a', 'a')

try:
    SERVER = sys.argv[1]
except:
    pass


print ('=> Server set to {0}'.format(SERVER))


def expected_json(actual, expect):
    if actual != expect:
        print ("FAILURE {0} != {1}".format(actual, expect))
        return False
    else:
        return True

def expected_status(r, code):
    if r.status_code == code:
        print("SUCCESS!")
    else:
        print("FAILURE {0} != {1}".format(code, r.status_code))


print("=> Listing Hosts Without Auth (Should Fail)")
r = requests.get(SERVER + '/api/v0/hosts')
print(r.json())
expected_status(r, 403)

print("=> Listing Hosts With Auth")
r = requests.get(SERVER + '/api/v0/hosts', auth=AUTH)
print(r.json())
expected_status(r, 200)

print("=> Listing Existing Host 10.0.0.1")
r = requests.get(SERVER + '/api/v0/host/10.0.0.1', auth=AUTH)
print(r.json())
expected_status(r, 200)

print("=> Listing Non Existing Host 10.0.0.2")
r = requests.get(SERVER + '/api/v0/hosts/10.0.0.2', auth=AUTH)
print(r.json())
expected_status(r, 404)

print("=> Creating Host 10.2.0.2")
r = requests.put(
    SERVER + '/api/v0/host/10.2.0.2', auth=AUTH,
    json={"ssh_priv_key": "dGVzdAo="})
print(r.json())
expected_status(r, 201)

print("=> Recreating Compatible Host 10.2.0.2")
r = requests.put(
    SERVER + '/api/v0/host/10.2.0.2', auth=AUTH,
    json={"ssh_priv_key": "dGVzdAo="})
print(r.json())
expected_status(r, 200)

print("=> Recreating Incompatible Host 10.2.0.2 (Should Fail)")
r = requests.put(
    SERVER + '/api/v0/host/10.2.0.2', auth=AUTH,
    json={"ssh_priv_key": "boguskey"})
print(r.json())
expected_status(r, 409)

print("=> Deleting Host 10.2.0.2")
r = requests.delete(SERVER + '/api/v0/host/10.2.0.2', auth=AUTH)
print(r.json())
expected_status(r, 410)

print("=> Getting Status Without Auth (Should Fail)")
r = requests.get(SERVER + '/api/v0/status')
print(r.json())
expected_status(r, 403)

print("=> Getting Status")
r = requests.get(SERVER + '/api/v0/status', auth=AUTH)
print(r.json())
expected_status(r, 200)

#------------
#  Clusters
#------------

print("=> Creating Cluster 'honeynut' Without Auth (Should Fail)")
r = requests.put(SERVER + '/api/v0/cluster/honeynut')
print(r.json())
expected_status(r, 403)

print("=> Creating Cluster 'honeynut' With Auth")
r = requests.put(SERVER + '/api/v0/cluster/honeynut', auth=AUTH)
print(r.json())
expected_status(r, 201)

print("=> Creating Cluster 'honeynut' Again (Should Be Idempotent)")
r = requests.put(SERVER + '/api/v0/cluster/honeynut', auth=AUTH)
print(r.json())
expected_status(r, 201)

print("=> Listing Clusters Without Auth (Should Fail)")
r = requests.get(SERVER + '/api/v0/clusters')
print(r.json())
expected_status(r, 403)

print("=> Listing Clusters With Auth")
r = requests.get(SERVER + '/api/v0/clusters', auth=AUTH)
print(r.json())
expect = ['honeynut']
expected_json(r.json(), expect) and expected_status(r, 200)

print("=> Examining Cluster 'honeynut' Without Auth (Should Fail)")
r = requests.get(SERVER + '/api/v0/cluster/honeynut')
print(r.json())
expected_status(r, 403)

print("=> Examining Cluster 'honeynut' With Auth")
r = requests.get(SERVER + '/api/v0/cluster/honeynut', auth=AUTH)
print(r.json())
expect = {'status': 'ok', 'hosts': {'total': 0, 'available': 0, 'unavailable': 0}}
expected_json(r.json(), expect) and expected_status(r, 200)

print("=> Creating Host 10.2.0.2")
r = requests.put(
    SERVER + '/api/v0/host/10.2.0.2', auth=AUTH,
    json={
        "address": "10.2.0.2",
        "ssh_priv_key": "dGVzdAo="
    })
print(r.json())
expected_status(r, 201)

print("=> Examining Cluster 'honeynut' (No Hosts)")
r = requests.get(SERVER + '/api/v0/cluster/honeynut', auth=AUTH)
print(r.json())
expect = {'status': 'ok', 'hosts': {'total': 0, 'available': 0, 'unavailable': 0}}
expected_json(r.json(), expect) and expected_status(r, 200)

print("=> Verify Host List for Cluster 'honeynut'")
r = requests.get(SERVER + '/api/v0/cluster/honeynut/hosts', auth=AUTH)
print(r.json())
expected_json(r.json(), []) and expected_status(r, 200)

print("=> Verify Host 10.2.0.2 Not In Cluster 'honeynut'")
r = requests.get(SERVER + '/api/v0/cluster/honeynut/hosts/10.2.0.2', auth=AUTH)
print(r.json())
expected_status(r, 404)

print("=> Adding Host 10.2.0.2 to Cluster 'honeynut'")
r = requests.put(SERVER + '/api/v0/cluster/honeynut/hosts/10.2.0.2', auth=AUTH)
print(r.json())
expected_status(r, 200)

print("=> Examining Cluster 'honeynut' (1 Host)")
r = requests.get(SERVER + '/api/v0/cluster/honeynut', auth=AUTH)
print(r.json())
expect = {'status': 'ok', 'hosts': {'total': 1, 'available': 0, 'unavailable': 1}}
expected_json(r.json(), expect) and expected_status(r, 200)

print("=> Verify Host List for Cluster 'honeynut'")
r = requests.get(SERVER + '/api/v0/cluster/honeynut/hosts', auth=AUTH)
print(r.json())
expected_json(r.json(), ['10.2.0.2']) and expected_status(r, 200)

print("=> Verify Host 10.2.0.2 In Cluster 'honeynut'")
r = requests.get(SERVER + '/api/v0/cluster/honeynut/hosts/10.2.0.2', auth=AUTH)
print(r.json())
expected_status(r, 200)

print("=> Deleting Host 10.2.0.2 from Cluster 'honeynut'")
r = requests.delete(SERVER + '/api/v0/cluster/honeynut/hosts/10.2.0.2', auth=AUTH)
print(r.json())
expected_status(r, 200)

print("=> Examining Cluster 'honeynut' (No Hosts)")
r = requests.get(SERVER + '/api/v0/cluster/honeynut', auth=AUTH)
print(r.json())
expect = {'status': 'ok', 'hosts': {'total': 0, 'available': 0, 'unavailable': 0}}
expected_json(r.json(), expect) and expected_status(r, 200)

print("=> Verify Host List for Cluster 'honeynut'")
r = requests.get(SERVER + '/api/v0/cluster/honeynut/hosts', auth=AUTH)
print(r.json())
expected_json(r.json(), []) and expected_status(r, 200)

print("=> Verify Host 10.2.0.2 Not In Cluster 'honeynut'")
r = requests.get(SERVER + '/api/v0/cluster/honeynut/hosts/10.2.0.2', auth=AUTH)
print(r.json())
expected_status(r, 404)

print("=> Directly Set Host List for Cluster 'honeynut' (w/ Malformed Request)")
r = requests.put(
    SERVER + '/api/v0/cluster/honeynut/hosts', auth=AUTH,
    json='Part of this nutritious breakfast!')
print(r.json())
expected_status(r, 400)

print("=> Directly Set Host List for Cluster 'honeynut' (w/ Wrong Prev Value)")
r = requests.put(
    SERVER + '/api/v0/cluster/honeynut/hosts', auth=AUTH,
    json={"old": ["bogus"], "new": ["10.2.0.2"]})
print(r.json())
expected_status(r, 409)

print("=> Verify Host 10.2.0.2 Not In Cluster 'honeynut'")
r = requests.get(SERVER + '/api/v0/cluster/honeynut/hosts/10.2.0.2', auth=AUTH)
print(r.json())
expected_status(r, 404)

print("=> Directly Set Host List for Cluster 'honeynut'")
r = requests.put(
    SERVER + '/api/v0/cluster/honeynut/hosts', auth=AUTH,
    json={"old": [], "new": ["10.2.0.2"]})
print(r.json())
expected_status(r, 200)

print("=> Verify Host 10.2.0.2 In Cluster 'honeynut'")
r = requests.get(SERVER + '/api/v0/cluster/honeynut/hosts/10.2.0.2', auth=AUTH)
print(r.json())
expected_status(r, 200)

print("=> Deleting Host 10.2.0.2 (Implicitly Deleted From Cluster)")
r = requests.delete(SERVER + '/api/v0/host/10.2.0.2', auth=AUTH)
print(r.json())
expected_status(r, 410)

print("=> Examining Cluster 'honeynut' (No Hosts)")
r = requests.get(SERVER + '/api/v0/cluster/honeynut', auth=AUTH)
print(r.json())
expect = {'status': 'ok', 'hosts': {'total': 0, 'available': 0, 'unavailable': 0}}
expected_json(r.json(), expect) and expected_status(r, 200)

print("=> Verify Host List for Cluster 'honeynut'")
r = requests.get(SERVER + '/api/v0/cluster/honeynut/hosts', auth=AUTH)
print(r.json())
expected_json(r.json(), []) and expected_status(r, 200)

print("=> Verify Host 10.2.0.2 Not In Cluster 'honeynut'")
r = requests.get(SERVER + '/api/v0/cluster/honeynut/hosts/10.2.0.2', auth=AUTH)
print(r.json())
expected_status(r, 404)

print("=> Creating Host 10.2.0.3 With Bad Cluster (Should Fail)")
r = requests.put(
    SERVER + '/api/v0/host/10.2.0.3', auth=AUTH,
    json={
        "address": "10.2.0.3",
        "ssh_priv_key": "dGVzdAo=",
        "cluster": "headache"
    })
print(r.json())
expected_status(r, 409)

print("=> Make Sure There Are No New Clusters")
r = requests.get(SERVER + '/api/v0/clusters', auth=AUTH)
print(r.json())
expect = ['honeynut']
expected_json(r.json(), expect) and expected_status(r, 200)

print("=> Creating Host 10.2.0.3 With 'honeynut' Cluster")
r = requests.put(
    SERVER + '/api/v0/host/10.2.0.3', auth=AUTH,
    json={
        "address": "10.2.0.3",
        "ssh_priv_key": "dGVzdAo=",
        "cluster": "honeynut"
    })
print(r.json())
expected_status(r, 201)

print("=> Verify Host 10.2.0.3 In Cluster 'honeynut'")
r = requests.get(SERVER + '/api/v0/cluster/honeynut/hosts/10.2.0.3', auth=AUTH)
print(r.json())
expected_status(r, 200)

print("=> Initiate Cluster Upgrade Without Auth (Should Fail)")
r = requests.put(
    SERVER + '/api/v0/cluster/honeynut/upgrade',
    json={"upgrade_to": "7.2.1"})
print(r.json())
expected_status(r, 403)

print("=> Initiate Cluster Upgrade With Auth")
r = requests.put(
    SERVER + '/api/v0/cluster/honeynut/upgrade', auth=AUTH,
    json={"upgrade_to": "7.2.1"})
actual = r.json()
print(actual)
del actual['started_at']  # Disregard timestamp
expect = {'status': 'in_process', 'upgrade_to': '7.2.1', 'upgraded': [], 'in_process': [], 'finished_at': None}
expected_json(actual, expect) and expected_status(r, 201)

print("=> Query Cluster Upgrade Status Without Auth (Should Fail)")
r = requests.get(SERVER + '/api/v0/cluster/honeynut/upgrade')
print(r.json())
expected_status(r, 403)

# FIXME: Skip GET upgrade status test for now; too racy.

print("=> Initiate Cluster Restart Without Auth (Should Fail)")
r = requests.put(SERVER + '/api/v0/cluster/honeynut/restart')
print(r.json())
expected_status(r, 403)

print("=> Initiate Cluster Restart With Auth")
r = requests.put(SERVER + '/api/v0/cluster/honeynut/restart', auth=AUTH)
actual = r.json()
print(actual)
del actual['started_at']  # Disregard timestamp
expect = {'status': 'in_process', 'restarted': [], 'in_process': [], 'finished_at': None}
expected_json(actual, expect) and expected_status(r, 201)

print("=> Query Cluster Restart Status Without Auth (Should Fail)")
r = requests.get(SERVER + '/api/v0/cluster/honeynut/restart')
print(r.json())
expected_status(r, 403)

# FIXME: Skip GET restart status test for now; too racy.

print("=> Deleting Cluster 'honeynut' Without Auth (Should Fail)")
r = requests.delete(SERVER + '/api/v0/cluster/honeynut')
print(r.json())
expected_status(r, 403)

print("=> Deleting Cluster 'honeynut' With Auth")
r = requests.delete(SERVER + '/api/v0/cluster/honeynut', auth=AUTH)
print(r.json())
expected_status(r, 410)
