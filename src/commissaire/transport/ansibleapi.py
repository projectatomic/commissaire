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

import jinja2
import logging
import os
import tempfile

from collections import namedtuple
from pkg_resources import resource_filename

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
        if 'exception' in result._result.keys():
            self.log.warn(
                'An exception occurred for {0}: {1}'.format(
                    result._host.get_name(), result._result['exception']))
            self.log.debug('{0}'.format(result.__dict__))

    def v2_runner_on_ok(self, result):
        """
        Called when everything went smoothly.

        :param result: Ansible's result.
        :type result: ansible.executor.task_result.TaskResult
        """
        self._clean_results(result._result, result._task.action)
        self.log.info('SUCCESS {0}: {1}'.format(
            result._host.get_name(), result._task.get_name().strip()))
        self.log.debug('{0}'.format(result.__dict__))

    def v2_runner_on_skipped(self, result):
        """
        Called when ansible skips a host.

        :param result: Ansible's result.
        :type result: ansible.executor.task_result.TaskResult
        """
        self.log.warn('SKIPPED {0}: {1}'.format(
            result._host.get_name(), result._task.get_name().strip()))
        self.log.debug('{0}'.format(result.__dict__))

    def v2_runner_on_unreachable(self, result):
        """
        Called when a host can not be reached.

        :param result: Ansible's result.
        :type result: ansible.executor.task_result.TaskResult
        """
        self.log.warn('UNREACHABLE {0}: {1}'.format(
            result._host.get_name(), result._task.get_name().strip()))
        self.log.debug('{0}'.format(result.__dict__))

    def v2_playbook_on_task_start(self, task, *args, **kwargs):
        """
        Called on the start of a task.

        :param task: The task being called.
        :type task: ansible.executor.task_executor.Task
        :param args: All other ignored non-keyword arguments.
        :type args: tuple
        :param kwargs: All other ignored keyword arguments.
        :type kwargs: dict
        """
        self.log.info("START TASK: {0}".format(task.get_name().strip()))
        self.log.debug('{0}'.format(task.__dict__))


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

    def _run(self, ip, key_file, play_source, expected_results=[0]):
        """
        Common code used for each run.

        :param ip: IP address to check.
        :type ip: str
        :param key_file: Full path the the file holding the private SSH key.
        :type key_file: string
        :param play_source: Ansible play.
        :type play_source: dict
        :param expected_results: List of expected return codes. Default: [0]
        :type expected_results: list
        :returns: Ansible exit code
        :type: int
        """
        ssh_args = ('-o StrictHostKeyChecking=no -o '
                    'ControlMaster=auto -o ControlPersist=60s')
        options = self.Options(
            connection='ssh', module_path=None, forks=1,
            remote_user='root', private_key_file=key_file,
            ssh_common_args=ssh_args, ssh_extra_args=ssh_args,
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

        if result in expected_results:
            self.logger.debug('{0}: Good result {1}'.format(ip, result))
            fact_cache = self.variable_manager._fact_cache.get(ip, {})
            return (result, fact_cache)

        # TODO: Do something :-)
        self.logger.debug('{0}: Bad result {1}'.format(ip, result))
        raise Exception('Can not run for {0}'.format(ip))

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
        return self._run(ip, key_file, play_source)

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
        return self._run(ip, key_file, play_source, [0, 2])

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
        result, fact_cache = self._run(ip, key_file, play_source)
        facts = {}
        facts['os'] = fact_cache['ansible_distribution'].lower()
        facts['cpus'] = fact_cache['ansible_processor_cores']
        facts['memory'] = fact_cache['ansible_memory_mb']['real']['total']
        space = 0
        for x in fact_cache['ansible_mounts']:
            space += x['size_total']
        facts['space'] = space

        # Special case for atomic: Since Atomic doesn't advertise itself and
        # instead calls itself 'redhat' we need to check for 'atomicos'
        # in other ansible_cmdline facts
        if facts['os'] == 'redhat':
            boot_image = fact_cache.get(
                'ansible_cmdline', {}).get('BOOT_IMAGE', '')
            root_mapper = fact_cache.get('ansible_cmdline', {}).get('root', '')
            if (boot_image.startswith('/ostree/rhel-atomic-host') or
                    'atomicos' in root_mapper):
                facts['os'] = 'atomic'

        return (result, facts)

    def bootstrap(self, ip, key_file, config, oscmd):
        """
        Bootstraps a host via ansible.

        :param ip: IP address to reboot.
        :type ip: str
        :param key_file: Full path the the file holding the private SSH key.
        :type key_file: str
        :param config: Configuration information.
        :type config: commissaire.config.Config
        :param oscmd: OSCmd instance to useS
        :type oscmd: commissaire.oscmd.OSCmdBase
        :returns: tuple -- (exitcode(int), facts(dict)).
        """
        # TODO: Use ansible to do multiple hosts...
        self.logger.debug('Using {0} as the oscmd class for {1}'.format(
            oscmd.os_type, ip))

        # TODO: I'd love to use ansibles "template" but it, as well as copy
        # always fails when used in tasks in 2.0.0.2.
        # Fill out templates
        tpl_loader = jinja2.loaders.FileSystemLoader(
            resource_filename('commissaire', 'data/templates/'))
        tpl_vars = {
            'bootstrap_ip': ip,
            'kubernetes_api_server_host': config.kubernetes['uri'].hostname,
            'kubernetes_api_server_port': config.kubernetes['uri'].port,
            'kubernetes_bearer_token': config.kubernetes['token'],
            'docker_registry_host': '127.0.0.1',  # TODO: Where do we get this?
            'docker_registry_port': 8080,  # TODO: Where do we get this?
            'etcd_host': config.etcd['uri'].hostname,
            'etcd_port': config.etcd['uri'].port,
            'flannel_key': '/atomic01/network'  # TODO: Where do we get this?
        }
        tpl_env = jinja2.Environment()
        configs = {}
        for tpl_name in (
                'docker', 'flanneld', 'kubelet', 'kube_config', 'kubeconfig'):
            f = tempfile.NamedTemporaryFile(prefix=tpl_name, delete=False)
            f.write(tpl_loader.load(tpl_env, tpl_name).render(tpl_vars))
            f.close()
            configs[tpl_name] = f.name

        # ---

        play_source = {
            'name': 'bootstrap',
            'hosts': ip,
            'gather_facts': 'no',
            'tasks': [
                {
                    'name': 'Install Flannel',
                    'action': {
                        'module': 'command',
                        'args': " ".join(oscmd.install_flannel()),
                    }
                },
                {
                    'name': 'Configure Flannel',
                    'action': {
                        'module': 'synchronize',
                        'args': {
                            'dest': oscmd.flanneld_config,
                            'src': configs['flanneld'],
                        }
                    }
                },
                {
                    'name': 'Enable and Start Flannel',
                    'action': {
                        'module': 'service',
                        'args': {
                            'name': oscmd.flannel_service,
                            'enabled': 'yes',
                            'state': 'started',
                        }
                    }
                },
                {
                    'name': 'Install Docker',
                    'action': {
                        'module': 'command',
                        'args': " ".join(oscmd.install_docker()),
                    }
                },
                {
                    'name': 'Configure Docker',
                    'action': {
                        'module': 'synchronize',
                        'args': {
                            'dest': oscmd.docker_config,
                            'src': configs['docker'],
                        }
                    }
                },
                {
                    'name': 'Enable and Start Docker',
                    'action': {
                        'module': 'service',
                        'args': {
                            'name': oscmd.docker_service,
                            'enabled': 'yes',
                            'state': 'started',
                        }
                    }
                },
                {
                    'name': 'Install Kubernetes Node',
                    'action': {
                        'module': 'command',
                        'args': " ".join(oscmd.install_kube()),
                    }
                },
                {
                    'name': 'Configure Kubernetes Node',
                    'action': {
                        'module': 'synchronize',
                        'args': {
                            'dest': oscmd.kubernetes_config,
                            'src': configs['kube_config'],
                        }
                    }
                },
                {
                    'name': 'Add Kubernetes kubeconfig',
                    'action': {
                        'module': 'synchronize',
                        'args': {
                            'dest': oscmd.kubernetes_kubeconfig,
                            'src': configs['kubeconfig'],
                        }
                    }
                },
                {
                    'name': 'Configure Kubernetes kubelet',
                    'action': {
                        'module': 'synchronize',
                        'args': {
                            'dest': oscmd.kubelet_config,
                            'src': configs['kubelet'],
                        }
                    }
                },
                {
                    'name': 'Enable and Start Kubelet',
                    'action': {
                        'module': 'service',
                        'args': {
                            'name': oscmd.kubelet_service,
                            'enabled': 'yes',
                            'state': 'started',
                        }
                    }
                },
                {
                    'name': 'Enable and Start Kube Proxy',
                    'action': {
                        'module': 'service',
                        'args': {
                            'name': oscmd.kubelet_proxy_service,
                            'enabled': 'yes',
                            'state': 'started',
                        }
                    }
                },
            ]
        }

        results = self._run(ip, key_file, play_source, [0])

        # Clean out the temporary configs
        map(os.unlink, configs.values())

        return results
