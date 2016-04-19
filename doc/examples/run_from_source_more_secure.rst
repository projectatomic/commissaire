.. note::

   Using client side certificates to access etcd/kubernetes will require proper configuration within etcd/kubernetes.

.. code-block:: shell

   (virtualenv)$ PYTHONPATH=`pwd`/src python src/commissaire/script.py  \
       --tls-keyfile /path/to/server.key \
       --tls-certificate /path/to/server.crt \
       --etcd-uri https://192.168.152.100:2379
       --etcd-cert-path /path/to/etcd_clientside.crt \
       --etcd-cert-key-path /path/to/etcd_clientside.key \
       --authentication-plugin commissaire.authentication.httpauthbyfile \
       --kube-uri https://192.168.152.101:8080 \
       --authentication-plugin-kwargs "filepath=conf/users.json" &
   ...