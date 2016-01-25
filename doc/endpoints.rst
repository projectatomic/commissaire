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



Clusters
--------
**Endpoint**: /api/v0/cluster/{IP}

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
       "address": string      // The IP address of the cluster host
       "ssh_priv_key": string // base64 encoded ssh private key
   }

.. note::
   The rest of the host record will be filled out once the data has been pulled from the cluster host.

Example
~~~~~~~

.. code-block:: javascript

   {
       "address": "192.168.100.50",
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
           }
       }
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

