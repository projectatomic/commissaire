.. code-block:: shell

   $ commctl user-data \
     --password \
     --username USER \
     --cluster CLUSTER \
     --endpoint https://example.com/ \
     CLUSTER.userdata
   Password: <PASS>
   $ # Let's check that the userdata file is indeed a multipart/mixed file
   $ file CLUSTER.userdata
   CLUSTER.userdata: multipart/mixed; boundary="===============8094544984785845936==, ASCII text
