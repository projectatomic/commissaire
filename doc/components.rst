Components
==========

Internal
--------
The following are internal components of commissaire.

Commissaire Server
~~~~~~~~~~~~~~~~~~
The commissaire server is the ``REST`` interface and is how an administrator works
with commissaire. It attempts to follow ``REST`` as strictly as possible through
the interpretation of commissaire developers.


Services
~~~~~~~~
See :ref:`commissaire_services`

External
--------
The following are external components of commissaire.

etcd
~~~~
etcd is used as the data store for commissaire. Any persistent data is kept
within etcd as either traditional *key* = *value* pairs or as *key* = *JSON*. While
any etcd instance will work it's recommended to use the same etcd cluster with
Kubernetes.

Container Manager
~~~~~~~~~~~~~~~~~
OpenShift or Kubernetes can be used as the container manager. commissaire utilizes
Kubernetes API to ensure that new host nodes register properly. From this point
forward Kubernetes is able to use the host node to schedule pods, etc...
