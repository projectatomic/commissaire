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
Configuration related classes.
"""

import json


class ConfigurationError(Exception):
    """
    Exception class for user configuration errors.
    """
    pass


def _normalize_member_names(json_object):
    """
    Normalize member names by converting hyphens to underscores.

    :param json_object: Dictionary to normalize.
    :type json_object: dict
    :returns: A normalized dictionary.
    :rtype: dict
    """
    normalized = {}
    for k, v in json_object.items():
        k = k.replace('-', '_')
        if isinstance(v, dict):
            v = _normalize_member_names(v)
        normalized[k] = v
    return normalized


def read_config_file(path=None):
    """
    Attempts to parse a configuration file, formatted as a JSON object.

    If a config file path is explicitly given, then failure to open the
    file will raise an IOError.  Otherwise a default path is tried, but
    no IOError is raised on failure.  If the file can be opened but not
    parsed, an exception is always raised.

    :param path: Full path to the config file, or None
    :type path: str or None
    :returns: configuration content as a dictionary
    :rtype: dict
    :raises: IOError, TypeError, ValueError
    """
    json_object = {}
    using_default = False

    if path is None:
        path = '/etc/commissaire/commissaire.conf'
        using_default = True

    try:
        with open(path, 'r') as fp:
            json_object = json.load(fp)
        if using_default:
            print('Using configuration in {0}'.format(path))
    except IOError:
        if not using_default:
            raise

    if type(json_object) is not dict:
        raise TypeError(
            '{0}: File content must be a JSON object'.format(path))

    # Recursively normalize the JSON member names.
    json_object = _normalize_member_names(json_object)

    # Special case:
    #
    # In the configuration file, the "authentication_plugin" member
    # can also be specified as a JSON object.  The object must have
    # at least a 'name' member specifying the plugin module name.
    auth_key = 'authentication_plugin'
    auth_plugin = json_object.get(auth_key)
    if type(auth_plugin) is dict:
        if 'name' not in auth_plugin:
            raise ValueError(
                '{0}: "{1}" is missing a "name" member'.format(
                    path, auth_key))
        # Since it's valid we can parse it down into the expected
        # format for loading.
        auth_plugin_name = json_object[auth_key].pop('name')
        json_object[auth_key + '_kwargs'] = json_object[auth_key]
        json_object[auth_key] = auth_plugin_name

    # Special case:
    #
    # In the configuration file, the "storage_handlers" member can
    # be specified as a JSON object or a list of JSON objects.
    handler_key = 'storage_handlers'
    handler_list = json_object.get(handler_key)
    if type(handler_list) is dict:
        json_object[handler_key] = [handler_list]

    return json_object
