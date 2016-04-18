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
Configuration.
"""

import logging

import etcd


class Config(dict):
    """
    Configuration container.
    """

    def __init__(self, listen={}, etcd={}, kubernetes={}):
        """
        Creates an instance of the Config class.

        :param listen: Structure containing the server listening data.
        :type listen: dict
        :param etcd: Structure containing the etcd connection data.
        :type etcd: dict
        :param kubernetes: Structure containing the kubernetes connection data.
        :type kubernets: dict
        :returns: commissaire.config.Config
        """
        self.listen = listen
        self.etcd = etcd
        self.kubernetes = kubernetes


def cli_etcd_or_default(name, cli, default, ds):
    """
    Returns the value for an option in the following order:
    CLI switch, etcd value, default.

    :param name: The name of the switch/etcd key.
    :type name: str
    :param cli: The argparse value.
    :param default: The default value if CLI and etcd have no values.
    :param ds: Etcd client
    :type ds: etcd.Client
    """
    result = None
    if cli:
        result = cli
        logging.info('Using CLI for {0} configuration.'.format(name))
    else:
        try:
            result = ds.get('/commissaire/config/{0}'.format(name)).value
            logging.info('Using Etcd for {0} configuration.'.format(name))
        except etcd.EtcdKeyNotFound:
            logging.info(
                'No CLI or etcd defined for {0}.'
                ' Using default of {1}.'.format(name, default))
            result = default
    return result
