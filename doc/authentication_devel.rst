.. _authdevel:

Authentication Plugins
======================

commissaire's authentication is handled by a simple WSGI based
plugin based system. To create a new authentication plugin you must:

- subclass ``commissaire_http.authentication.Authenticator``
- name the class ``AuthenticationPlugin``
- override the ``authenticate`` method

If you need to have configuration items passed when used you will also need to
override ``__init__`` adding in keyword arguments.

.. note::

   The ``authenticate`` should always return ``True`` for success,
   ``False`` for general failure, or handle responses itself as a WSGI
   application.

Examples
````````

Basic
~~~~~

.. code-block:: python

    from commissaire_http.authentication import Authenticator

    class AlwaysAllowOnSSL(Authenticator):
        """
        Example: Allows anyone if they use https.
        """

        def authenticate(self, environ, start_response):
            """
            Allows access if https is in use.

            :param environ: WSGI environment instance.
            :type environ: dict
            :param start_response: WSGI start response callable.
            :type start_response: callable
            :returns: True on success, False on failure
            :rtype: bool
            """
            if environ.get('wsgi.url_scheme', 'http') == 'https':
                return True
            return False

    #: Alias AlwaysAllowOnSSL
    AuthenticationPlugin = AlwaysAllowOnSSL


As a WSGI Application
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from commissaire_http.authentication import Authenticator

    class AlwaysAllowOnSSL(Authenticator):
        """
        Example: Allows anyone if they use https but pretends to be a teapot
        if they use http.
        """

        def authenticate(self, environ, start_response):
            """
            Allows access if https is in use.

            :param environ: WSGI environment instance.
            :type environ: dict
            :param start_response: WSGI start response callable.
            :type start_response: callable
            :returns: True on success, False on failure
            :rtype: bool
            """
            if environ.get('wsgi.url_scheme', 'http') == 'https':
                return True
            start_response("418 I'm a teapot", [('content-type', 'text/plain')])
            return [bytes('Whiiiiieee', 'utf8')]

    #: Alias AlwaysAllowOnSSL
    AuthenticationPlugin = AlwaysAllowOnSSL


Real Code
~~~~~~~~~
See `httpauthclientcert <https://github.com/projectatomic/commissaire-http/blob/master/src/commissaire_http/authentication/httpauthclientcert.py>`_
