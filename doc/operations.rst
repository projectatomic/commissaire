Operations
==========

Preface
-------
All operations via commissaire are done via REST. While any HTTP client can
be used this document will show examples using *commctl* as well as *curl*.

.. include:: examples/commctl_note.rst


commctl
~~~~~~~
commctl requires a configuration file. The default path is
``~/.commissaire.json`` though it can be changed with the ``--config``/``-c``
option.

.. include:: examples/commctl_config.rst

The password may be stored in the configuration file as well.

.. warning::

   The configuration file is plain text. If you choose to keep a password in the file make sure to keep the file permissions locked down.

.. include:: examples/commctl_config_with_password.rst


Multiple endpoints may be specified. If the first endpoint is unreachable
the next endpoint in the list is used.

.. include:: examples/commctl_config_multihost.rst


curl
~~~~
Every call requires a username and password to be passed via HTTP Basic Auth.
With curl this looks like:

.. code-block:: shell

   curl ... -u "USERNAME:PASSWORD" ...


The proper headers must also be passed. Since all of the REST communication
is done via JSON the content-type must be set to application/json.

.. code-block:: shell

   curl ... -H "Content-Type: application/json" ...


Lastly, the type of operation must be specified. For example, *PUT* must be
used when creating while *GET* must be used for retrieving.

.. code-block:: shell

   curl ... -XPUT ...


Bootstrapping
-------------
Bootstrapping happens when a new host is added to commissaire via the Host
endpoint.

.. include:: examples/create_host.rst

It's important to remember *ssh_priv_key* must be base64 encoded without
newlines. On many systems this can be done via that **base64** command
and using the **-w0** switch.

.. code-block:: shell

   $ cat path/to/key | base64 -w0 > encoded_key

For specifics on the endpoint see :ref:`host_op`

.. note::

   commissaire can help automate the bootstrapping of new hosts using
   cloud-init for early initialization.  See :ref:`cloud_init`.


Cluster Operations with commctl
-------------------------------

These operations are done across all hosts associated with a cluster.

List
~~~~
To list all clusters:

.. include:: examples/commctl_list_clusters.rst

To list all hosts:

.. include:: examples/commctl_list_hosts.rst

To list all hosts in a specific cluster:

.. include:: examples/commctl_list_hosts_in_cluster.rst


Restart
~~~~~~~
To restart a cluster:

.. include:: examples/commctl_create_restart.rst

To check up on a restart:

.. include:: examples/commctl_get_restart.rst


Upgrade
~~~~~~~
To upgrade a cluster:

.. include:: examples/commctl_create_upgrade.rst

To check up on an upgrade:

.. include:: examples/commctl_get_upgrade.rst


Cluster Operations with curl
----------------------------

These operations are done across all hosts associated with a cluster.

Restart
~~~~~~~
Restarting a cluster is done by creating a new restart record for a specific
cluster.

.. include:: examples/create_restart.rst

To check up on a restart a REST *GET* call on the same endpoint will show the
current status.

.. include:: examples/get_restart.rst

For specifics on the endpoint see :ref:`cluster_op_restart`


Upgrade
~~~~~~~
Upgrading a cluster is done by creating a new upgrade record for a specific
cluster.

.. include:: examples/create_upgrade.rst

To check up on an upgrade a REST *GET* call on the same endpoint will show the
current status.

.. include:: examples/get_upgrade.rst

For specifics on the endpoint see :ref:`cluster_op_upgrade`
