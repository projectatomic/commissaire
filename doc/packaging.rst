Building Packages
=================

RPM
---
commissaire's spec file is located in the `Fedora package
repo <http://pkgs.fedoraproject.org/cgit/rpms/commissaire-client.git/tree/>`_.

Generate the Source Distribution
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: shell

   (virtualenv)$ ./setup.py sdist
   ...


Move Source Distribution To RPM Source
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note::

   Your rpmbuild root may be different! Check with your distribution.

.. code-block:: shell

   (virtualenv)$ mv dist/*.tar.gz ~/rpmbuild/SOURCES/`./setup.py --version`.tar.gz


Build The Package
~~~~~~~~~~~~~~~~~

.. code-block:: shell

   (virtualenv)$ rpmbuild -ba contrib/package/rpm/commissaire.spec
   ...

Your package should now be output in your rpmbuild root's ``RPMS/noarch/`` and
``SRPMS`` directories.
