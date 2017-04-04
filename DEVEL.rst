Installation instructions
=========================

The following instructions will setup a development environment
for commissaire.

If something does not work as expected, please create an issue or
propose a PR.


Prepare environment
-------------------

The environment can be installed on a base Fedora 24 installation.

First install the required packages:

.. code-block:: shell

   $ sudo dnf update -y
   $ sudo dnf install -y etcd redis
   $ sudo dnf install -y @development-tools redhat-rpm-config
   $ sudo dnf install -y python3 python3-virtualenv


Next enable the ``etcd`` and ``redis`` services:

.. code-block:: shell

   $ sudo systemctl enable etcd redis
   $ sudo systemctl start etcd redis



Pull repositories
-----------------

Commissaire consists of several projects that either provide
common code or the actual services. You can clone the repos
by following the example below:

.. code-block:: shell

   $ mkdir commissaire-projects
   $ cd commissaire-projects
   $ git clone https://github.com/projectatomic/commissaire
   $ git clone https://github.com/projectatomic/commissaire-service
   $ git clone https://github.com/projectatomic/commissaire-http
   $ git clone https://github.com/projectatomic/commctl


After this we will install each project to setup a development
environment.


Create VirtualEnv
-----------------

In the ``commissaire-projects`` directory you previously created
(*Pull Repositories*, above) create the ``devel`` virtualenv:

.. code-block::

   $ virtualenv-3.5 devel
   $ . ./devel/bin/activate


Continue executing the following commands in the virtualenv you just created.


**NOTE**: For ``zsh`` users, you may need to run the ``rehash`` shell
builtin after you ``pip install`` each project so that the commands
are available in your ``$PATH``.


Install Commissaire
===================

.. code-block::

   $ cd commissaire
   $ pip install -e .
   $ cd ..


Install Commissaire Service
---------------------------

.. code-block::

   $ cd commissaire-service
   $ pip install -e .
   $ ../commissaire/tools/etcd_init.sh


Edit your storage configuration to point to your etcd instance:

.. code-block::

   $ cp conf/storage.conf mystorage.conf


**Note**: Point ``server_url`` to ``http://127.0.0.1:2379`` (not https)


Start the service

.. code-block::

   $ commissaire-storage-service -c mystorage.conf &
   $ cd ..


Install Commissaire Server
--------------------------

.. code-block::

   $ cd commissaire-http
   $ pip install -e .  # Install commissaire-http into the virtualenv


Edit the configuration to point to your redis instance

.. code-block::

   $ cp conf/commissaire.conf config.conf

**Note:** If locally installed you do not need to change anything

Start the service:

.. code-block::

   $ commissaire-server -c config.conf &
   $ cd ..


Run testcases for Commissaire Server
++++++++++++++++++++++++++++++++++++


**Note**: that you can use ``tox`` to run testcases for this project.

Install using:

.. code-block::

   $ pip install tox


and then, from the ``commissaire-http`` folder, run the following
command:

.. code-block:: shell

   $ tox -v -e py35


Verification
------------


After this the API will be available at ``http://127.0.0.1:8000/``. To
verify it works, we will use the initial user ``a`` with pass ``a``.

.. code-block::

   $ curl -u "a:a" -X GET http://127.0.0.1:8000/api/v0/clusters/


Using ``commctl``
-----------------

.. code-block::

   $ cd commctl
   $ pip install -e .
   $ cd ..


Edit the configuration:

.. code-block::

   $ vi ~/.commissaire.json

.. code-block:: json

    {
        "username": "a",
        "password": "a",
        "endpoint": "http://127.0.0.1:8000"
    }

To query the known clusters:

.. code-block::

   $ commctl cluster list

In our case this should now return ``No object found``
