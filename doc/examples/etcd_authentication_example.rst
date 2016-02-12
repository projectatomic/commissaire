.. code-block:: shell

   (virtualenv)$ cat conf/users.json | etcdctl set '/commissaire/config/httpbasicauthbyuserlist'
   ...
