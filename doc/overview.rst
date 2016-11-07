Overview
========

.. pull-quote::

   It actually configured Kubernetes when I could not remember how to.

   -- Ryan Cook

commissaire is a lightweight REST interface for upgrading, restarting, and bootstrapping new hosts into an existing Container Management cluster such as OpenShift_ or Kubernetes_.

.. _Kubernetes: http://kubernetes.io

.. _OpenShift: https://www.openshift.com

Feature Overview
----------------

- Restart hosts in an OpenShift or Kubernetes cluster
- Upgrade hosts in a OpenShift or Kubernetes cluster
- :ref:`Bootstrap new hosts into an existing OpenShift or Kubernetes cluster <bootstrapping>`
- No agent required for hosts: All communication is done over SSH
- :ref:`Simple REST interface for automation <rest_endpoints>`
- Service status for health checking
- :ref:`Plug-in based authentication framework <authdevel>`
- :ref:`Command line interface for operators <commctl_cli>`
- Built in support for Atomic Host and Server variants of RHEL, Fedora, and CentOS


Logical Flow
------------

.. image:: commissaire-flow-diagram.png


What commissaire Is Not
-----------------------
There are a lot of overloaded words in technology. It's important to note what
commissaire is not as much as what it is. commissaire is not:

- A Container Manager or scheduler (such as OpenShift or Kubernetes)
- A configuration management system (such as Ansible_ or Puppet_)
- A replacement for individual host management systems

.. _Ansible: https://www.ansible.com

.. _Puppet: https://puppet.com

Example Uses
------------

.. todo::

    Add more use cases!

.. note::

   This is an early list. More use cases will be added in the future.

- An administrator needs to upgrade an entire group of hosts acting as Kubernetes nodes
- An administrator needs to restart an entire group of hosts acting as Kubernetes nodes
- An organization would like new hosts to register themselves into a Kubernetes cluster upon first boot without administrator intervention
- An organization would like to keep groups of hosts used as Kubernetes nodes out of direct control of anything but Kubernetes and basic operations.
