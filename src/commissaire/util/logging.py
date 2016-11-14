# Copyright (C) 2016  Port.direct, Ltd
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
Logging utils.
"""
import logging


def setup_logging(config, components):
    if config.debug:
        logging_debug = True
    else:
        logging_debug = False

    if 'logging_levels' in config:
        logging_components = config.logging_levels
    else:
        logging_components = {}

    for name in components:
        if name not in logging_components:
            component_log_opts = {}
            component_log_opts['level'] = 'INFO'
            logging_components[name] = component_log_opts

    if 'logging_format' in config:
        logging_format = config.logging_format
    else:
        logging_format = '%(name)s(%(levelname)s): %(message)s'

    apply_logging(logging_components, logging_format, logging_debug)


def apply_logging(components, log_format, logging_debug):
    for name, opts in components.items():
        if 'format' in opts:
            log_format = opts['format']
        logger = logging.getLogger(name)
        if not logging_debug:
            log_level = logging.getLevelName(opts['level'])
        else:
            log_level = logging.getLevelName('DEBUG')
        logger.setLevel(log_level)

        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(log_format))
        logger.handlers.append(handler)
