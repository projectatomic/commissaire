.. _rest_endpoints:

REST Endpoints
==============

.. _cluster_op:

Cluster
-------


**Endpoint**: /api/v0/cluster/{NAME}

(Internal model name: ``Cluster``)

GET
```
Retrieve the status of the cluster.

.. code-block:: javascript

   {
       "status" string,
       "hosts": {
           "total": int,
           "available": int,
           "unavailable": int
       }
   }

Example
~~~~~~~

.. code-block:: javascript

   {
       "status": "ok",
       "hosts": {
           "total": 3,
           "available": 3,
           "unavailable": 0
       }
   }

PUT
```
Creates a new cluster.

.. note::

    To retain backwards compatibilty this endpoint will also continue accepting
    no payload until version ``0.1.0``. Until then the type of ``kubernetes``
    will be used.

.. code-block:: javascript

    {
        "type": enum(string), // The cluster type
        "network": string     // The name of the network
    }

.. note::

   See :ref:`cluster_types` for a list and description of cluster types.


Example
~~~~~~~

.. code-block:: javascript

   {
       "type": "kubernetes",
       "network": "default"
   }


Cluster Members
---------------
**Endpoint**: /api/v0/cluster/{NAME}/hosts

GET
```
Retrieve the host list for a cluster.

.. code-block:: javascript

   [
       host_address,...
   ]

Example
~~~~~~~

.. code-block:: javascript

   [
       "192.168.100.50",
       "192.168.100.51"
   ]

PUT
```
Replace the host list for a cluster.  The "old" list must match the
current host list.

.. code-block:: javascript

   {
       "old": [host_address,...]
       "new": [host_address,...]
   }

Example
~~~~~~~

.. code-block:: javascript

   {
       "old": ["192.168.100.50"],
       "new": ["192.168.100.50", "192.168.100.51"]
   }


Cluster Members (Individual)
----------------------------
**Endpoint**: /api/v0/cluster/{NAME}/hosts/{IP}

GET
```
Membership test.  Returns 200 if host {IP} is in cluster, else 404.

PUT
```
Adds host {IP} to cluster. (Idempotent)

No body.

DELETE
``````
Removes host {IP} from cluster. (Idempotent)

No body.


.. _cluster_op_deploy:

Cluster Operations: Deploy
--------------------------
**Endpoint**: /api/v0/cluster/{NAME}/deploy

(Internal model name: ``ClusterDeploy``)

GET
```
Retrieve the current status of an OSTree tree deployment.

.. code-block:: javascript

   {
       "status": string,
       "version": string,
       "deployed": HOST_LIST,
       "in_process": HOST_LIST,
       "started_at": string,
       "finished_at": string
   }

Example
~~~~~~~

.. code-block:: javascript

   {
       "status": "in_process",
       "version": "7.2.6",
       "deployed": [{...}],
       "in_process": [{...}],
       "started_at": "2015-12-17T15:48:18.710454",
       "finished_at": null
   }

PUT
```
Start a new OSTree tree deployment.

.. code-block:: javascript

   {
       "version": string  // Which OSTree tree to deploy
   }

Example
~~~~~~~

.. code-block:: javascript

   {
       "version": "7.2.6"
   }

Example Response
~~~~~~~~~~~~~~~~

.. code-block:: javascript

   {
       "status": "in_process",
       "version": "7.2.6",
       "deployed": [{...}],
       "in_process": [{...}],
       "started_at": "2015-12-17T15:48:18.710454",
       "finished_at": null
   }


.. _cluster_op_upgrade:

Cluster Operations: Upgrade
---------------------------
**Endpoint**: /api/v0/cluster/{NAME}/upgrade

(Internal model name: ``ClusterUpgrade``)

GET
```
Retrieve the current status of upgrades.

.. code-block:: javascript

   {
       "status": string,
       "upgraded": HOST_LIST,
       "in_process": HOST_LIST,
       "started_at": string,
       "finished_at": string
   }

Example
~~~~~~~

.. code-block:: javascript

   {
       "status": "in_process",
       "upgraded": [{...}],
       "in_process": [{...}],
       "started_at": "2015-12-17T15:48:18.710454",
       "finished_at": null
   }

PUT
```
Start a new upgrade.

No body.

