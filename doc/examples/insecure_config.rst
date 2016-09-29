
.. code-block:: shell

   $ cat /etc/commissaire/commissaire.conf
   {
     "listen-interface": "127.0.0.1",
     "listen-port": 8000,
     "bus-uri": "redis://127.0.0.1:6379/",
     "storage-handlers": [
       {
         "name": "commissaire.storage.etcd",
         "server_url": "http://192.168.152.101:2379",
         "models": []
       }
     ],
     "authentication-plugin": {
       "name": "commissaire.authentication.httpbasicauth",
       "users": {
         "a": {
           "hash": "$2a$12$GlBCEIwz85QZUCkWYj11he6HaRHufzIvwQjlKeu7Rwmqi/mWOpRXK"
         }
       }
     }
   }
