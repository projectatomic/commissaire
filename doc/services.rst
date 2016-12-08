.. _commissaire_services:

Commissaire Services
====================

Commissaire Service is a framework for writing long running services for the
Commissaire management system. It provides a standard way to connect to
Commissaire's message bus and provide/consume services.

Example Use Cases
-----------------

Commissaire Clusterexec
```````````````````````

.. todo::

    Add commissaire-clusterexec-service

Commissaire Container Manager
``````````````````````````````
Commissaire's ``Container Manager`` service is a set of long running processes which provide
a consistant API to work with container managers.


Example Configuration File
~~~~~~~~~~~~~~~~~~~~~~~~~~
By default ``commissaire-clustermgr-service`` looks at ``/etc/commissaire/containermgr.conf``
for it's configuration. This can be overriden with the ``-c/--config`` flag.

.. literalinclude:: ../../commissaire-service/conf/containermgr.conf

Commissaire Investigator
````````````````````````
Commissaire's ``Investigator`` is a set of long running processes which
connect to and bootstrap new hosts wanting to be managed by Commissaire.


Commissaire Watcher
```````````````````

.. todo::

    Currently not ported to new architecture.

Commissaire's ``Watcher`` is a set of long running processes which periodically
connects to hosts that have already been bootstrapped and checks their status.


Commissaire Storage
```````````````````
Commissaire's ``Storage`` is a set of long running processes which broker storage
and retrieval requests of persistent data.


Writing a Service
-----------------

High Level
----------

* Subclass ``commissaire_service.service.CommissaireService``
* Define all ``on_{{ method }}`` methods to exposed them on the message bus
* Define how to run the service (Directly or via a ServiceManager)

Specifics
---------

Create the Subclass
```````````````````

All Commissaire Services must subclass (or reimplement the functionality of...)
``commissaire_service.service.CommissaireService``.

.. code-block:: python

    from commissaire_service.service import CommissaireService


    class MyService(CommissaireService):
        """
        This is MyService.
        """
        pass


Define Exposed methods
``````````````````````

``CommissaireService`` uses the ``on_{{ method }}`` convention for exposing methods
to remote callers. If you wanted to expose a method as ``ping`` you would
define a method on your service called ``on_ping``. ``on_{{ method }}``'s
expect to take 1 or more arguments where the 1 required argument is ``message``
which is the message itself in the case the method needs extra information.

To return results back to the caller via the message bus simply use the ``return``
statement as if it was a normal method. If there is an error ``raise`` the
proper exception. These will be transformed into proper messages and returned
to the message bus and passed to the caller.

.. note::

    message must always be the **first** argument!

.. code-block:: python

    def on_ping(self, message):
        """
        Exposed as ping. Takes no bus arguments.
        """
        return 'pong'

    def on_echo(self, message, words):
        """
        Exposed as echo. Takes one bus argument of words.
        """
        return words

    def on_fail(self, message):
        """
        Exposed as fail. Takes no bus arguments.
        """
        raise NotImplementedError('I was never created')


Running the Service
-------------------
The simplest way to run a ``CommissaireService`` is to create an instance
and use it's ``run`` method.

.. code-block:: python

    #: The arguments used to create new kombu.Queue instances
    queue_kwargs = [
        {'name': 'my_queue', 'routing_key': 'queues.my_queue.*'},
    ]

    try:
        MyService(
            exchange_name='my_exchange',
            connection_url='redis://127.0.0.1:6379/',
            qkwargs=queue_kwargs
        ).run()
    except Exception as error:
        # Handle it ;-)
        pass


A more likely pattern is to run multiple instances of a service on the same
queue to be able to handle more requests. This can be done by wrapping the
service in a ``ServiceManager``. As you can see it follows a similar pattern
as the ``CommissaireService`` prepending a few inputs required for
running multiple processes.

.. note::

    Debugging with multiple processes can be much harder. If you need to debug
    a service it is recommend to use the ``CommissaireService`` directly to
    ensure no ``Exception`` information gets eaten up between the process pool
    and service.

.. code-block:: python

    #: The arguments used to create new kombu.Queue instances
    queue_kwargs = [
        {'name': 'my_queue', 'routing_key': 'queues.my_queue.*'},
    ]

    try:
        ServiceManager(
            service_class=MyService,
            process_count=3,
            exchange_name='my_exchange',
            connection_url='redis://127.0.0.1:6379/',
            qkwargs=queue_kwargs
        ).run()
    except Exception as error:
        pass


Code Example
------------

See `simpleservice <https://github.com/projectatomic/commissaire-service/blob/master/example/simpleservice.py>`_.
