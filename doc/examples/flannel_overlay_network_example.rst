.. note::

   For more information as to why this is necessary see the `flannel documentation <https://coreos.com/flannel/docs/latest/flannel-config.html>`_ or the `Project Atomic Getting Started Guide <http://www.projectatomic.io/docs/gettingstarted/>`_

.. code-block:: shell

   (virtualenv)$  etcdctl set '/atomic01/network/config' '{"Network": "172.16.0.0/12", "SubnetLen": 24, "Backend": {"Type": "vxlan"}}'
   ...
