Getting Involved
================

Development Location
--------------------
The code for commissaire lives on GitHub. The main repo can be found at
https://github.com/projectatomic/commissaire.

Development Setup
-----------------

You will want to set up a virtualenv to work with. This will keep from poluting
your system with application only dependencies while you code.

.. include:: examples/setup_virtualenv.rst

.. note::

   Any time you will be working on commissaire make sure to activate the virtualenv

Getting Up To Speed
-------------------

As you can see commissaire uses a number of libraries.

.. literalinclude:: ../requirements.txt

Of these, the most important to be up to speed on are:

- gevent: http://www.gevent.org/
- falcon: http://falconframework.org/
- ansible: https://www.ansible.com/

Standards
---------

Conventions
~~~~~~~~~~~

Code
````
Like most projects commissaire expects specific coding standards to be followed.
`pep8 <https://www.python.org/dev/peps/pep-0008/>`_ is followed strictly with
the exception of E402: module level import not at top of file.

Ansible Templates
`````````````````
Variables are used with jinja2 templates and should always prefix
**commissaire_**. Here is a current list variables in use as examples:

============================================= ======================================================
Name                                          Description
============================================= ======================================================
commissaire_targets                           Host(s) to target
commissaire_install_libselinux_python         Command to install libselinux-python
commissaire_install_flannel                   Command to install flannel
commissaire_flanneld_config_local             Local flannel config file to template to the target(s)
commissaire_flanneld_config                   Remote path to the flannel config
commissaire_flannel_service                   Name of the flannel service
commissaire_install_docker                    Command to install docker
commissaire_docker_config_local               Local docker config file to template to the target(s)
commissaire_docker_config                     Remote path to the docker config
commissaire_docker_service                    Name of the docker service
commissaire_install_kube                      Command to install kubernetes minion packages
commissaire_kubernetes_config_local           Local kubernetes config file to template to the target(s)
commissaire_kubernetes_config                 Remote path to the kubernetes config
commissaire_kubeconfig_config_local           Local kubeconfig file to template to the target(s)
commissaire_kubeconfig_config                 Remote path to the kubeconfig
commissaire_kubelet_service                   Name of the kubelet service
commissaire_kubeproxy_service                 Name of the kubernetes proxy service
commissaire_restart_command                   Host restart command
commissaire_upgrade_command                   Host upgrade command
commissaire_bootstrap_ip                      The IP address of the host
commissaire_kubernetes_api_server_host        The kubernetes api server host
commissaire_kubernetes_api_server_port        The kubernetes api server port
commissaire_kubernetes_bearer_token           The bearer token used to contact kubernetes
commissaire_docker_registry_host              The docker registry host
commissaire_docker_registry_port              The docker registry port
commissaire_etcd_host                         The etcd host
commissaire_etcd_port                         The etcd port
commissaire_flannel_key                       The flannel configuration key
============================================= ======================================================

Compatibility
~~~~~~~~~~~~~
Code should attempt to be compatible with both Python 2 and Python 3. When
this is not possible it's assumed a workaround can be created in the
`commissaire.compat package <apidoc/commissaire.compat.html>`_  module.
If that is also not possible then Python 2 should be the fallback syntax.

Testing
~~~~~~~
commissaire uses TravisCI to verify that all unittests are passing.
**All unittests must pass and coverage must be above 80% before code
will be accepted. No exceptions.**.

To run unittests locally and see where your code stands:

.. include:: examples/run_unittest_example.rst
