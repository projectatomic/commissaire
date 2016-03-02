Getting Started
===============

.. _manual_installation:

Manual Installation
-------------------
To test out the current code you will need the following installed:

* Python2.6+
* virtualenv
* etcd2 (running)
* Kubernetes Cluster with a bearer token for access (running)
* (Optional) docker (running)

Set up virtualenv
~~~~~~~~~~~~~~~~~

.. include:: examples/setup_virtualenv.rst

(Optional): Run Unittests
~~~~~~~~~~~~~~~~~~~~~~~~~
If you are running from the matest master it's a good idea to verify that all
the unittests run. From the repo root...

.. include:: examples/run_unittest_example.rst


(Optional): Put Configs in Etcd
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
commissaire will default back to the local files but using Etcd is where configuration should be stored.

.. include:: examples/etcd_authentication_example.rst

.. include:: examples/etcd_logging_example.rst


Set The Kubernetes Bearer Token
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
You'll also need to set the kubernetes bearer token in etcd.

.. note:: There is no default for the bearer token!

.. include:: examples/etcd_set_kube_bearer_token.rst


(Optional): Build Docker Container
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
If you want to run from Docker and would like to build the image for yourself run...

.. code-block:: shell

    docker build --tag commissaire .
    ...

Running the service
~~~~~~~~~~~~~~~~~~~

From Source
```````````
From the repo root...

.. include:: examples/run_from_source.rst

Via Docker
``````````
To run the image specify the ETCD and KUBE variables pointing towards the specific services.

.. include:: examples/run_via_docker.rst

Adding a Cluster
~~~~~~~~~~~~~~~~
Verify that Commissaire is running as a container or in the virtual environment then execute...

.. include:: examples/create_cluster.rst

Adding a Host
~~~~~~~~~~~~~
Verify that Commissaire is running as a container or in the virtual environment then execute...

.. include:: examples/create_host.rst