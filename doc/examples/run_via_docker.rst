.. code-block:: shell

    docker run -d -p 8000:8000 -e ETCD=http://192.168.152.100:2379 -e KUBE=http://192.168.152.101:8080 commissaire
    ...