Example Response
~~~~~~~~~~~~~~~~

.. code-block:: javascript

   {
       "status": "in_process",
       "upgraded": [{...}],
       "in_process": [{...}],
       "started_at": "2015-12-17T15:48:18.710454",
       "finished_at": null
   }


.. _cluster_op_restart:

Cluster Operations: Restart
---------------------------
**Endpoint**: /api/v0/cluster/{NAME}/restart

(Internal model name: ``ClusterRestart``)

GET
```
Retrieve the status of a restart.

.. code-block:: javascript

   {
       "status": string,
       "restarted": HOST_LIST,
       "in_process": HOST_LIST,
       "started_at": string,
       "finished_at": string
   }

Example
~~~~~~~

.. code-block:: javascript

   {
       "status": "in_process",
       "restarted": [{...}],
       "in_process": [{...}],
       "started_at": "2015-12-17T15:48:18.710454",
       "finished_at": null
   }

PUT
```
Create a new restart.

No body.

Example Response
~~~~~~~~~~~~~~~~
.. code-block:: javascript

   {
       "status": "in_process",
       "restarted": [{...}],
       "in_process": [{...}],
       "started_at": "2015-12-17T15:48:18.710454",
       "finished_at": null
   }



Clusters
--------
**Endpoint**: /api/v0/cluster/

(Internal model name: ``Clusters``)

GET
```
Retrieve a list of all clusters.

.. code-block:: javascript

   [
       string,...
   ]


Example
~~~~~~~

.. code-block:: javascript

   [
      "mycluster",
   ]


.. _host_op:

Host
----

**Endpoint**: /api/v0/host/{IP}

(Internal model name: ``Host``)

GET
```
Retrieve a specific host record.

.. code-block:: javascript

   {
       "address": string,       // The IP address of the cluster host
       "status":  enum(string), // The status of the cluster host
       "os": enum(string),      // The OS name
       "cpus": int,             // The number of CPUs on the cluster host
       "memory": int,           // The memory of the cluster host in kilobytes
       "space": int,            // The diskspace on the cluster host
       "last_check": string     // ISO date format the cluster host was last checked
   }

.. note::
   See :ref:`host-statuses` for a list and description of host statuses.

.. note::
   See :ref:`host-os` for a list and description of host statuses.

Example
~~~~~~~

.. code-block:: javascript

   {
       "address": "192.168.100.50",
       "status": "active",
       "os": "atomic",
       "cpus": 4,
       "memory": 11989228,
       "space": 487652,
       "last_check": "2015-12-17T15:48:18.710454"
   }

PUT
```
Creates a new host record.

.. code-block:: javascript

   {
       "ssh_priv_key": string, // base64 encoded ssh private key
       "remote_user": string,  // Optional name of ssh user to use (default=root)
       "cluster": string      // Optional cluster the host should be associated with
   }

.. note::
   The rest of the host record will be filled out once the data has been pulled from the cluster host.

.. note::
   As a convenience to hosts wishing to add themselves as part of a boot
   script, the endpoint /api/v0/host (without the {IP}) also accepts PUT
   requests.  Here, the host address is inferred from the request itself
   but otherwise works the same: creates a new host record accessible at
   /api/v0/host/{IP}.

Example
~~~~~~~

.. code-block:: javascript

   {
       "cluster": "default",
       "remote_user": "root",
       "ssh_priv_key": "dGVzdAo..."
   }

DELETE
``````
Deletes a host record.


.. _host_creds_op:

HostCreds
---------

**Endpoint**: /api/v0/host/{IP}/creds

GET
```
Retrieve a specific hosts credentials.

.. code-block:: javascript

   {
       "ssh_priv_key": string, // base64 encoded ssh private key
       "remote_user":  string, // name of ssh user to use for connections
   }

HostStatus
----------

**Endpoint**: /api/v0/host/{IP}/status

(Internal model name: ``HostStatus``)

