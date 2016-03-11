.. note::

   Using client side certificates to access etcd/kubernetes will require proper configuration within etcd/kubernetes.

.. code-block:: shell

   (virtualenv)$ PYTHONPATH=`pwd`/src python src/commissaire/script.py  \
       --kube-uri https://127.0.0.1:8080 \
       --tls-keyfile /path/to/server.key \
       --tls-certificate /path/to/server.crt \
       --etcd-uri https://127.0.0.1:2379
       --etcd-cert-path /path/to/etcd_clientside.crt \
       --etcd-cert-key-path /path/to/etcd_clientside.key &
   ...