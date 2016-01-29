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
Ansible API transport.
"""

import logging

from collections import namedtuple

from ansible.parsing.dataloader import DataLoader
from ansible.vars import VariableManager
from ansible.inventory import Inventory, Host, Group
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.plugins.callback import CallbackBase


class LogForward(CallbackBase):
    """
    Forwards Ansible's output into a logger.
    """
    #: Version required for this callback
    CALLBACK_VERSION = 2.0
    #: Kind of callback
    CALLBACK_TYPE = 'log'
    #: Name of the callback
    CALLBACK_NAME = 'logforward'
    #: Does it require a callback
    CALLBACK_NEEDS_WHITELIST = False

    def __init__(self):
        """
        Creates the instance and sets the logger.
        """
        super(LogForward, self).__init__()
        self.log = logging.getLogger('transport')

    def v2_runner_on_failed(self, result, *args, **kwargs):
        """
        Called when the runner failed.

        :param result: Ansible's result.
        :type result: ansible.executor.task_result.TaskResult
        :param args: All other ignored non-keyword arguments.
        :type args: tuple
        :param kwargs: All other ignored keyword arguments.
        :type kwargs: dict
        """
        exception = result._result.get('exception', 'No Exception')
        self.log.warn(
            'An exception occurred: {0}\n'.format(exception))

    def v2_runner_on_ok(self, result):
        """
        Called when everything went smoothly.

        :param result: Ansible's result.
        :type result: ansible.executor.task_result.TaskResult
        """
        self._clean_results(result._result, result._task.action)
        self.log.info('SUCCESS {0}'.format(result._host.get_name()))

    def v2_runner_on_skipped(self, result):
        """
        Called when ansible skips a host.

        :param result: Ansible's result.
        :type result: ansible.executor.task_result.TaskResult
        """
        self.log.warn('SKIPPED {0}'.format(result._host.get_name()))

    def v2_runner_on_unreachable(self, result):
        """
        Called when a host can not be reached.

        :param result: Ansible's result.
        :type result: ansible.executor.task_result.TaskResult
        """
        self.log.warn('UNREACHABLE {0}'.format(
            result._host.get_name(),
            result._result))


class Transport:
    """
    Transport using Ansible.
    """

    def __init__(self):
        """
        Creates an instance of the Transport.
        """
        self.logger = logging.getLogger('transport')
        self.Options = namedtuple(
            'Options', ['connection', 'module_path', 'forks', 'remote_user',
                        'private_key_file', 'ssh_common_args',
                        'ssh_extra_args', 'sftp_extra_args', 'scp_extra_args',
                        'become', 'become_method', 'become_user', 'verbosity',
                        'check'])
        # initialize needed objects
        self.variable_manager = VariableManager()
        self.loader = DataLoader()
        self.passwords = {}

    def _run(self, ip, key_file, play_source):
        """
        Common code used for each run.

        :param ip: IP address to check.
        :type ip: str
        :param key_file: Full path the the file holding the private SSH key.
        :type key_file: string
        :param play_source: Ansible play.
        :type play_source: dict
        :returns: Ansible exit code
        :type: int
        """
        options = self.Options(
            connection='ssh', module_path=None, forks=1,
            remote_user='root', private_key_file=key_file,
            ssh_common_args=None, ssh_extra_args=None,
            sftp_extra_args=None, scp_extra_args=None,
            become=None, become_method=None, become_user=None,
            verbosity=None, check=False)
        # create inventory and pass to var manager
        inventory = Inventory(
            loader=self.loader,
            variable_manager=self.variable_manager,
            host_list=ip)
        # TODO: Fix this ... weird but works
        group = Group(ip)
        group.add_host(Host(ip, 22))
        inventory.groups.update({ip: group})
        # ---

        self.variable_manager.set_inventory(inventory)
        play = Play().load(
            play_source,
            variable_manager=self.variable_manager,
            loader=self.loader)
        # actually run it
        tqm = None
        try:
            tqm = TaskQueueManager(
                inventory=inventory,
                variable_manager=self.variable_manager,
                loader=self.loader,
                options=options,
                passwords=self.passwords,
                stdout_callback=LogForward(),
            )
            result = tqm.run(play)
        finally:
            if tqm is not None:
                tqm.cleanup()
        return result

    def upgrade(self, ip, key_file, oscmd):
        """
        Upgrades a host via ansible.

        :param ip: IP address to upgrade.
        :type ip: str
        :param key_file: Full path the the file holding the private SSH key.
        :param oscmd: OSCmd instance to use
        :type oscmd: commissaire.oscmd.OSCmdBase
        :type key_file: str
        :returns: tuple -- (exitcode(int), facts(dict)).
        """
        # TODO: Use ansible to do multiple hosts...
        play_source = {
            'name': 'upgrade',
            'hosts': ip,
            'gather_facts': 'no',
            'tasks': [{
                'action': {
                    'module': 'command',
                    'args': " ".join(oscmd.upgrade())
                }
            }]
        }
        result = self._run(ip, key_file, play_source)
        if result == 0:
            fact_cache = self.variable_manager._fact_cache[ip] = {}
            return (result, fact_cache)
        # TODO: Do something :-)
        raise Exception('Can not upgrade {0}'.format(ip))

    def restart(self, ip, key_file, oscmd):
        """
        Restarts a host via ansible.

        :param ip: IP address to reboot.
        :type ip: str
        :param key_file: Full path the the file holding the private SSH key.
        :type key_file: str
        :param oscmd: OSCmd instance to use
        :type oscmd: commissaire.oscmd.OSCmdBase
        :returns: tuple -- (exitcode(int), facts(dict)).
        """
        # TODO: Use ansible to do multiple hosts...
        play_source = {
            'name': 'reboot',
            'hosts': ip,
            'gather_facts': 'no',
            'tasks': [{
                'action': {
                    'module': 'command',
                    'args': " ".join(oscmd.restart())
                }
            }]
        }
        result = self._run(ip, key_file, play_source)
        if result in (0, 2):  # OK and Connection broken
            result = 0  # Set result to 0 as it actually did reboot
            fact_cache = self.variable_manager._fact_cache[ip] = {}
            return (result, fact_cache)
        # TODO: Do something :-)
        raise Exception('Can not reboot {0}'.format(ip))

    def get_info(self, ip, key_file):
        """
        Get's information from the host via ansible.

        :param ip: IP address to check.
        :type ip: str
        :param key_file: Full path the the file holding the private SSH key.
        :type key_file: str
        :returns: tuple -- (exitcode(int), facts(dict)).
        """
        # create play with tasks
        play_source = {
            'name': 'gather',
            'hosts': ip,
            'gather_facts': 'yes',
            'tasks': []

        }
        result = self._run(ip, key_file, play_source)
        if result == 0:
            fact_cache = self.variable_manager._fact_cache[ip]
            facts = {}
            facts['os'] = fact_cache['ansible_distribution'].lower()
            facts['cpus'] = fact_cache['ansible_processor_cores']
            facts['memory'] = fact_cache['ansible_memory_mb']['real']['total']
            space = 0
            for x in fact_cache['ansible_mounts']:
                space += x['size_total']
            facts['space'] = space

            return (result, facts)
        # TODO: Make specific exceptions
        raise Exception('Can not get info for {0}'.format(ip))
