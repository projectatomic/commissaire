.. _commissaire_services:

Commissaire Services
====================

Commissaire Service is a framework for writing long running services for the
Commissaire management system. It provides a standard way to connect to
Commissaire's message bus and provide/consume services.

Each service by default looks for a ``.conf`` file named after itself
in ``/etc/commissaire`` for its configuration.  For example, the Storage
service looks for ``/etc/commissaire/storage.conf``.  The default location
can be overridden with the ``-c/--config`` command-line option for any of
the services.

For easier deployment on cloud services, each Commissaire service will also
look to etcd_ for configuration if certain environment variables are defined,
particularly ``ETCD_MACHINES``.

Recognized environment variables for retrieving configuration from ``etcd``
are:

- ``ETCD_MACHINES`` : Comma-separated list of ``etcd`` service URLs
- ``ETCD_TLSPEM`` : Optional path to local TLS client certificate public key file
- ``ETCD_TLSKEY`` : Optional path to local TLS client certificate private key file
- ``ETCD_CACERT`` : Optional path to local TLS certificate authority public key file
- ``ETCD_USERNAME`` : Optional username used for basic auth
- ``ETCD_PASSWORD`` : Optional password used for basic auth


Example Use Cases
-----------------

Commissaire Clusterexec
```````````````````````
Commissaire's ``Cluster Execution`` service is a set of long running processes
which handle rolling operations over hosts in a cluster.

- Local configuration in file ``/etc/commissaire/clusterexec.conf``
- Remote configuration in ``etcd`` key ``/commissaire/config/clusterexec``

Commissaire Container Manager
``````````````````````````````
Commissaire's ``Container Manager`` service is a set of long running processes
which provide a consistant API to work with container managers.

- Local configuration in file ``/etc/commissaire/containermgr.conf``
- Remote configuration in ``etcd`` key ``/commissaire/config/containermgr``

Commissaire Investigator
````````````````````````
Commissaire's ``Investigator`` is a set of long running processes which
connect to and bootstrap new hosts wanting to be managed by Commissaire.

- Local configuration in file ``/etc/commissaire/investigator.conf``
- Remote configuration in ``etcd`` key ``/commissaire/config/investigator``

Commissaire Watcher
```````````````````
Commissaire's ``Watcher`` is a set of long running processes which periodically
connects to hosts that have already been bootstrapped and checks their status.

- Local configuration in file ``/etc/commissaire/watcher.conf``
- Remote configuration in ``etcd`` key ``/commissaire/config/watcher``

Commissaire Storage
```````````````````
Commissaire's ``Storage`` is a set of long running processes which broker
storage and retrieval requests of persistent data.

Additionally, this service publishes notifications on the bus when creating,
updating or deleting stored records. Other services can listen for and react
to these notifications to automatically update internal state or kick off a
long-running operation.

- Local configuration in file ``/etc/commissaire/storage.conf``
- Remote configuration in ``etcd`` key ``/commissaire/config/storage``


Writing a Service
-----------------
See :ref:`Developing Services <services_devel>`

.. _etcd: https://github.com/coreos/etcd
