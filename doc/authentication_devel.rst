Authentication Plugins
======================

commissaire's authentication is handled by a simple
plugin based system. To create a new authentication plugin you must:

- subclass ``commissaire.authentication.Authenticator``
- name the class ``AuthenticationPlugin``
- override the ``authenticate`` method

If you need to have configuration items passed when used you will also need to
override ``__init__`` adding in keyword arguments.

.. note::

   The ``authenticate`` should always return on success or raise
   ``falcon.HTTPForbidden`` on failure.

Once created it can be used via the ``--authentication-plugin`` and
``--authentication-plugin-kwargs`` command line switches.

Example
```````

.. literalinclude:: ../src/commissaire/authentication/httpauth.py


Example With Config
````````````````````

.. note::

   This subclasses the first example.

.. literalinclude:: ../src/commissaire/authentication/httpauthbyfile.py