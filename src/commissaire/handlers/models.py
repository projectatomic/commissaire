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
"""
Models for handlers.
"""

import json

from commissaire.model import Model


class Cluster(Model):
    """
    Representation of a Cluster.
    """
    _json_type = dict
    _attributes = ('status', 'hostset')
    _hidden_attributes = ('hostset',)

    def __init__(self, **kwargs):
        Model.__init__(self, **kwargs)
        # Hosts is always calculated, not stored in etcd.
        self.hosts = {'total': 0,
                      'available': 0,
                      'unavailable': 0}

    # FIXME Generalize and move to Model?
    def to_json_with_hosts(self, secure=False):
        data = {}
        for key in self._attributes:
            if secure:
                data[key] = getattr(self, key)
            elif key not in self._hidden_attributes:
                data[key] = getattr(self, key)
        data['hosts'] = self.hosts
        return json.dumps(data)


class ClusterRestart(Model):
    """
    Representation of a Cluster restart operation.
    """
    _json_type = dict
    _attributes = (
        'status', 'restarted', 'in_process',
        'started_at', 'finished_at')


class ClusterUpgrade(Model):
    """
    Representation of a Cluster upgrade operation.
    """
    _json_type = dict
    _attributes = (
        'status', 'upgrade_to', 'upgraded', 'in_process',
        'started_at', 'finished_at')


class Clusters(Model):
    """
    Representation of a group of one or more Clusters.
    """
    _json_type = list
    _attributes = ('clusters',)


class Host(Model):
    """
    Representation of a Host.
    """
    _json_type = dict
    _attributes = (
        'address', 'status', 'os', 'cpus', 'memory',
        'space', 'last_check', 'ssh_priv_key')
    _hidden_attributes = ('ssh_priv_key', )


class Hosts(Model):
    """
    Representation of a group of one or more Hosts.
    """
    _json_type = list
    _attributes = ('hosts', )


class Status(Model):
    """
    Representation of a Host.
    """
    _json_type = dict
    _attributes = (
        'etcd', 'investigator')
