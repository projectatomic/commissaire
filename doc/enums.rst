Enums
=====

.. _host-os:

OS's
----

* **atomic**: http://www.projectatomic.io/
* **rhel**:  http://www.redhat.com/en/technologies/linux-platforms/enterprise-linux
* **centos**: https://www.centos.org/
* **fedora**: https://getfedora.org/


.. _network-types:

* **flannel_etcd**: Uses the configured etcd store handler for it's network configuration
* **flanneld_service**:  Uses flannel in client/server mode. Requires options to have ``address`` of ``host:port``.


Statuses
--------

.. _host-statuses:

Host Statuses
~~~~~~~~~~~~~

* **investigating**: The host has passed credentials to commissaire which is now looking at the system.
* **bootstrapping**: The host is going through changes to become active.
* **active**: The host is part of the cluster and is registered with the Container Manager.
* **inactive**: The host exists but is currently not actively working as a node for the Container Manager.
* **disassociated**: The host exists but is not associated with the Container Manager.
* **failed**: Unable to access the system.


.. _upgrade-statuses:

Upgrade Statuses
~~~~~~~~~~~~~~~~

* **in_process**: The cluster is currently upgrading hosts.
* **finished**: The cluster successfully upgraded.
* **failed**: The cluster could not upgrade.

.. _status-statuses:

Status Statuses
~~~~~~~~~~~~~~~

* **OK**: The status check is currently working.
* **FAILED**: The status check is currently failing.

.. _cluster_types:

Cluster Types
~~~~~~~~~~~~~

* **kubernetes**: A cluster with a Kubernetes compatible API.
* **host_only**: A cluster for only managing hosts.
