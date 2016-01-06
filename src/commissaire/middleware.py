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


class JSONify:

    # def process_request(self, req, resp):

    def process_response(self, req, resp, resource):
        if 'model' in req.context.keys() and resp.body is None:
            try:
                resp.body = req.context['model'].to_json()
            except:
                # TODO unable to encode json ...
                pass

        # Never send 'None'
        if resp.body is None:
            resp.body = '{}'
