
commctl
=======

Preface
-------

.. _commctl_preface:


``commctl`` is the official command line utility for Commissaire.

.. include:: examples/commctl_note.rst

Installation
------------

Via Source
~~~~~~~~~~

.. include:: examples/commctl_install_source.rst

Via Docker
~~~~~~~~~~

.. todo::

    TODO

Via RPM
~~~~~~~

If you want to roll your own RPM, the spec file can be found in ``contrib/package/rpm/commissaire.spec``.
On RHEL/CentOS/Fedora based systems you will also need to make sure to have an RPM build environment set up.
This includes packages such as:

* rpm-build
* redhat-rpm-config

For further dependencies please see ``BuildRequires`` in the spec file.


Configuration
-------------
``commctl`` requires a configuration file. The default path is
``~/.commissaire.json`` though it can be changed with the ``--config``/``-c``
option.


.. include:: examples/commctl_config.rst

.. note::

    At least one endpoint must be defined!

The password may be stored in the configuration file as well.

.. warning::

   The configuration file is plain text. If you choose to keep a password in the file make sure to keep the file permissions locked down.

.. include:: examples/commctl_config_with_password.rst


If you are using the :ref:`Kubernetes authentication plugin <kubeauth>` you can opt to reuse the credentials from your kubeconfig like so:

.. note::

    If you include username/password and kubeconfig items the username/password will be ignored in favor of the kubeconfig.

.. include:: examples/commctl_config_with_kubeconfig.rst

Multiple fallback endpoints may be specified as a list. The endpoints are
tried in order until a successful connection is made.

.. include:: examples/commctl_config_multihost.rst


Commands
--------

cluster
~~~~~~~

.. note::

    For API versions of these commands see the :ref:`Cluster API<cluster_op>`

create
``````

``create`` will create a new cluster. It takes in two flags:

* ``-t``/``--type``: Type of the cluster (Default: kubernetes)
* ``-n``/``--network``: Name of the network (Default: default)

``create`` requires one positional argument:

* ``name``: The name to give the cluster

.. code-block:: shell

   $ commctl cluster create --type kubernetes --network default my_cluster


delete
``````

``delete`` will delete a cluster from the server.

``delete`` requires one positional argument:

* ``name``: The name of the cluster to delete


.. code-block:: shell

   $ commctl cluster delete my_cluster


get
```

``get`` will retrieve a cluster from the server.

``get`` requires one positional argument:

* ``name``: The name of the cluster to retrieve

.. code-block:: shell

   $ commctl cluster get my_cluster


list
````

``list`` will provide a list of all configured clusters.


To list all clusters:

.. include:: examples/commctl_list_clusters.rst

deploy start
````````````

``deploy start`` will create a new deployment on an Atomic host. This is an
asynchronous action. See :ref:`deploy_status` on checking the results.

``deploy start`` requires two positional arguments:

* ``name``: The name of the cluster to deploy upon
* ``version``: The version with which to upgrade


.. code-block:: shell

   $ commctl cluster deploy start mycluster 7.4.1


.. _deploy_status:

deploy status
`````````````

``deploy status`` will retrieve the status of an deploy

``deploy status`` requires one positional argument:

* ``name``: The name of the cluster to check

.. code-block:: shell

   $ commctl cluster deploy status mycluster


restart start
`````````````

``restart start`` will create a new restart roll on a cluster of hosts. This is an
asynchronous action. See :ref:`restart_status` on checking the results.

``restart start`` requires one positional argument:

* ``name``: The name of the cluster to restart


.. include:: examples/commctl_create_restart.rst


.. _restart_status:

restart status
``````````````

``restart status`` will retrieve the status of an restart

``restart status`` requires one positional argument:

* ``name``: The name of the cluster to check

.. include:: examples/commctl_get_restart.rst


upgrade start
`````````````

``upgrade start`` will create a new upgrade on a cluster of hosts. This is an
asynchronous action. See :ref:`upgrade_status` on checking the results.

``upgrade start`` requires one positional argument:

* ``name``: The name of the cluster to upgrade

.. include:: examples/commctl_create_upgrade.rst



.. _upgrade_status:

upgrade status
``````````````

``upgrade status`` will retrieve the status of an upgrade

``upgrade status`` requires one positional argument:

* ``name``: The name of the cluster to check

.. include:: examples/commctl_get_upgrade.rst



host
~~~~
.. note::

    For API versions of these commands see the :ref:`Host API<host_op>`

create
``````

``create`` will create a new host record. It takes in one flag:

