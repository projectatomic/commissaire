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
Status handlers.
"""

import cherrypy
import falcon

from commissaire.jobs import PROCS
from commissaire.resource import Resource
from commissaire.handlers.models import Status


class StatusResource(Resource):
    """
    Resource for working with Status.
    """

    def on_get(self, req, resp):
        """
        Handles GET requests for Status.

        :param req: Request instance that will be passed through.
        :type req: falcon.Request
        :param resp: Response instance that will be passed through.
        :type resp: falcon.Response
        """
        # Fail closed
        kwargs = {
            'etcd': {
                'status': 'FAILED',
            },
            'investigator': {
                'status': 'FAILED',
                'info': {
                    'size': 0,
                    'in_use': 0,
                    'errors': [],
                },
            },
        }
        resp.status = falcon.HTTP_503

        # Check etcd connection
        root_dir, error = cherrypy.engine.publish('store-get', '/')[0]
        if not error:
            kwargs['etcd']['status'] = 'OK'
        else:
            self.logger.debug('There is no root directory in etcd...')
            kwargs['etcd']['status'] = 'FAILED'

        # Check investigator proccess
        # XXX: Change investigator if more than 1 process is allowed
        if PROCS['investigator'].is_alive():
            kwargs['investigator']['status'] = 'OK'
            kwargs['investigator']['info']['size'] = 1
            kwargs['investigator']['info']['in_use'] = 1

        self.logger.debug('Status: {0}', kwargs)

        resp.status = falcon.HTTP_200
        req.context['model'] = Status(**kwargs)
