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
The following is a quick way to allow you to generate a hash.

.. code-block:: shell

   python -c "import bcrypt, getpass; print(bcrypt.hashpw(getpass.getpass(), bcrypt.gensalt()))"

.. todo::

   Replace this with a simple script.


Example
~~~~~~~

.. literalinclude:: ../conf/users.json
   :language: json


Using Etcd
----------

To put the configuration in Etcd set the ``/commissaire/config/httpbasicauthbyuserlist`` key with
valid JSON.

.. include:: examples/etcd_authentication_example.rst


Development Information
-----------------------

commissaire's authentication is handled by a simple
plugin based system. To create a new authentication plugin
subclass ``commissaire.authentication.Authenticator``
and implement the ``authenticate`` method. The ``authenticate``
should always return on success or raise ``falcon.HTTPForbidden``
on failure.

.. note::
   In the future this will be configurable through a configuration file.
   For now it requires code modification to switch out a plugin.


Example
-------

.. code-block:: python

   import falcon

   from commissaire.authentication import Authenticator

   
   class LocalhostOnlyAuthenticator(Authenticator):

       def authenticate(self, req, resp):
           if r.env['REMOTE_ADDR'] == '127.0.0.1':
               return
           raise falcon.HTTPForbidden()