* ``-c``/``--cluster``: Adds the host to the specified cluster

``create`` requires two positional arguments:

* ``address``: The domain or address of the host to access and add
* ``ssh_priv_key``: The full path to the hosts ssh_private_key for access

.. code-block:: shell

   $ commctl host create --cluster my_cluster 192.168.152.110 /path/to/host/priv/ssh_key

.. note::

    When creating a new host record the host will need to have an ssh key already generated
    and available for commissaire. The host also will need to have ssh running and the ``python``
    command must be available. If you want to bootstrap new hosts please see our :ref:`cloud_init`
    documentation.


delete
``````

``delete`` will delete a host from the server.

``delete`` requires one positional argument:

* ``name``: The name of the host to delete

.. code-block:: shell

   $ commctl host delete 192.168.152.110


get
```

``get`` retrieves a host record from the server.

``get`` requires one positional argument:

* ``address``: The address or domain of the host to retrieve

.. code-block:: shell

   $ commctl host get 192.168.152.110


list
````
``list`` will provide a list of all configured hosts.

To list all hosts:

.. include:: examples/commctl_list_hosts.rst


status
``````

``status`` retrieves status information for a specific host.

``status`` requires one positional argument:

* ``address``: The address or domain of the host to retrieve status


.. code-block:: shell

   $ commctl host status 192.168.152.110


ssh
```

.. note::

    For the api used for this commands see the :ref:`Host Creds API<host_creds_op>`


``commctl`` provides a simple way to connect to your host node by pulling down
the ``ssh_priv_key`` and ``remote_user`` from the server. The ``ssh_priv_key`` is
stored temporarily and is removed upon the completion of the connection.

``ssh`` requires one positional argument:

* ``hostname``: The address or domain of th

``ssh`` allows for N optional positional argument:

* ``extra_args``: Extra arguments to pass to the ssh command

To connect to a host node:

.. include:: examples/commctl_host_ssh.rst

To connect to a host node with extra ssh parameters:

.. include:: examples/commctl_host_ssh_with_parameters.rst



network
~~~~~~~

.. note::

    For API versions of these commands see the :ref:`Network API<network_op>`


create
``````

``create`` will create a new network record. It takes in two flags:

* ``-t``/``--type``: The type of the network: (Default: flannel_etcd)
* ``-o``/``--options``: Additional options for the network (Default: "{}")

``create`` requires one positional argument:

* ``name``: The name to give the network

.. code-block:: shell

   $ commctl network create --type flannel_server --options '{"address": "192.168.152.100:8080"}' my_network


delete
``````

``delete`` will delete a network from the server.

``delete`` requires one positional argument:

* ``name``: The name of the network to delete


.. code-block:: shell

   $ commctl network delete my_network


get
```

``get`` will retrieve a network from the server.

``get`` requires one positional argument:

* ``name``: The name of the network to retrieve

.. code-block:: shell

   $ commctl network get my_network


list
````

``list`` will provide a list of all configured networks.

To list all hosts in a specific cluster:

.. include:: examples/commctl_list_hosts_in_cluster.rst



.. _commctl_passhash:

passhash
~~~~~~~~

The ``passhash`` command provides an easy way to create bcrypt2 hashes.


The quickest way to use the command is to provide no flags. This will prompt
you for the password and output the hash.

.. code-block:: shell

   $ commctl passhash
   Password:
   $2a$12$tMz3FVwwwkXoXcTvCHdNnul1wC.sBX1KyRYEB.FZ42VCPZVc5.SyW

If you have a password in a file you can use the ``--file``/``-f`` switch to
use it as the password.

.. code-block:: shell

   $ commctl passhash --file my_password.txt
   $2a$12$K5KtQ6woCJW5Y9gSC9W25eRu1rMWIT5WyLsLtauoZyB2bZQ8yjc1C

If you would like to change the strength of the hash via it's rounds you can use
``--rounds``/``-r``.

.. code-block:: shell

   $ commctl passhash --rounds 15
   Password:
   $2a$15$mTKz3Hl08AcJsK79YGk9G.RHe1P9ksr/whLyxZGsh92bvJt83mb8q


If you want to pass the password directly in the command you can use ``--password``

.. warning::

    Generally this is a bad idea as the password may be kept in shell history and
    will be viewable by anyone else with access to the terminal.

.. code-block:: shell

   $ commctl passhash --password bad_idea
   $2a$12$BJZYMKFEvG1osE5YXBxwIOMEHCpvHu8IlSnVpE6L0JbuhNCa.Lj.C
