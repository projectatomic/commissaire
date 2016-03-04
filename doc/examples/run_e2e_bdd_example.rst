
.. code-block:: shell

   (virtualenv)$ behave -D start-etcd=true -D start-server=true
   ...


You can also run the tests against any commissaire/etcd instance directly.

.. warning::

   Do **not** point to a real instance of commissaire. e2e/BDD tests will
   simulate real usage on a running server and will probably cause damage.

See :ref:`manual_installation` for how to set up commissaire.

.. code-block:: shell

   # Set up ...
   (virtualenv)$ behave -D server=http://127.0.0.1:8000 -D etcd=http://127.0.0.1:2379
   ...
