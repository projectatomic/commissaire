Authentication
==============


Modifying Users
---------------

By default commissaire will look at Etcd for user/hash combinations under
the ``/commissaire/config/httpbasicauthbyuserlist`` key.

If the key does not exist the backup is to use local file authentication
using the same JSON schema.

.. code-block:: javascript

   {
       "username(string)": {
           "hash": "bcrypthash(string)"
       }...
   }


Generating a hash
~~~~~~~~~~~~~~~~~
commissaire comes with a utility to create bcrypt hashes.

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
