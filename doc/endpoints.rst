REST Endpoints
==============

Host
----

**Endpoint**: /api/v0/host/{IP}

GET
```

PUT
```

DELETE
``````

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

