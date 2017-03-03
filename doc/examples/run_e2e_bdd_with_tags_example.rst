The following command shows how to run all the create tests that are not marked
slow:

.. code-block:: shell

   # Set up ...
   (virtualenv)$ behave -k -t create,~slow \
       -D commissaire-server=http://127.0.0.1:8000 \
       -D etcd=http://127.0.0.1:2379 \
       -D bus-uri=redis://127.0.0.1:6379
   ...


The same thing using the ``./tools/behave`` script:

.. code-block:: shell

   # Set up ...
   (virtualenv)$ ./tools/behave -t create,~slow
   ...
