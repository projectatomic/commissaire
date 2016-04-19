
.. code-block:: shell

   (virtualenv)$ PYTHONPATH=`pwd`/src python src/commissaire/script.py \
       --etcd-uri http://192.168.152.100:2379 \
       --kube-uri http://192.168.152.101:8080 \
       --authentication-plugin commissaire.authentication.httpauthbyfile \
       --authentication-plugin-kwargs "filepath=conf/users.json" &
   ...
