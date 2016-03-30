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

    def _run(self, ips, key_file, play_file,
             expected_results=[0], play_vars={}):
        """
        Common code used for each run.

        :param ips: IP address(es) to check.
        :type ips: str or list
        :param key_file: Full path the the file holding the private SSH key.
        :type key_file: string
        :param play_file: Path to the ansible play file.
        :type play_file: str
        :param expected_results: List of expected return codes. Default: [0]
        :type expected_results: list
        :returns: Ansible exit code
        :type: int
        """
        if type(ips) != list:
            ips = [ips]

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
            host_list=ips)
        self.logger.debug('Options: {0}'.format(options))

        group = Group('commissaire_targets')
        for ip in ips:
            host = Host(ip, 22)
            group.add_host(host)

        inventory.groups.update({'commissaire_targets': group})
        self.logger.debug('Inventory: {0}'.format(inventory))

        self.variable_manager.set_inventory(inventory)

        play_source = self.loader.load_from_file(play_file)[0]
        play = Play().load(
            play_source,
            variable_manager=self.variable_manager,
            loader=self.loader)

        # Add any variables provided into the play
        play.vars.update(play_vars)

        self.logger.debug(
            'Running play for hosts {0}: play={1}, vars={2}'.format(
                ips, play_source, play.vars))

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
                self.logger.debug('Cleaning up after the TaskQueueManager.')
                tqm.cleanup()

        if result in expected_results:
            self.logger.debug('{0}: Good result {1}'.format(ip, result))
            fact_cache = self.variable_manager._fact_cache.get(ip, {})
            return (result, fact_cache)

        self.logger.debug('{0}: Bad result {1}'.format(ip, result))
        raise Exception('Can not run for {0}'.format(ip))

    def upgrade(self, ips, key_file, oscmd):
        """
        Upgrades a host via ansible.

        :param ips: IP address(es) to upgrade.
        :type ips: str or list
        :param key_file: Full path the the file holding the private SSH key.
        :param oscmd: OSCmd class to use
        :type oscmd: commissaire.oscmd.OSCmdBase
        :type key_file: str
        :returns: tuple -- (exitcode(int), facts(dict)).
        """
        play_file = resource_filename(
            'commissaire', 'data/ansible/playbooks/upgrade.yaml')
        return self._run(
            ips, key_file, play_file, [0],
            {'commissaire_upgrade_command': " ".join(oscmd.upgrade())})

    def restart(self, ips, key_file, oscmd):
        """
        Restarts a host via ansible.

        :param ips: IP address(es) to restart.
        :type ips: str or list
        :param key_file: Full path the the file holding the private SSH key.
        :type key_file: str
        :param oscmd: OSCmd class to use
        :type oscmd: commissaire.oscmd.OSCmdBase
        :returns: tuple -- (exitcode(int), facts(dict)).
        """
        play_file = resource_filename(
            'commissaire', 'data/ansible/playbooks/restart.yaml')
        return self._run(
            ips, key_file, play_file, [0, 2],
            {'commissaire_restart_command': " ".join(oscmd.restart())})

    def get_info(self, ip, key_file):
        """
        Get's information from the host via ansible.

        :param ip: IP address to check.
        :type ip: str
        :param key_file: Full path the the file holding the private SSH key.
        :type key_file: str
        :returns: tuple -- (exitcode(int), facts(dict)).
        """
        play_file = resource_filename(
            'commissaire', 'data/ansible/playbooks/get_info.yaml')
        result, fact_cache = self._run(ip, key_file, play_file)
        facts = {}
        facts['os'] = fact_cache['ansible_distribution'].lower()
        facts['cpus'] = fact_cache['ansible_processor_cores']
        facts['memory'] = fact_cache['ansible_memory_mb']['real']['total']
        space = 0
        for x in fact_cache['ansible_mounts']:
            space += x['size_total']
        facts['space'] = space

        # Special case for atomic: Since Atomic doesn't advertise itself
        # and instead calls itself 'redhat' or 'fedora' we need to check
        # for 'atomicos' in other ansible_cmdline facts
        if facts['os'] == 'redhat':
            self.logger.debug(
                'Found os of redhat. Checking for special atomic case...')
            boot_image = fact_cache.get(
                'ansible_cmdline', {}).get('BOOT_IMAGE', '')
            root_mapper = fact_cache.get('ansible_cmdline', {}).get('root', '')
            if (boot_image.startswith('/ostree/rhel-atomic-host') or
                    'atomicos' in root_mapper):
                facts['os'] = 'atomic'
            self.logger.debug('Facts: {0}'.format(facts))
        if facts['os'] == 'fedora':
            self.logger.debug(
                'Found os of fedora. Checking for special atomic case...')
            boot_image = fact_cache.get(
                'ansible_cmdline', {}).get('BOOT_IMAGE', '')
            root_mapper = fact_cache.get('ansible_cmdline', {}).get('root', '')
            if (boot_image.startswith('/ostree/fedora-atomic') or
                    'atomicos' in root_mapper):
                facts['os'] = 'atomic'
            self.logger.debug('Facts: {0}'.format(facts))

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
        :param oscmd: OSCmd class to use
        :type oscmd: commissaire.oscmd.OSCmdBase
        :returns: tuple -- (exitcode(int), facts(dict)).
        """
        self.logger.debug('Using {0} as the oscmd class for {1}'.format(
            oscmd.os_type, ip))

        play_vars = {
            'commissaire_etcd_use_cert': False,
            'commissaire_kubernetes_use_cert': False,
            'commissaire_bootstrap_ip': ip,
            'commissaire_kubernetes_api_server_scheme': config.kubernetes.get(
                'uri').scheme,
            'commissaire_kubernetes_api_server_host': config.kubernetes.get(
                'uri').hostname,
            'commissaire_kubernetes_api_server_port': config.kubernetes.get(
                'uri').port,
            'commissaire_kubernetes_bearer_token': config.kubernetes.get(
                'token', ''),
            # TODO: Where do we get this?
            'commissaire_docker_registry_host': '127.0.0.1',
            # TODO: Where do we get this?
            'commissaire_docker_registry_port': 8080,
            'commissaire_etcd_scheme': config.etcd['uri'].scheme,
            'commissaire_etcd_host': config.etcd['uri'].hostname,
            'commissaire_etcd_port': config.etcd['uri'].port,
            # TODO: Where do we get this?
            'commissaire_flannel_key': '/atomic01/network',
            'commissaire_docker_config_local': resource_filename(
                'commissaire', 'data/templates/docker'),
            'commissaire_flanneld_config_local': resource_filename(
                'commissaire', 'data/templates/flanneld'),
            'commissaire_kubelet_config_local': resource_filename(
                'commissaire', 'data/templates/kubelet'),
            'commissaire_kubernetes_config_local': resource_filename(
                'commissaire', 'data/templates/kube_config'),
            'commissaire_kubeconfig_config_local': resource_filename(
                'commissaire', 'data/templates/kubeconfig'),
            'commissaire_install_libselinux_python': " ".join(
                oscmd.install_libselinux_python()),
            'commissaire_docker_config': oscmd.docker_config,
            'commissaire_flanneld_config': oscmd.flanneld_config,
            'commissaire_kubelet_config': oscmd.kubelet_config,
            'commissaire_kubernetes_config': oscmd.kubernetes_config,
            'commissaire_kubeconfig_config': oscmd.kubernetes_kubeconfig,
            'commissaire_install_flannel': " ".join(oscmd.install_flannel()),
            'commissaire_install_docker': " ".join(oscmd.install_docker()),
            'commissaire_install_kube': " ".join(oscmd.install_kube()),
            'commissaire_flannel_service': oscmd.flannel_service,
            'commissaire_docker_service': oscmd.flannel_service,
            'commissaire_kubelet_service': oscmd.kubelet_service,
            'commissaire_kubeproxy_service': oscmd.kubelet_proxy_service,
        }

        # Client Certificate additions
        if config.etcd.get('certificate_path', None):
            self.logger.info('Using etcd client certs')
            play_vars['commissaire_etcd_client_cert_path'] = (
                oscmd.etcd_client_cert)
            play_vars['commissaire_etcd_client_cert_path_local'] = (
                config.etcd['certificate_path'])
            play_vars['commissaire_etcd_client_key_path'] = (
                oscmd.etcd_client_key)
            play_vars['commissaire_etcd_client_key_path_local'] = (
                config.etcd['certificate_key_path'])
            play_vars['commissaire_etcd_use_cert'] = True

        if config.kubernetes.get('certificate_path', None):
            self.logger.info('Using kubernetes client certs')
            play_vars['commissaire_kubernetes_client_cert_path'] = (
                oscmd.kube_client_cert)
            play_vars['commissaire_kubernetes_client_cert_path_local'] = (
                config.kubernetes['certificate_path'])
            play_vars['commissaire_kubernetes_client_key_path'] = (
                oscmd.kube_client_key)
            play_vars['commissaire_kubernetes_client_key_path_local'] = (
                config.kubernetes['certificate_key_path'])
            play_vars['commissaire_kubernetes_use_cert'] = True

        # XXX: Need to enable some package repositories for OS 'rhel'
        #      (or 'redhat').  This is a hack for a single corner case.
        #      We discussed how to generalize future cases where we need
        #      extra commands for a specific OS but decided to defer until
        #      more crop up.
        #
        #      See https://github.com/projectatomic/commissaire/pull/56
        #
        if oscmd.os_type in ('rhel', 'redhat'):
            play_vars['commissaire_enable_pkg_repos'] = (
                'subscription-manager repos '
                '--enable=rhel-7-server-extras-rpms '
                '--enable=rhel-7-server-optional-rpms')
        else:
            play_vars['commissaire_enable_pkg_repos'] = 'true'

        self.logger.debug('Variables for bootstrap: {0}'.format(play_vars))

        play_file = resource_filename(
            'commissaire', 'data/ansible/playbooks/bootstrap.yaml')
        results = self._run(ip, key_file, play_file, [0], play_vars)

        return results
