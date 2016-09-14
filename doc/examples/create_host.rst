.. code-block:: shell

   curl -u "a:a" -XPUT -H "Content-Type: application/json" http://localhost:8000/api/v0/host/192.168.1.100 -d '{"host": "192.168.1.100", "cluster": "datacenter1", "remote_user": "root", "ssh_priv_key": "dGVzdAo="}'
   ...
