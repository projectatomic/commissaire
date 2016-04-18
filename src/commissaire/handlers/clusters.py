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
"""
Cluster(s) handlers.
"""

import datetime
import json

import cherrypy
import falcon

from multiprocessing import Process

from commissaire.resource import Resource
from commissaire.jobs.clusterexec import clusterexec
from commissaire.handlers.models import (
    Cluster, Clusters, ClusterRestart, ClusterUpgrade, Host)

import commissaire.handlers.util as util


class ClustersResource(Resource):
    """
    Resource for working with Clusters.
    """

    def on_get(self, req, resp):
        """
        Handles GET requests for Clusters.

        :param req: Request instance that will be passed through.
        :type req: falcon.Request
        :param resp: Response instance that will be passed through.
        :type resp: falcon.Response
        """
        clusters_dir, error = cherrypy.engine.publish(
            'store-get', '/commissaire/clusters/')[0]
        if error:
            self.logger.warn(
                'Etcd does not have any clusters. Returning [] and 404.')
            resp.status = falcon.HTTP_404
            req.context['model'] = None
            return

        results = []
        # Don't let an empty clusters directory through
        if len(clusters_dir._children):
            for cluster in clusters_dir.leaves:
                results.append(cluster.key.split('/')[-1])
            resp.status = falcon.HTTP_200
            req.context['model'] = Clusters(clusters=results)
        else:
            self.logger.debug(
                'Etcd has a clusters directory but no content.')
            resp.status = falcon.HTTP_200
            req.context['model'] = None


class ClusterResource(Resource):
    """
    Resource for working with a single Cluster.
    """

    def _calculate_hosts(self, cluster):
        """
        Calculates the hosts metadata for the cluster.

        :param cluster: The name of the cluster.
        :type cluster: str
        """
        # XXX: Not sure which wil be more efficient: fetch all
        #      the host data in one etcd call and sort through
        #      them, or fetch the ones we need individually.
        #      For the MVP phase, fetch all is better.
        etcd_resp, error = cherrypy.engine.publish(
            'store-get', '/commissaire/hosts')[0]

        if error:
            self.logger.warn(
                'Etcd does not have any hosts. '
                'Cannot determine cluster stats.')
            return

        available = unavailable = total = 0
        for child in etcd_resp._children:
            host = Host(**json.loads(child['value']))
            if host.address in cluster.hostset:
                total += 1
                if host.status == 'active':
                    available += 1
                else:
                    unavailable += 1

        cluster.hosts['total'] = total
        cluster.hosts['available'] = available
        cluster.hosts['unavailable'] = unavailable

    def on_get(self, req, resp, name):
        """
        Handles retrieval of an existing Cluster.

        :param req: Request instance that will be passed through.
        :type req: falcon.Request
        :param resp: Response instance that will be passed through.
        :type resp: falcon.Response
        :param name: The name of the Cluster being requested.
        :type name: str
        """
        key = util.etcd_cluster_key(name)
        etcd_resp, error = cherrypy.engine.publish('store-get', key)[0]

        if error:
            resp.status = falcon.HTTP_404
            return

        cluster = Cluster(**json.loads(etcd_resp.value))

        if not cluster:
            resp.status = falcon.HTTP_404
            return

        self._calculate_hosts(cluster)
        # Have to set resp.body explicitly to include Hosts.
        resp.body = cluster.to_json_with_hosts()
        resp.status = falcon.HTTP_200

    def on_put(self, req, resp, name):
        """
        Handles the creation of a new Cluster.

        :param req: Request instance that will be passed through.
        :type req: falcon.Request
        :param resp: Response instance that will be passed through.
        :type resp: falcon.Response
        :param name: The name of the Cluster being created.
        :type name: str
        """
        # PUT is idempotent, and since there's no body to this request,
        # there's nothing to conflict with.  The request should always
        # succeed, even if we didn't actually do anything.
        if util.etcd_cluster_exists(name):
            self.logger.info(
                'Creation of already exisiting cluster {0} requested.'.format(
                    name))
        else:
            key = util.etcd_cluster_key(name)
            cluster = Cluster(status='ok', hostset=[])
            etcd_resp, _ = cherrypy.engine.publish(
                'store-save', key, cluster.to_json(secure=True))[0]
            self.logger.info(
                'Created cluster {0} per request.'.format(name))
            self.logger.debug('Etcd Response: {0}'.format(etcd_resp))
        resp.status = falcon.HTTP_201

    def on_delete(self, req, resp, name):
        """
        Handles the deletion of a Cluster.

        :param req: Request instance that will be passed through.
        :type req: falcon.Request
        :param resp: Response instance that will be passed through.
        :type resp: falcon.Response
        :param name: The name of the Cluster being deleted.
        :type name: str
        """
        resp.body = '{}'
        if not util.etcd_cluster_exists(name):
            self.logger.info(
                'Deleting for non-existent cluster {0} requested.'.format(
                    name))
            resp.status = falcon.HTTP_404
        else:
            self.store.delete(util.etcd_cluster_key(name))
            resp.status = falcon.HTTP_200
            self.logger.info(
                'Deleted cluster {0} per request.'.format(name))


