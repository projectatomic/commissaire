.. _authdevel:

Authentication Plugins
======================

commissaire's authentication is handled by a simple
plugin based system. To create a new authentication plugin you must:

- subclass ``commissaire_http.authentication.Authenticator``
- name the class ``AuthenticationPlugin``
- override the ``authenticate`` method

If you need to have configuration items passed when used you will also need to
override ``__init__`` adding in keyword arguments.

.. note::

   The ``authenticate`` should always return ``True`` for success or
   ``False`` on failure.

Example
```````
See `httpbasicauth <https://github.com/projectatomic/commissaire-http/tree/master/src/commissaire_http/authentication/httpbasicauth.py>`_
