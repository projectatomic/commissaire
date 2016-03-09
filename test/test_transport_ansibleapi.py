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
"""
Test cases for the commissaire.transport.ansibleapi module.
"""

import logging

from . import TestCase, available_os_types, get_fixture_file_path

from ansible.executor.task_result import TaskResult
from ansible.inventory import Host
from ansible.playbook.task import Task
from commissaire.compat.urlparser import urlparse
from commissaire.config import Config
from commissaire.transport import ansibleapi
from commissaire.oscmd import OSCmdBase, get_oscmd
from mock import MagicMock, patch


class Test_LogForward(TestCase):
    """
    Tests for the LogForward class.
    """

    def before(self):
        """
        Sets up a fresh instance of the class before each run.
        """
        self.logforward = ansibleapi.LogForward()
        self.logger = MagicMock(logging.Logger)
        self.logforward.log = self.logger

    def test_v2_runner_on_failed(self):
        """
        Verify failed results uses the logger.
        """
        result = TaskResult('127.0.0.1', Task(), {'exception': 'error'})
        result._host = MagicMock()
        result._host.get_name.return_value = '127.0.0.1'

        self.logforward.v2_runner_on_failed(result)
        self.assertEqual(1, self.logforward.log.warn.call_count)

    def test_v2_runner_on_ok(self):
        """
        Verify OK results uses the logger.
        """
        result = TaskResult('127.0.0.1', Task(), {})
        result._host = Host('127.0.0.1')

        self.logforward.v2_runner_on_ok(result)
        self.assertEqual(1, self.logforward.log.info.call_count)

    def test_v2_runner_on_skipped(self):
        """
        Verify SKIPPED results uses the logger.
        """
        result = TaskResult('127.0.0.1', Task(), {})
        result._host = Host('127.0.0.1')

        self.logforward.v2_runner_on_skipped(result)
        self.assertEqual(1, self.logforward.log.warn.call_count)

    def test_v2_runner_on_unreachable(self):
        """
        Verify UNREACHABLE results uses the logger.
        """
        result = TaskResult('127.0.0.1', Task(), {})
        result._host = Host('127.0.0.1')

        self.logforward.v2_runner_on_unreachable(result)
        self.assertEqual(1, self.logforward.log.warn.call_count)


class Test_Transport(TestCase):
    """
    Tests for the ansible based Transport.
    """

    def test_get_info(self):
        """
        Verify Transport().get_info works as expected.
        """
        with patch('commissaire.transport.ansibleapi.TaskQueueManager') as _tqm:
            _tqm().run.return_value = 0

            transport = ansibleapi.Transport()
            fact_cache = {
                '10.2.0.2': {
                    'ansible_distribution': 'Fedora',
                    'ansible_processor_cores': 2,
                    'ansible_memory_mb': {
                        'real': {
                            'total': 987654321,
                        }
                    },
                    'ansible_mounts': [{'size_total': 123456789}],
                },
            }
            transport.variable_manager._fact_cache = fact_cache
            result, facts = transport.get_info('10.2.0.2', get_fixture_file_path('test/fake_key'))
            # We should have a successful response
            self.assertEquals(0, result)
            # We should match the expected facts
            self.assertEquals(
                {
                    'os': fact_cache['10.2.0.2']['ansible_distribution'].lower(),
                    'cpus': fact_cache['10.2.0.2']['ansible_processor_cores'],
                    'memory': fact_cache['10.2.0.2']['ansible_memory_mb']['real']['total'],
                    'space': fact_cache['10.2.0.2']['ansible_mounts'][0]['size_total'],
                },
                facts
            )

    def test_bootstrap(self):
        """
        Verify Transport().bootstrap works as expected.
        """
        with patch('commissaire.transport.ansibleapi.TaskQueueManager') as _tqm:
            _tqm().run.return_value = 0

            transport = ansibleapi.Transport()
            transport.variable_manager._fact_cache = {}
            oscmd = MagicMock(OSCmdBase)

            config = Config(
                etcd={
                    'uri': urlparse('http://127.0.0.1:2379'),
                },
                kubernetes={
                    'uri': urlparse('http://127.0.0.1:8080'),
                    'token': 'token',
                }
            )

            result, facts = transport.bootstrap(
                '10.2.0.2', 'test/fake_key', config, oscmd)
            # We should have a successful response
            self.assertEquals(0, result)
            # We should see expected calls
            self.assertEquals(1, oscmd.install_docker.call_count)
            self.assertEquals(1, oscmd.install_kube.call_count)

            # Check 'commissaire_enable_pkg_repos' playbook variable
            # for various operating systems.
            transport = ansibleapi.Transport()
            transport._run = MagicMock()
            transport._run.return_value = (0, {})

            needs_enable_repos = ('redhat', 'rhel')

            for os_type in available_os_types:
                oscmd = get_oscmd(os_type)
                result, facts = transport.bootstrap(
                    '10.2.0.2.', 'test/fake_key', config, oscmd)
                play_vars = transport._run.call_args[0][4]
                command = play_vars['commissaire_enable_pkg_repos']
                if os_type in needs_enable_repos:
                    self.assertIn('subscription-manager repos', command)
                else:
                    self.assertEqual('true', command)  # no-op command
