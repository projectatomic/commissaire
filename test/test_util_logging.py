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

from argparse import Namespace
from copy import deepcopy
from logging import INFO, DEBUG
from unittest import mock

from . import TestCase

from commissaire.util import logging

#: Component names to use in tests
COMPONENTS = (
    'one',
    'two',
)
#: Default logging copomponents when needed in tests
DEFAULT_LOGGING_COMPONENTS = {
    'two': {
        'level': 'INFO'
    },
    'one': {
        'level': 'INFO'
    },
}
#: Default format to use when format needs to be modified
CHANGED_FORMAT = '%(msg)s'


class Test_setup_logging(TestCase):
    """
    Tests the setup_logging function.
    """

    def test_setup_logging_with_components(self):
        """
        Test setup_logging with components.
        """
        for debug in (True, False):
            config = Namespace(debug=debug)

            with mock.patch('commissaire.util.logging.apply_logging') as _al:
                logging.setup_logging(config, COMPONENTS)
                _al.assert_called_once_with(
                    DEFAULT_LOGGING_COMPONENTS, mock.ANY, debug)

    def test_setup_logging_with_components_and_format(self):
        """
        Test setup_logging with components and format.
        """
        config = Namespace(debug=False, logging_format=CHANGED_FORMAT)

        with mock.patch('commissaire.util.logging.apply_logging') as _al:
            logging.setup_logging(config, COMPONENTS)
            _al.assert_called_once_with(
                DEFAULT_LOGGING_COMPONENTS, CHANGED_FORMAT, False)

    def test_setup_logging_with_components_and_logging_levels(self):
        """
        Test setup_logging with components and format.
        """
        config = Namespace(
            logging_levels={
                'one': {
                    'level': 'DEBUG',
                }
            }, debug=False)

        with mock.patch('commissaire.util.logging.apply_logging') as _al:
            logging.setup_logging(config, COMPONENTS)
            _al.assert_called_once_with(
                {'two': {'level': 'INFO'}, 'one': {'level': 'DEBUG'}},
                mock.ANY, False)


class Test_apply_logging(TestCase):
    """
    Tests the apply_logging function.
    """

    def test_apply_logging_with_format(self):
        """
        Test apply_logging.
        """
        logging_components = deepcopy(DEFAULT_LOGGING_COMPONENTS)
        del logging_components['two']
        logging_components['one']['format'] = CHANGED_FORMAT

        for debug in (True, False):
            with mock.patch('logging.getLogger') as _gl, \
                    mock.patch('logging.Formatter') as _lf:
                _logger = _gl()
                # Make the call
                logging.apply_logging(logging_components, 'DEFAULT', debug)
                LEVEL = INFO
                if debug:
                    LEVEL = DEBUG
                # Ensure the logger calls are what we expect
                _logger.setLevel.assert_called_once_with(LEVEL)
                _lf.assert_called_once_with(CHANGED_FORMAT)

    def test_apply_logging_without_format(self):
        """
        Test apply_logging without format.
        """
        logging_components = deepcopy(DEFAULT_LOGGING_COMPONENTS)
        del logging_components['two']
        default_format = 'DEFAULT'

        for debug in (True, False):
            with mock.patch('logging.getLogger') as _gl, \
                    mock.patch('logging.Formatter') as _lf:
                _logger = _gl()
                # Make the function call
                logging.apply_logging(
                    logging_components, default_format, debug)
                LEVEL = INFO
                if debug:
                    LEVEL = DEBUG
                # Ensure the logger calls are what we expect
                _logger.setLevel.assert_called_once_with(LEVEL)
                _lf.assert_called_once_with(default_format)
