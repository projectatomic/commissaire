Authentication
==============

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
