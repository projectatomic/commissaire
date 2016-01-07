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

**Endpoint**: /api/v0/hosts


GET
```
Retrieve a list of hosts.

.. code-block:: javascript

   [
       {
           "address": string,
           "status":  enum(string),
           "os": string,
           "cpus": int,
           "memory": int,
           "space": int,
           "last_check": string
       }...
   ]

.. note::
   See :ref:`host-statuses` for a list and description of host statuses.


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

