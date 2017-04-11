.. _cloud_init:

Cloud-Init Integration
======================

Commissaire provides a ``commctl`` command to generate a ``user-data`` file
for ``cloud-init`` that automatically registers hosts to the Commissaire
server during bootup. This command is aptly named ``user-data``.


commctl user-data command
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: examples/commctl-user-data-help.txt


Create the User-Data File
~~~~~~~~~~~~~~~~~~~~~~~~~

Let's say you have the following properties:

* A Commissaire username of USER
* A Commissaire password of PASS
* A Commisaire cluster you want new hosts to join called CLUSTER
* A Commissaire REST Server listening at https://example.com/
* The expectation of having the ``user-data`` file at ``./CLUSTER.userdata``

You would create the ``user-data`` file like so:

.. code-block:: shell

   $ commctl user-data \
     --password \
     --username USER \
     --cluster CLUSTER \
     --endpoint https://example.com/ \
     --outfile CLUSTER.userdata
   Password: <PASS>
   $ # Let's check that the userdata file is indeed a multipart/mixed file
   $ file CLUSTER.userdata
   CLUSTER.userdata: multipart/mixed; boundary="===============8094544984785845936==, ASCII text
