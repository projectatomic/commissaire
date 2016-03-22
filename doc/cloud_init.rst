.. _cloud_init:

Cloud-Init Integration
======================

commissaire provides a script in ``config/cloud-init/part-handler.py``
to help automatically register hosts to the commissaire server during
bootup by way of cloud-init.

The script is intended to be embedded or referenced by an ``#include``
directive in a multi-part ``user-data`` file, along with a simple config
file containing the server parameters.

Here's a sample config file showing all recognized parameters:

::

  # Host name of the commissaire service.
  COMMISSAIRE_SERVER_HOST = master.example.com

  # (optional) Port number of the commissaire service. Defaults to 8000.
  COMMISSAIRE_SERVER_PORT = 8000

  # (optional) User name to use for commissaire service authentication.
  COMMISSAIRE_SERVER_USERNAME = user

  # (optional) Password to use for commissaire service authentication.
  COMMISSAIRE_SERVER_PASSWORD = 12345

  # (optional) Boolean value indicates whether to connect to the
  # service using Transport Layer Security (TLS). Defaults to true.
  COMMISSAIRE_SERVER_SECURE = true

  # (optional) The name of the cluster to join.
  COMMISSAIRE_CLUSTER = mycluster

  # (optional) The private SSH key file for the root account of this
  # host. Defaults to '/root/.ssh/id_rsa' and, if necessary, generates
  # a public/private key pair with no passphrase.
  ROOT_SSH_KEY_PATH = /root/.ssh/id_rsa


Create the User-Data File
~~~~~~~~~~~~~~~~~~~~~~~~~

The ``user-data`` file must use MIME multipart/mixed format.  You can
generate such a file with the make-mime.py_ script in cloud-init's
``tools`` directory.

.. _make-mime.py: http://bazaar.launchpad.net/~cloud-init-dev/cloud-init/trunk/view/head:/tools/make-mime.py

Suppose the config file above is named ``commissaire.txt``.  To assemble
it, the ``part-handler.py`` script and a cloud-config file named, say,
``config.txt`` into a valid MIME multipart/mixed structure, use the
``make-mime.py`` script as follows:

.. code-block:: shell

   $ python make-mime.py \
            --attach config.txt:cloud-config \
            --attach part-handler.py:part-handler \
            --attach commissaire.txt:x-commissaire-host \
            > user-data

.. note::

   The content type of the ``commissaire.txt`` config file must be
   ``text/x-commissaire-host`` (the attach option assumes the "text/" part).

Alternatively, you can instruct cloud-init to download the ``part-handler.py``
script from a URL at boot time by attaching a ``text/x-include-url`` file:

.. code-block:: shell

   $ python make-mime.py \
            --attach config.txt:cloud-config \
            --attach include.txt:x-include-url \
            --attach commissaire.txt:x-commissaire-host \
            > user-data

.. note::

   Whether the part handler is included by way of direct embedding or a URL,
   it must appear in the multipart file `before` the ``text/x-commissaire-host``
   part so cloud-init knows how to handle the ``text/x-commissaire-host`` part.
