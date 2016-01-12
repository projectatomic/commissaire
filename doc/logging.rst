Logging
=======
Logging configuration is defined either in Etcd or via a local file. In both
cases the syntax is the same.


Example: Default Local file
---------------------------

.. literalinclude:: ../conf/logger.json
   :language: json


Using Etcd
----------

To put the configuration in Etcd set the ``/commissaire/config/logger`` key with
valid JSON.

.. code-block:: shell

   (virtualenv)$ cat conf/logger.json | etcdctl set '/commissaire/config/logger'
   ...
