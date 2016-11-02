.. code-block:: shell

   $ cat /etc/commissaire/commissaire.conf
   {
     "listen-interface": "127.0.0.1",
     "listen-port": 8000,
     "tls-pemfile": "/path/to/server.pem",
     "bus-uri": "redis://127.0.0.1:6379/",
     "authentication-plugins": [{
       "name": "commissaire_http.authentication.httpbasicauth",
       "filepath": "conf/users.json"
     }]
   }
