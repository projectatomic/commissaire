.. code-block:: shell

   $ cat /etc/commissaire/commissaire.conf
   {
     ...
     "register-store-handler": [
       "name": "commissaire.store.kubestorehandler",
       ...
       "token": "$KUBERNETES_ACCESS_TOKEN"
     ]
   }
