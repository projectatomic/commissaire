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


Example Use Cases
-----------------

Commissaire Clusterexec
```````````````````````
Commissaire's ``Cluster Execution`` service is a set of long running processes
which handle rolling operations over hosts in a cluster.

Configuration in ``/etc/commissaire/clusterexec.conf``

Commissaire Container Manager
``````````````````````````````
Commissaire's ``Container Manager`` service is a set of long running processes
which provide a consistant API to work with container managers.

Configuration in ``/etc/commissaire/containermgr.conf``

Commissaire Investigator
````````````````````````
Commissaire's ``Investigator`` is a set of long running processes which
connect to and bootstrap new hosts wanting to be managed by Commissaire.

Configuration in ``/etc/commissaire/investigator.conf``

Commissaire Watcher
```````````````````
Commissaire's ``Watcher`` is a set of long running processes which periodically
connects to hosts that have already been bootstrapped and checks their status.

Configuration in ``/etc/commissaire/watcher.conf``

Commissaire Storage
```````````````````
Commissaire's ``Storage`` is a set of long running processes which broker
storage and retrieval requests of persistent data.

Configuration in ``/etc/commissaire/storage.conf``




Writing a Service
-----------------
See :ref:`Developing Services <services_devel>`

