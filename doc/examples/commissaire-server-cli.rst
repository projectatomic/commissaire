
.. code-block:: shell

   usage: commissaire-server [-h] [--config-file CONFIG_FILE] [--no-config-file]
                             [--listen-interface LISTEN_INTERFACE]
                             [--listen-port LISTEN_PORT]
                             [--tls-pemfile TLS_PEMFILE]
                             [--tls-clientverifyfile TLS_CLIENTVERIFYFILE]
                             [--authentication-plugin MODULE_NAME:key=value,..]
                             [--bus-exchange BUS_EXCHANGE] [--bus-uri BUS_URI]
   
   optional arguments:
     -h, --help            show this help message and exit
     --config-file CONFIG_FILE, -c CONFIG_FILE
                           Full path to a JSON configuration file (command-line
                           arguments override)
     --no-config-file      Disregard default configuration file, if it exists
     --listen-interface LISTEN_INTERFACE, -i LISTEN_INTERFACE
                           Interface to listen on
     --listen-port LISTEN_PORT, -p LISTEN_PORT
                           Port to listen on
     --tls-pemfile TLS_PEMFILE
                           Full path to the TLS PEM for the commissaire server
     --tls-clientverifyfile TLS_CLIENTVERIFYFILE
                           Full path to the TLS file containing the certificate
                           authorities that client certificates should be
                           verified against
     --authentication-plugin MODULE_NAME:key=value,..
                           Authentication Plugin module and configuration.
     --bus-exchange BUS_EXCHANGE
                           Message bus exchange name.
     --bus-uri BUS_URI     Message bus connection URI. See:http://kombu.readthedo
                           cs.io/en/latest/userguide/connections.html

