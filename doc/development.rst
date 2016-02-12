Getting Involved
================

Development Location
--------------------
The code for commissaire lives on GitHub. The main repo can be found at
https://github.com/projectatomic/commissaire.

Development Setup
-----------------

You will want to set up a virtualenv to work with. This will keep from poluting
your system with application only dependencies while you code.

.. include:: examples/setup_virtualenv.rst

.. note::

   Any time you will be working on commissaire make sure to activate the virtualenv

Getting Up To Speed
-------------------

As you can see commissaire uses a number of libraries.

.. literalinclude:: ../requirements.txt

Of these, the most important to be up to speed on are:

- gevent: http://www.gevent.org/
- falcon: http://falconframework.org/

Coding Standards
-----------------

Convention
~~~~~~~~~~
Like most projects commissaire expects specific coding standards to be followed.
`pep8 <https://www.python.org/dev/peps/pep-0008/>`_ is followed strictly with
the exception of E402: module level import not at top of file.

Compatibility
~~~~~~~~~~~~~
Code shoulld attempt to be compatible with both Python 2 and Python 3. When
this is not possible it's assumed a workaround can be created in the
`commissaire.compat package <apidoc/commissaire.compat.html>`_  module.
If that is also not possible then Python 2 should be the fallback syntax.

Testing
~~~~~~~
commissaire uses TravisCI to verify that all unittests are passing.
**All unittests must pass and coverege must be above 80% before code
will be accepted. No exceptions.**.

To run unittests locally and see where your code stands:

.. include:: examples/run_unittest_example.rst
