Authentication
==============

Defining Authentication Plugin
------------------------------

The default authentication plugin uses a JSON schema in etcd to lookup users.
To change to another plugin use the ``--authentication-plugin`` switch. If the
plugin has required configuration options you may also need to use the
``--authentication-plugin-kwargs``.

.. code-block:: shell

   $ commissaire [...] \
   --authentication-plugin commissaire.authentication.httpauthbyfile
   --authentication-plugin-kwargs "filepath=/path/to/users.json"


Modifying Users
---------------

By default commissaire will look at Etcd for user/hash combinations under
the ``/commissaire/config/httpbasicauthbyuserlist`` key.

commissaire can also use a local file for authentication using the same JSON
schema.

.. code-block:: javascript

   {
       "username(string)": {
           "hash": "bcrypthash(string)"
       }...
   }


Generating a hash
~~~~~~~~~~~~~~~~~
commissaire has a utility to create bcrypt hashes.

.. include:: examples/commctl_note.rst

.. code-block:: shell

	$ commissaire-hashpass
	Password:
	$2b$12$rq/RN.Y1WD0ZyKPpLJkFVOv3XdLxW5thJ3OEaRgaMMFCgzLzHjiJG
	$


Example
~~~~~~~

.. literalinclude:: ../conf/users.json
   :language: json


Using Etcd
----------

To put the configuration in Etcd set the ``/commissaire/config/httpbasicauthbyuserlist`` key with
valid JSON.

.. include:: examples/etcd_authentication_example.rst
