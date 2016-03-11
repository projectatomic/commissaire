.. code-block:: shell

    docker run -d \
        -v /path/to/etcd/certificates:/certs \
        -e ETCD=https://127.0.0.1:2379 \
        -e KUBE=https://127.0.0.1:8080 \
        -e EXTRA_ARGS="--tls-certfile /certs/server.crt --tls-keyfile /certs/server.key --etcd-cert-path /certs/etcd.crt --etcd-cert-key-path /certs/etcd.key" \
        docker.io/commissaire/amhm
    ...