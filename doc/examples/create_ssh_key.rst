This creates a new ssh public and private key as ``new_key.pub`` and ``new_key``.

.. code-block:: shell

   $ ssh-keygen -f new_key -C root
   Generating public/private rsa key pair.
   Enter passphrase (empty for no passphrase): 
   Enter same passphrase again: 
   Your identification has been saved in new_key.
   Your public key has been saved in new_key.pub.
   The key fingerprint is:
   SHA256:YoFOXojY0tIkAQBRiPe00HWQdJ8zgOylJwDuQXXJfXc steve@bitfall
   The key's randomart image is:
   +---[RSA 2048]----+
   |O%oo=.=*Bo.      |
   |*.*+ Bo+*= . E   |
   |oo .o Eo=.. .    |
   |+.  + o .        |
   |...   o+S        |
   |oo oo  .    ..   |
   |+ . +            |
   | ..              |
   |                 |
   +----[SHA256]-----+
