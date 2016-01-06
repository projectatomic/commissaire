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

import falcon
import etcd
import json

from commissaire.model import Model
from commissaire.resource import Resource


class Host(Model):
    _json_type = dict
    _attributes = (
        'address', 'status', 'os', 'cpus', 'memory', 'space', 'last_check')


class Hosts(Model):
    _json_type = list
    _attributes = ('hosts', )


class HostsResource(Resource):

    def on_get(self, req, resp):
        hosts_dir = self.store.get('/testing/hosts/')
        results = []
        # Don't let an empty host directory through
        if hosts_dir.value is not None:
            for host in hosts_dir.leaves:
                results.append(Host(**json.loads(host.value)))
            resp.status = falcon.HTTP_200
            req.context['model'] = Hosts(hosts=results)
        else:
            resp.status = falcon.HTTP_200
            req.context['model'] = None


class HostResource(Resource):

    def on_get(self, req, resp, address):
        # TODO: Verify input
        try:
            host = self.store.get('/testing/hosts/{}'.format(address))
        except etcd.EtcdKeyNotFound:
            resp.status = falcon.HTTP_404
            return

        resp.status = falcon.HTTP_200
        host.address = address
        req.context['model'] = Host(**json.loads(host.value))

    def on_put(self, req, resp, address):
        # TODO: Verify input
        try:
            host = self.store.get('/testing/hosts/{}'.format(address))
            resp.status = falcon.HTTP_409
            return
        except etcd.EtcdKeyNotFound:
            data = req.stream.read()
            print(data.decode())
            host = Host(**json.loads(data.decode()))
            new_host = self.store.set(
                '/testing/hosts/{}'.format(address), host.to_json())
            resp.status = falcon.HTTP_201
            req.context['model'] = Host(**json.loads(new_host.value))

    def on_delete(self, req, resp, address):
        resp.body = '{}'
        try:
            host = self.store.delete(
                '/testing/hosts/{}'.format(address))
            falcon.status = falcon.HTTP_410
        except etcd.EtcdKeyNotFound:
            resp.status = falcon.HTTP_404
