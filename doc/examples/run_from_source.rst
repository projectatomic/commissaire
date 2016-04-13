
.. code-block:: shell

   (virtualenv)$ PYTHONPATH=`pwd`/src python src/commissaire/script.py \
       --etcd-uri http://127.0.0.1:2379 \
       --kube-uri http://127.0.0.1:8080 \
       --authentication-plugin commissaire.authentication.httpauthbyfile \
       --authentication-plugin-kwargs "filepath=conf/users.json" &
   ...
