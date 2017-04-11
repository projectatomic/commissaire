Walkthrough
===========

This document walkthroughs a simple scenario with Commissaire.

Before We Start
----------------

Some commands sections talk about an ssh key. The clarify, the ssh key always meets these requirements:

* The key is a private ssh key
* A copy of the private key would be on the operators system
* The key would belong to a user on the remote host (IE: it would be listed in the authorized_keys file on the remote host)
* The user on the remote system would be privileged (easiest example: root)
* The key is used within Commissaire to access hosts

Configuring a ContainerManager (Optional)
-----------------------------------------
If you will be using OpenShift, OCP, or Kubernetes then configuring a ContainerManager is the first thing to do.
This essentially will tell commissaire how to communicate with your ContainerManager. When a cluster is associated
to this ContainerManager new hosts will be automatically added into the the ContainerManager as nodes.

Let's say you wanted to add a ContainerManager called ``ocp``,  which has a url of ``https://openshift.example.com``,
and uses a token of ``aaa`` for authentication:

.. include:: examples/commctl_create_container_manager.rst

.. note::

   :ref:`walkthrough_adding_hosts_to_the_cluster`, later in this document, will show
   how the ContainerManager interacts binds with Clusters and Hosts.

Creating a Cluster
------------------
Clusters are groupings of hosts. These hosts are expected to be similar to each other in functionality. In other words,
the configurations of hosts in a cluster should not differ. While the functionality provided by the hosts may differ
the system itself should not. Take OpenShift nodes as an example. Some nodes may be hosting pods running different
workloads, such as database services, web applications, or a mixture. However, the underlying hosts themselves are
configured to be OpenShift nodes and are configured identical to each other.

To create a brand new cluster:

.. note::

    If you did not create a ContainerManager you can omit ``--container-manager``.

.. include:: examples/commctl_create_cluster.rst

.. _walkthrough_adding_hosts_to_the_cluster:

Adding Hosts To The Cluster
---------------------------

Adding new hosts to Commissaire comes in two forms. Automatic registration and manual additions.

Automatic Registration
~~~~~~~~~~~~~~~~~~~~~~

First, you must create the ``user-data`` file. ``commctl`` provides a command, named ``user-data``, which helps
generate this file for you. Here is an example:

.. include:: examples/commctl-user-data.rst


Now provide the new ``user-data`` file when provisioning new hosts in your cloud provider. When the new host starts
it will automatically register into Commissaire.

Manual Registration
~~~~~~~~~~~~~~~~~~~
You can also add hosts into Commissaire in a manual fashion. To do this you will need:

1. The host to have ``sshd`` running
2. The host to have ``sshd`` port open.
3. The private key to an administrative user on the host (EG: ``root``)


.. note::

   Jump to :ref:`walkthrough_creating_keys` if you want to create a new key

Let's say you have a host called ``192.168.152.110`` which you'd like to add to the cluster ``my_cluster``. You also
have a private key of the remote root user for ``192.168.152.110`` at ``/path/to/remote/hosts/priv/ssh_key``. The
following command would add the host to the cluster:

.. note::

    Remember, the ssh key references the operators copy of the key used when accessing the new host

.. include:: examples/commctl_host_create.rst

Operations
----------

Now that you have at least one host registered in a cluster you can now do operations. Let's do a restart. The
following command will start the restart process.

.. include:: examples/commctl_create_restart.rst

Now let's see what the status of the process is:

.. linclude:: examples/commctl_get_restart.rst

For more operations via ``commctl`` see :ref:`commctl_cli`



Optional Steps
--------------

The following are optional items which may prove useful for some users.

.. _walkthrough_creating_keys:

Creating Keys
~~~~~~~~~~~~~
If you want to create a new key pair for the remote host you can do the following:

.. literalinclude:: examples/create_ssh_key.rst

You could then use your cloud provider to inject the key into the host.

* `AWS documentation <http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html#how-to-generate-your-own-key-and-import-it-to-aws>`_
* `GCE <https://cloud.google.com/compute/docs/instances/adding-removing-ssh-keys#project-wide>`_
