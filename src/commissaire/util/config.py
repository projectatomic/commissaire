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
import logging

from commissaire.util.logging import setup_logging


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


def read_config_file(path=None, default='/etc/commissaire/commissaire.conf'):
    """
    Attempts to parse a configuration file, formatted as a JSON object.

    If a config file path is explicitly given, then failure to open the
    file will raise an IOError.  Otherwise a default path is tried, but
    no IOError is raised on failure.  If the file can be opened but not
    parsed, an exception is always raised.

    :param path: Full path to the config file, or None
    :type path: str or None
    :param default: The default file path to user
    :type default: str
    :returns: configuration content as a dictionary
    :rtype: dict
    :raises: IOError, TypeError, ValueError
    """
    json_object = {}
    using_default = False

    if path is None:
        path = default
        using_default = True

    try:
        with open(path, 'r') as fp:
            json_object = json.load(fp)
        if using_default:
            print('Using configuration in {}'.format(path))
    except IOError:
        if not using_default:
            raise

    if type(json_object) is not dict:
        raise TypeError(
            '{}: File content must be a JSON object'.format(path))

    # Recursively normalize the JSON member names.
    json_object = _normalize_member_names(json_object)

    # Process any logging configuration straight away.
    # This is NOT included in the returned dictionary.
    if 'logging' in json_object:
        setup_logging(json_object.pop('logging'))

    # Handle the debug log-level option straight away.
    # This is NOT included in the returned dictionary.
    if json_object.pop('debug', False):
        logging.getLogger().setLevel(logging.DEBUG)
        logging.info('Debugging messages enabled')

    # Special case:
    #
    # In the configuration file, the "authentication_plugins" member
    # can also be specified as a list of JSON objects.  Each object must
    # have at least a 'name' member specifying the plugin module name.
    auth_plugins = json_object.get('authentication_plugins', [])
    configured_plugins = {}

    if auth_plugins and not isinstance(auth_plugins, list):
        raise ValueError(
            '{}: "{}" must be a list. Not at {}.'.format(
                path, auth_plugins, type(auth_plugins)))

    for plugin in auth_plugins:
        if isinstance(plugin, dict):
            if 'name' not in plugin.keys():
                raise ValueError(
                    '{}: "{}" is missing a "name" member'.format(
                        path, plugin))
            # Since it's valid we can parse it down into the
            # expected format for loading.
            configured_plugins[plugin.pop('name')] = plugin

    # Overwrite authentication_plugins with the configured_plugins
    json_object['authentication_plugins'] = configured_plugins

    # Special case:
    #
    # In the configuration file, the "storage_handlers" member can
    # be specified as a JSON object or a list of JSON objects.
    handler_key = 'storage_handlers'
    handler_list = json_object.get(handler_key)
    if isinstance(handler_list, dict):
        json_object[handler_key] = [handler_list]

    return json_object
