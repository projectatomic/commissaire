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

The configuration format, whether retrieved from a local file or from etcd_, is a
JSON object with some common and some service-specific members.  JSON members that
are recognized by all services include:

- ``bus_uri`` : Message bus connection URI, handed off to a Kombu Connection_.
  The service's ``--bus-uri`` command-line option overrides this.
- ``logging`` : Logging configuration.  This section is parsed into a Python
  dictionary and handed off to Python's logging.config.dictConfig_ function.
  Commissaire installs a default formatter and handler in the "root" logger which
  logs to stderr, so this section can usually be omitted.
- ``debug`` : A boolean option to enable debug-level logging messages in the
  "root" logger.  The effect should be application-wide unless overridden in the
  ``logging`` section.  Defaults to ``False``.

Built-In Services
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

Configuration
'''''''''''''

The ``Storage`` service looks for a few additional JSON members in its
configuration:

- ``custodia_socket_path`` : File path to the Unix domain socket opened by the
  Custodia_ service.  The default path matches Custodia_'s default socket path
  (`/var/run/custodia/custodia.sock`), so this member need only be set if the
  Custodia_ service is using a different socket path.
- ``storage_handlers`` : This is a JSON object, or a list of JSON objects,
  describing which storage plugins to use, a list of model types to claim, and
  any other plugin-specific settings.  Each object recognizes these members:

  - ``type`` : The module name of the storage plugin (for convenience, no dots
    in the name implies a prefix of ``commissaire.storage``).  This value is
    **required**, although it will usually be ``etcd``, as no other plugins
    come built-in at this time.
  - ``name`` : Optional name to uniquely identify the plugin instance.  If
    omitted, a unique name is derived from the plugin's module name, such as
    ``commissaire.storage.etcd``.
  - ``models`` : A list of model type names such as ``"Host"`` or ``"Cluster"``,
    or glob-style patterns like ``"Host*"`` or ``"*"``.  Storage requests for
    these types of models will be routed to the plugin instance specified by
    the ``type`` member.  Defaults to ``["*"]``, which is usually sufficient.


Writing a Service
-----------------
See :ref:`Developing Services <services_devel>`

.. _etcd: https://github.com/coreos/etcd
.. _Connection: http://kombu.readthedocs.io/en/latest/reference/kombu.connection.html
.. _logging.config.dictConfig: https://docs.python.org/3/library/logging.config.html
.. _Custodia: https://custodia.readthedocs.io/