class ClusterHostsResource(Resource):
    """
    Resource for managing host membership in a Cluster.
    """

    def on_get(self, req, resp, name):
        """
        Handles GET requests for Cluster hosts.

        :param req: Request instance that will be passed through.
        :type req: falcon.Request
        :param resp: Response instance that will be passed through.
        :type resp: falcon.Response
        :param name: The name of the Cluster being requested.
        :type name: str
        """
        cluster = util.get_cluster_model(name)
        if not cluster:
            resp.status = falcon.HTTP_404
            return

        resp.body = json.dumps(cluster.hostset)
        resp.status = falcon.HTTP_200

    def on_put(self, req, resp, name):
        """
        Handles PUT requests for Cluster hosts.
        This replaces the entire host list for a Cluster.

        :param req: Request instance that will be passed through.
        :type req: falcon.Request
        :param resp: Response instance that will be passed through.
        :type resp: falcon.Response
        :param name: The name of the Cluster being requested.
        :type name: str
        """
        try:
            req_body = json.loads(req.stream.read().decode())
            old_hosts = set(req_body['old'])  # Ensures no duplicates
            new_hosts = set(req_body['new'])  # Ensures no duplicates
        except (KeyError, TypeError):
            self.logger.info(
                'Bad client PUT request for cluster {0}: {1}'.
                format(name, req_body))
            resp.status = falcon.HTTP_400
            return

        cluster = util.get_cluster_model(name)
        if not cluster:
            resp.status = falcon.HTTP_404
            return

        # old_hosts must match current hosts to accept new_hosts.
        # Note: Order doesn't matter, so etcd's atomic comparison
        #       of the raw values would be too strict.
        if old_hosts != set(cluster.hostset):
            self.logger.info(
                'Conflict setting hosts for cluster {0}'.format(name))
            resp.status = falcon.HTTP_409
            return

        # FIXME: Need input validation.  For each new host,
        #        - Does the host exist at /commissaire/hosts/{IP}?
        #        - Does the host already belong to another cluster?

        # FIXME: Should guard against races here, since we're fetching
        #        the cluster record and writing it back with some parts
        #        unmodified.  Use either locking or a conditional write
        #        with the etcd 'modifiedIndex'.  Deferring for now.

        cluster.hostset = list(new_hosts)
        cherrypy.engine.publish(
            'store-save', cluster.etcd.key, cluster.to_json(secure=True))
        resp.status = falcon.HTTP_200


