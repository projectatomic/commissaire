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
import logging.config

DEFAULT_FORMAT = '%(name)s(%(levelname)s): %(message)s'


def setup_logging(config):
    """
    Takes a logging configuration and ensures the root logger has a
    handler named "default", which can be referenced in the logging
    configuration.  Most loggers will defer to this default handler
    implicitly, by way of propagation.  The augmented configuration
    is then handed off to logging.config.dictConfig().

    This function should only be called once at program startup.

    :param config: Logging configuration dictionary
    :type config: dict
    """
    formatters = config.setdefault('formatters', {})
    if 'default' not in formatters:
        formatters['default'] = {
            'format': DEFAULT_FORMAT
        }

    handlers = config.setdefault('handlers', {})
    if 'default' not in handlers:
        handlers['default'] = {
            'class': 'logging.StreamHandler',
            'formatter': 'default'
        }

    root_logger = config.setdefault('root', {})
    root_handlers = root_logger.setdefault('handlers', [])
    if 'default' not in root_handlers:
        root_handlers.append('default')

    logging.config.dictConfig(config)
