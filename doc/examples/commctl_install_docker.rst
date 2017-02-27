
From a checkout of the ``commctl`` repository:

.. code-block:: shell

   $ sudo docker build -t commctl .  # Done once to build the image
   ...
   $ sudo docker run -t -i --volume=`pwd`/.commissaire.json:/root/.commissaire.json:Z commctl --help
