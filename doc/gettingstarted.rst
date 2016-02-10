Getting Started
===============

Development/Manual Installation
--------------------------------
To test out the current development code you will need the following installed:

* Python2.6
* virtualenv
* etcd2 (running)
* Kubernetes Cluster with a bearer token for access (running)
* (Optional) docker (running)

Set up virtualenv
~~~~~~~~~~~~~~~~~

.. code-block:: shell

   $ virtualenv /where/you/want/it/to/live
   ...
   (virtualenv)$ . /where/you/want/it/to/live/bin/activate
   (virtualenv)$ pip install -r requirements.txt
   ...

(Optional): Run Unittests
~~~~~~~~~~~~~~~~~~~~~~~~~
From the repo root...

.. code-block:: shell

   (virtualenv)$ pip install -r test-requirements.txt
   ...
   (virtualenv)$ python setup.py nosetests

Adding a Host Manually
~~~~~~~~~~~~~~~~~~~~~~

.. todo::

   Remove this once container registration work is merged.

Verify that etcd is running then execute...

.. code-block:: shell

   (virtualenv)$ etcdctl set /commissaire/hosts/10.0.0.1 '{"address": "10.0.0.1","status": "available","os": "atomic","cpus": 2,"memory": 11989228,"space": 487652,"last_check": "2015-12-17T15:48:18.710454","ssh_priv_key": "dGVzdAo=", "cluster": "default"}'

(Optional): Put Configs in Etcd
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
commissaire will default back to the local files but using Etcd is where configuration should be stored.

.. code-block:: shell

   (virtualenv)$ cat conf/users.json | etcdctl set '/commissaire/config/httpbasicauthbyuserlist'
   ...
   (virtualenv)$ cat conf/logger.json | etcdctl set '/commissaire/config/logger'
   ...

Set The Kubernetes Bearer Token
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
You'll also need to set the kubernetes bearer token.

.. note:: There is no default bearer token!

.. code-block:: shell

   (virtualenv)$ etcdctl set '/commissaire/config/kubetoken' $KUBERNETES_ACCESS_TOKEN


(Optional): Build Docker Container
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
From the repo root build the image...

.. code-block:: shell
    docker build --tag commissaire .
    ...

Running the service
~~~~~~~~~~~~~~~~~~~

From Source
```````````
From the repo root...

.. code-block:: shell

   (virtualenv)$ PYTHONPATH=`pwd`/src python src/commissaire/script.py -e http://127.0.0.1:2379 -k http://127.0.0.1:8080 &
   ...

Via Docker
``````````
To run the image specify the ETCD and KUBE variables pointing towards the specific services.

.. code-block:: shell

    docker run -d -e ETCD=http://127.0.0.1:2379 -e KUBE=http://127.0.0.1:8080 commissaire
    ...