class ClusterSingleHostResource(ClusterHostsResource):
    """
    Resource for managing a single host's membership in a Cluster.
    """

    def on_get(self, req, resp, name, address):
        """
        Handles GET requests for individual hosts in a Cluster.
        This is a membership test, returning 200 OK if the host
        address is part of the cluster, or else 404 Not Found.

        :param req: Request instance that will be passed through.
        :type req: falcon.Request
        :param resp: Response instance that will be passed through.
        :type resp: falcon.Response
        :param name: The name of the Cluster being requested.
        :type name: str
        :param address: The address of the Host being requested.
        :type address: str
        """
        cluster = util.get_cluster_model(name)
        if not cluster:
            resp.status = falcon.HTTP_404
            return

        if address in cluster.hostset:
            resp.status = falcon.HTTP_200
        else:
            resp.status = falcon.HTTP_404

    def on_put(self, req, resp, name, address):
        """
        Handles PUT requests for individual hosts in a Cluster.
        This adds a single host to the cluster, idempotently.

        :param req: Request instance that will be passed through.
        :type req: falcon.Request
        :param resp: Response instance that will be passed through.
        :type resp: falcon.Response
        :param name: The name of the Cluster being requested.
        :type name: str
        :param address: The address of the Host being requested.
        :type address: str
        """
        try:
            util.etcd_cluster_add_host(name, address)
            resp.status = falcon.HTTP_200
        except KeyError:
            resp.status = falcon.HTTP_404

    def on_delete(self, req, resp, name, address):
        """
        Handles DELETE requests for individual hosts in a Cluster.
        This removes a single host from the cluster, idempotently.

        :param req: Request instance that will be passed through.
        :type req: falcon.Request
        :param resp: Response instance that will be passed through.
        :type resp: falcon.Response
        :param name: The name of the Cluster being requested.
        :type name: str
        :param address: The address of the Host being requested.
        :type address: str
        """
        try:
            util.etcd_cluster_remove_host(name, address)
            resp.status = falcon.HTTP_200
        except KeyError:
            resp.status = falcon.HTTP_404


class ClusterRestartResource(Resource):
    """
    Resource for initiating or querying a Cluster restart.
    """

    def on_get(self, req, resp, name):
        """
        Handles GET (or "status") requests for a Cluster restart.

        :param req: Request instance that will be passed through.
        :type req: falcon.Request
        :param resp: Response instance that will be passed through.
        :type resp: falcon.Response
        :param name: The name of the Cluster being restarted.
        :type name: str
        """
        key = '/commissaire/cluster/{0}/restart'.format(name)
        if not util.etcd_cluster_exists(name):
            self.logger.info(
                'Restart GET requested for nonexistent cluster {0}'.format(
                    name))
            resp.status = falcon.HTTP_404
            return
        status, error = cherrypy.engine.publish('store-get', key)[0]
        self.logger.debug('Etcd Response: {0}'.format(status))
        if error:
            # Return "204 No Content" if we have no status,
            # meaning no restart is in progress.  The client
            # can't be expected to know that, so it's not a
            # client error (4xx).
            self.logger.debug((
                'Restart GET requested for {0} but no restart '
                'has ever been executed.').format(name))
            resp.status = falcon.HTTP_204
            return
        resp.status = falcon.HTTP_200
        req.context['model'] = ClusterRestart(**json.loads(status.value))

    def on_put(self, req, resp, name):
        """
        Handles PUT (or "initiate") requests for a Cluster restart.

        :param req: Request instance that will be passed through.
        :type req: falcon.Request
        :param resp: Response instance that will be passed through.
        :type resp: falcon.Response
        :param name: The name of the Cluster being restarted.
        :type name: str
        """
        # Make sure the cluster name is valid.
        if not util.etcd_cluster_exists(name):
            self.logger.info(
                'Restart PUT requested for nonexistent cluster {0}'.format(
                    name))
            resp.status = falcon.HTTP_404
            return

        # If the operation is already in progress, return the current
        # status with response code 200 OK.
        key = '/commissaire/cluster/{0}/restart'.format(name)
        etcd_resp, error = cherrypy.engine.publish('store-get', key)[0]
        if not error:
            self.logger.debug('Etcd Response: {0}'.format(etcd_resp))
            cluster_restart = ClusterRestart(**json.loads(etcd_resp.value))
            if not cluster_restart.finished_at:
                self.logger.debug(
                    'Cluster {0} restart already in progress'.format(name))
                resp.status = falcon.HTTP_200
                req.context['model'] = cluster_restart
                return

        # TODO: Move to a poll?
        p = Process(target=clusterexec, args=(name, 'restart'))
        p.start()

        self.logger.debug('Started restart in clusterexecpool for {0}'.format(
            name))
        cluster_restart_default = {
            'status': 'in_process',
            'restarted': [],
            'in_process': [],
            'started_at': datetime.datetime.utcnow().isoformat(),
            'finished_at': None
        }
        cluster_restart = ClusterRestart(**cluster_restart_default)
        cherrypy.engine.publish('store-save', key, cluster_restart.to_json())
        resp.status = falcon.HTTP_201
        req.context['model'] = cluster_restart


