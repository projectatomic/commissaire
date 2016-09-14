Operations
==========

Preface
-------
All operations via commissaire are done via REST. While any HTTP client can
be used, many users will feel more comfortable using :ref:`commctl <commctl_preface>`.



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

.. _bootstrapping:

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

Deploy
~~~~~~
Deploying to a cluster is done by creating a new upgrade record for a specific
cluster.

.. include:: examples/create_deploy.rst

To check up on a deploy a REST *GET* call on the same endpoint will show the
current status.

.. include:: examples/get_deploy.rst

For specifics on the endpoint see :ref:`cluster_op_deploy`
