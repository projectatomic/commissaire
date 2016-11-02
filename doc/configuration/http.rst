REST Configuration
==================

.. todo::

   Wordsmithing.


.. _rest_configuration_file:

Configuration File
------------------

.. include:: ../examples/secure_rest_config.rst


.. _rest_configuration_cli:

Via CLI
-------

.. include:: ../examples/commissaire-server-cli.rst


Example
~~~~~~~

The following will run the same server as the above configuration file examples.

.. note::

   ``--no-config`` is required when bypassing the configuration file!

.. include:: ../examples/commissaire-server-cli-example.rst


Authentication
~~~~~~~~~~~~~~

Multiple authentication plugins can be configured via the CLI. To do this use the
``--authentication-plugin`` switch multiple times.

.. include:: ../examples/commissaire-server-cli-multiple-auth.rst
