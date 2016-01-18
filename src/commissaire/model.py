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


import json


class Model:
    """
    Parent class for models.
    """
    _json_type = None
    _attributes = ()
    _hidden_attributes = ()

    def __init__(self, **kwargs):
        for key in self._attributes:
            if key not in kwargs:
                raise TypeError(
                    '__init__() missing 1 or more required '
                    'keyword arguments: {0}'.format(
                        ', '.join(self._attributes)))
            setattr(self, key, kwargs[key])

    def _struct_for_json(self, secure=False):
        if self._json_type is dict:
            return self._dict_for_json(secure)
        elif self._json_type is list:
            return self._list_for_json(secure)

    def _list_for_json(self, secure):
        if len(self._attributes) == 1:
            data = getattr(self, self._attributes[0])
        return data

    def _dict_for_json(self, secure):
        data = {}
        for key in self._attributes:
            if secure:
                data[key] = getattr(self, key)
            elif key not in self._hidden_attributes:
                data[key] = getattr(self, key)
        return data

    def to_json(self, secure=False):
        return json.dumps(
            self._struct_for_json(secure=secure),
            default=lambda o: o._struct_for_json(secure=secure))
