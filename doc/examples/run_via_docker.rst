.. code-block:: shell

    $ sudo docker run --detach \
        --publish 8000:8000 \
        --volume /path/to/config:/etc/commissaire \
        --volume /path/to/certificates:/certs \
        commissaire
    ...