GET
```
Retrieve a specific hosts status.

**Query Parameters**
 * *raw*:

   * **Examples**: ``true``, ``false``, ``True``, ``False``, ``0``, ``1``
   * **Optional**: Yes
   * **Description**: If set to true only the status structure from the container manager will be returned

.. code-block:: javascript

  {
      "type":               string, // type of status
      "host":               dict,   // status elements from the Host instance
      "container_manager":  dict,   // status elements reported from the Container Manager
  }


Example: Default
~~~~~~~~~~~~~~~~

.. code-block:: javascript

  {
      "type": "host_only",
      "host": {
          "last_check": "2016-07-29T19:54:57.204671",
          "status": "active",
      },
      "container_manager": {...}
  }


Example: Raw
~~~~~~~~~~~~

This example is partially what would be returned from a kubernetes type cluster.

  .. code-block:: javascript

    {
        "status": {
            "capacity": {
              "cpu": "1",
              "memory": "500680Ki",
              "pods": "110"
            },
            "allocatable": {
              "cpu": "1",
              "memory": "500680Ki",
              "pods": "110"
            },
            ...
        }
    }


Hosts
-----

**Endpoint**: /api/v0/hosts

(Internal model name: ``Hosts``)

GET
```
Retrieve a list of hosts.

.. code-block:: javascript

   [
       {
           "address": string,       // The IP address of the cluster host
           "status":  enum(string), // The status of the cluster host
           "os": enum(string),      // The OS name
           "cpus": int,             // The number of CPUs on the cluster host
           "memory": int,           // The memory of the cluster host in kilobytes
           "space": int,            // The diskspace on the cluster host
           "last_check": string     // ISO date format the cluster host was last checked
       }...
   ]

.. note::
   See :ref:`host-statuses` for a list and description of host statuses.

.. note::
   See :ref:`host-os` for a list and description of host statuses.



Example
~~~~~~~

.. code-block:: javascript

   [
       {
           "address": "192.168.100.50",
           "status": "active",
           "os": "atomic",
           "cpus": 4,
           "memory": 11989228,
           "space": 487652,
           "last_check": "2015-12-17T15:48:18.710454"
       },
       {
           "address": "192.168.100.51",
           "status": "active",
           "os": "atomic",
           "cpus": 3,
           "memory": 11989228,
           "space": 487652,
           "last_check": "2015-12-17T15:48:30.401090"
       }
   ]


.. _networks_op:


Networks
--------
**Endpoint**: /api/v0/networks/

(Internal model name: ``Networks``)

GET
```
Retrieve a list of all networks.

.. code-block:: javascript

   [
       string,...
   ]


Example
~~~~~~~

.. code-block:: javascript

   [
      "mynetwork",
   ]


.. _network_op:

Network
-------

**Endpoint**: /api/v0/network/{name}

(Internal model name: ``Network``)

GET
```
Retrieve a specific network record.

.. code-block:: javascript

  {
      "name": string,        // The name of the network
      "type":  enum(string), // The type of the network
      "options": dict        // Options to explain a network
  }

.. note::
  See :ref:`network-types` for a list and description of network types.

Example
~~~~~~~

.. code-block:: javascript

  {
      "name": "mynetwork",
      "type": "flannel_server",
      "options": {
          "address": "192.168.152.101:8080"
      },
  }

PUT
```
Creates a new network record.


.. code-block:: javascript

  {
      "type":  enum(string), // The type of the network
      "options": dict        // Options to explain a network
  }

.. note::
  See :ref:`network-types` for a list and description of network types.


Example
~~~~~~~

.. code-block:: javascript

  {
      "type": "flannel_server",
      "options": {
          "address": "192.168.152.101:8080"
      },
  }

DELETE
``````
Deletes a network record.



Status
------

**Endpoint**: /api/v0/status

(Internal model name: ``Status``)

GET
```
Retrieve a the status of the system.

.. code-block:: javascript

   {
       "etcd": {
           "status": enum(string),      // Status of etcd connection
       },
       "investigator": {
           "status": enum(string),      // Status of the investigator pool
           "info": {
               "size": int,             // Total size of the investigator pool
               "in_use": int,           // Amount of the pool in use
               "errors": [string,...],  // Errors from the pool
           },
       },
   }

.. note::
   See :ref:`status-statuses` for a list and description of status statuses.


Example
~~~~~~~

.. code-block:: javascript

   {
       "etcd": {
           "status": "OK"
       },
       "investigator": {
           "status": "OK",
           "info": {
               "size": 1,
               "in_use": 1,
               "errors": []
           }
       }
   }
