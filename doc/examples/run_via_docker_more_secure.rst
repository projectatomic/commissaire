.. code-block:: shell

    docker run -d \
        -p 8000:8000
        -v /path/to/etcd/certificates:/certs \
        -e ETCD=https://192.168.152.100:2379 \
        -e KUBE=https://192.168.152.101:8080 \
        -e EXTRA_ARGS="--tls-certfile /certs/server.crt --tls-keyfile /certs/server.key --etcd-cert-path /certs/etcd.crt --etcd-cert-key-path /certs/etcd.key" \
        commissaire
    ...