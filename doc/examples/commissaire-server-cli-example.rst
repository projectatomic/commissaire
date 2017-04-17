
.. code-block:: shell

   $ commissaire-server --no-config \
       --bus-uri redis://127.0.0.1:6379/ \
       --bus-exchange commissaire \
       --tls-pemfile /path/to/server.pem \
       --listen-interface 8000 \
       --authentication-plugin commissaire_http.authentication.httpbasicauth:filepath=conf/users.json \
       --self-auth /api/v0/secrets
