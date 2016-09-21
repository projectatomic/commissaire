.. code-block:: shell

   $ cat /etc/commissaire/commissaire.conf
   {
     "listen-interface": "127.0.0.1",
     "listen-port": 8000,
     "tls-certfile": "/path/to/server.crt",
     "tls-keyfile": "/path/to/server.key",
     "storage-handlers": [
       {
         "name": "commissaire.storage.etcd",
         "server_url": "https://192.168.152.100:2379",
         "certificate_path": "/path/to/etcd_clientside.crt",
         "certificate_key_path": "/path/to/etcd_clientside.key",
         "models": []
       }
     ],
     "authentication-plugin": {
       "name": "commissaire.authentication.httpbasicauth",
       "filepath": "conf/users.json"
     }
   }

