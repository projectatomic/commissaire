REST Endpoints
==============

Cluster
-------
**Endpoint**: /api/v0/cluster/{NAME}

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

No body.


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


.. _cluster_op_upgrade:

Cluster Operations: Upgrade
---------------------------
**Endpoint**: /api/v0/cluster/{NAME}/upgrade

GET
```
Retrieve the current status of upgrades.

.. code-block:: javascript

   {
       "status": string,
       "upgrade_to": string,
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
       "upgrade_to": "7.2.1",
       "upgraded": [{...}],
       "in_process": [{...}],
       "started_at": "2015-12-17T15:48:18.710454",
       "finished_at": null
   }

PUT
```
Start a new upgrade.

.. code-block:: javascript

   {
       "upgrade_to": string
   }

Example
~~~~~~~

.. code-block:: javascript

   {
       "upgrade_to": "7.2.1"
   }

Example Response
~~~~~~~~~~~~~~~~

.. code-block:: javascript

   {
       "status": "in_process",
       "upgrade_to": "7.2.1",
       "upgraded": [{...}],
       "in_process": [{...}],
       "started_at": "2015-12-17T15:48:18.710454",
       "finished_at": null
   }


.. _cluster_op_restart:

Cluster Operations: Restart
---------------------------
**Endpoint**: /api/v0/cluster/{NAME}/restart

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
       "ssh_priv_key": string // base64 encoded ssh private key
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
       "ssh_priv_key": "dGVzdAo..."
   }

DELETE
``````
Deletes a host record.


Hosts
-----

**Endpoint**: /api/v0/clusters


GET
```
Retrieve a list of clusters.

.. code-block:: javascript

   [
       string...
   ]


Example
~~~~~~~

.. code-block:: javascript

   [
       "development",
       "production"
   ]


**Endpoint**: /api/v0/hosts


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


Status
------

**Endpoint**: /api/v0/status

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
       "clusterexecpool": {
           "status": enum(string),      // Status of the clusterexec pool
           "info": {
               "size": int,             // Total size of the clusterexec pool
               "in_use": int,           // Amount of the pool in use
               "errors": [string,...],  // Errors from the pool
           }
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
       "clusterexec": {
           "status": "OK",
           "info": {
               "size": 5,
               "in_use": 0,
               "errors": []
           }
       }

   }

