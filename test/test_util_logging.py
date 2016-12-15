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
Test cases for the commissaire.util.logging module.
"""

from copy import deepcopy
from unittest import mock

from . import TestCase

from commissaire.util import logging

DEFAULT_CONFIG = {
    'formatters': {
        'default': {
            'format': logging.DEFAULT_FORMAT,
        }
    },
    'handlers': {
        'default': {
            'class': 'logging.StreamHandler',
            'formatter': 'default'
        }
    },
    'root': {
        'handlers': ['default']
    }
}

class Test_setup_logging(TestCase):
    """
    Tests the setup_logging function.
    """

    def test_setup_logging_default(self):
        """
        Test setup_logging with default configuration.
        """
        with mock.patch('logging.config.dictConfig') as dc:
            config = {}
            logging.setup_logging(config)
            dc.assert_called_once_with(DEFAULT_CONFIG)

    def test_setup_logging_with_formatter(self):
        """
        Test setup_logging does not overwrite a custom formatter.
        """
        with mock.patch('logging.config.dictConfig') as dc:
            config = {
                'formatters': {
                    'default': {
                        'format': '%(asctime)s: %(message)s'
                    }
                }
            }
            expected = deepcopy(DEFAULT_CONFIG)
            expected.update(config)
            logging.setup_logging(config)
            dc.assert_called_once_with(expected)

    def test_setup_logging_with_handler(self):
        """
        Test setup_logging does not overwrite a custom handler.
        """
        with mock.patch('logging.config.dictConfig') as dc:
            config = {
                'handlers': {
                    'default': {
                        'class': 'logging.handlers.RotatingFileHandler',
                        'formatter': 'default',
                        'filename': 'commissaire.log'
                    }
                }
            }
            expected = deepcopy(DEFAULT_CONFIG)
            expected.update(config)
            logging.setup_logging(config)
            dc.assert_called_once_with(expected)

    def test_setup_logging_with_root_logger(self):
        """
        Test setup_logging does not duplicate root logger handler.
        """
        with mock.patch('logging.config.dictConfig') as dc:
            config = {
                'root': {
                    'handlers': ['default']
                }
            }
            logging.setup_logging(config)
            dc.assert_called_once_with(DEFAULT_CONFIG)