class ClusterUpgradeResource(Resource):
    """
    Resource for initiating or querying a Cluster upgrade.
    """

    def on_get(self, req, resp, name):
        """
        Handles GET (or "status") requests for a Cluster upgrade.

        :param req: Request instance that will be passed through.
        :type req: falcon.Request
        :param resp: Response instance that will be passed through.
        :type resp: falcon.Response
        :param name: The name of the Cluster being upgraded.
        :type name: str
        """
        key = '/commissaire/cluster/{0}/upgrade'.format(name)
        if not util.etcd_cluster_exists(name):
            self.logger.info(
                'Upgrade GET requested for nonexistent cluster {0}'.format(
                    name))
            resp.status = falcon.HTTP_404
            return

        status, error = cherrypy.engine.publish('store-get', key)[0]
        self.logger.debug('Etcd Response: {0}'.format(status))

        if error:
            # Return "204 No Content" if we have no status,
            # meaning no upgrade is in progress.  The client
            # can't be expected to know that, so it's not a
            # client error (4xx).
            self.logger.debug((
                'Upgrade GET requested for {0} but no upgrade '
                'has ever been executed.').format(name))
            resp.status = falcon.HTTP_204
            return

        resp.status = falcon.HTTP_200
        req.context['model'] = ClusterUpgrade(**json.loads(status.value))

    def on_put(self, req, resp, name):
        """
        Handles PUT (or "initiate") requests for a Cluster upgrade.

        :param req: Request instance that will be passed through.
        :type req: falcon.Request
        :param resp: Response instance that will be passed through.
        :type resp: falcon.Response
        :param name: The name of the Cluster being upgraded.
        :type name: str
        """
        data = req.stream.read().decode()
        try:
            args = json.loads(data)
            upgrade_to = args['upgrade_to']
        except (KeyError, ValueError):
            resp.status = falcon.HTTP_400
            return

        # Make sure the cluster name is valid.
        if not util.etcd_cluster_exists(name):
            self.logger.info(
                'Upgrade PUT requested for nonexistent cluster {0}'.format(
                    name))
            resp.status = falcon.HTTP_404
            return

        # If the operation is already in progress and the requested version
        # matches, return the current status with response code 200 OK.
        # If the requested version conflicts with the operation in progress,
        # return the current status with response code 409 Conflict.
        key = '/commissaire/cluster/{0}/upgrade'.format(name)
        etcd_resp, error = cherrypy.engine.publish('store-get', key)[0]
        self.logger.debug('Etcd Response: {0}'.format(etcd_resp))
        if not error:
            cluster_upgrade = ClusterUpgrade(**json.loads(etcd_resp.value))
            if not cluster_upgrade.finished_at:
                if cluster_upgrade.upgrade_to == upgrade_to:
                    self.logger.debug(
                        'Cluster {0} upgrade to {1} already in progress'.
                        format(name, upgrade_to))
                    resp.status = falcon.HTTP_200
                else:
                    self.logger.debug(
                        'Cluster upgrade to {0} requested while '
                        'upgrade to {1} was already in progress'.
                        format(upgrade_to, cluster_upgrade.upgrade_to))
                    resp.status = falcon.HTTP_409
                req.context['model'] = cluster_upgrade
                return

        # FIXME: How do I pass 'upgrade_to'?
        p = Process(target=clusterexec, args=(name, 'upgrade'))
        p.start()
        self.logger.debug('Started upgrade in clusterexecpool for {0}'.format(
            name))
        cluster_upgrade_default = {
            'status': 'in_process',
            'upgrade_to': upgrade_to,
            'upgraded': [],
            'in_process': [],
            'started_at': datetime.datetime.utcnow().isoformat(),
            'finished_at': None
        }
        cluster_upgrade = ClusterUpgrade(**cluster_upgrade_default)
        cherrypy.engine.publish(
            'store-save', key, cluster_upgrade.to_json())
        resp.status = falcon.HTTP_201
        req.context['model'] = cluster_upgrade
