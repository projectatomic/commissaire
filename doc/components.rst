Components
==========

Internal
--------
The following are internal components of commissaire.

REST Interface
~~~~~~~~~~~~~~
The rest interface is the way an administrator works with commissaire. It
attempts to follow REST as strictly as possible through the interpretation of
commissaire developers.

Investigator
~~~~~~~~~~~~
The investigator is a subprocess which is tasked with investigating
and bootstrapping new host nodes. When a new host is added it's the
investigator which populates the host data in etcd and gets the right services
going on the new host.

ClusterExecPool
~~~~~~~~~~~~~~~
This is a static greenlet pool used for executing commands across a cluster. For
instance, a reboot of a cluser will utilize this pool to execute remote commands
in their own greenlet. Because the pool is limited there will only ever be X
number of the command being executed at once.


External
--------
The following are external components of commissaire.

etcd
~~~~
etcd is used as the data store for commissaire. Any persistent data is kept
within etcd as either traditional *key* = *value* pairs or as *key* = *JSON*. While
any etcd instance will work it's recommended to use the same etcd cluster with
kubernetes.

kubernetes
~~~~~~~~~~
kubernetes is used as the container manager. commissaire utilizes kubernetes
api to ensure that new host nodes register properly. From this point forward
kubernetes is able to use the host node to schedule pods, etc...