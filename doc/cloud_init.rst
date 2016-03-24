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

.. literalinclude:: ../contrib/cloud-init/commissaire.txt
   :language: shell

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


Example
-------

.. code-block:: shell

  $ wget "http://bazaar.launchpad.net/~cloud-init-dev/cloud-init/trunk/download/head:/makemime.py-20130122042101-yeyh09eokb87l6oa-1/make-mime.py"
  # <snip>
  2016-03-24 10:54:33 (167 MB/s) - ‘make-mime.py’ saved [1946/1946]

  $ wget "https://raw.githubusercontent.com/projectatomic/commissaire/master/contrib/cloud-init/part-handler.py"
  # <snip>
  2016-03-24 10:56:33 (772 MB/s) - ‘part-handler.py’ saved [4848/4848]

  $ wget "https://raw.githubusercontent.com/projectatomic/commissaire/master/contrib/cloud-init/commissaire.txt"
  # <snip>
  2016-03-24 10:57:07 (752 MB/s) - ‘commissaire.txt’ saved [866/866]

  $ $EDITOR config.txt     # Edit the cloud config to your liking
  $ $EDITOR commisaire.txt # Edit the commissaire config to your liking
  $ python make-mime.py \
         --attach config.txt:cloud-config \
         --attach part-handler.py:part-handler \
         --attach commissaire.txt:x-commissaire-host \
         > user-data
  WARNING: content type 'text/x-commissaire-host' for attachment 3 may be incorrect!
  $