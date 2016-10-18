Commissaire HTTP
================

Commissaire HTTP provides a multithreaded REST interface into Commissaire
functionality. The server is broken up into 5 main parts: ``Router``,
``Dispatcher``, ``handlers``, and the ``CommissaireHttpServer`` itself.

Router
------
The ``Router`` maps URI paths to controllers. The following example would route
the path /hello/ to the controller at ``commissaire_http.handlers.hello_world``
if the HTTP method is ``GET``.

.. todo::

    Add example when a controller is a callable instead of a string.

.. code-block:: python

   mapper = Router()
   mapper.connect(
       '/hello/',
       controller='commissaire_http.handlers.hello_world',
       conditions={'method': 'GET'})


Dispatcher
----------
The ``Dispatcher`` uses a ``Router`` and, as it's name suggests, dispatches
the requests to the proper controller. It also takes care of loading
handlers. The following example creates a new ``Dispatcher`` instance using
a previously created ``Mapper``. It will load handlers found in the
``commissaire_http.handlers`` and ``mypackage.handlers`` packages.

.. code-block:: python

   dispatcher = Dispatcher(
       mapper,
       handler_packages=[
        'commissaire_http.handlers',
        'mypackage.handlers'])


Handlers
--------
``Handlers``, also called controllers, do the majority of the business logic.
A ``Handler`` can be a function or a class, but must follow a specific
convention so the ``Dispatcher`` knows it's valid during loading.

.. todo::

    Add section on creating a _register function for routing
    (see commissaire_http.handlers.clusters._register)

Function Handler
````````````````
Function handlers must take two parameters: ``message`` and ``bus``. The first
input, ``message``, is the jsonrpc message. The second input, ``bus`` will
either be a valid connection to the bus or, if the bus is not enabled,
``None``.

When referencing a function handler as a controller use the full package path
to the function. If the function is ``hello_world`` and it lives under
``commissaire_http.handlers`` then the controller would be
``commissaire_http.handlers.hello_world``.

The following example would show the user ``{"Hello": "there"}`` or
``{"Hello", "{{ name }}"}`` depending on parameters. Remember, the return of
the handler must be a valid jsonrpc message as well!

.. note::

    The ``method`` in the incoming jsonrpc message is hijacked and filled
    with the HTTP method that was used to call the handler.

.. code-block:: python

   def hello_world(message, bus):
       """
       Example function handler that simply says hello. If name is give
       in the query string it uses it.

       :param message: jsonrpc message structure.
       :type message: dict
       :returns: A jsonrpc structure.
       :rtype: dict
       """
       response_msg = {'Hello': 'there'}
       if message['params'].get('name'):
           response_msg['Hello'] = message['params']['name']
       return {
           'jsonrpc': '2.0',
           'id': message['id'],
           'result': response_msg,
       }


Class Handler
`````````````
A class handler is not much different than function handlers. Instead of
defining a single function, a class is declared with methods that take three
parameters: ``self``, ``message``, and ``bus``. If the method should not be
considered a handler it must start with an underscore.

One major difference between a class handler and function handler is that class
handlers are instantiated when they are loaded!

When referencing a class handler as a controller, use the full package path
to the class and the method. If the class is ``ClassHandlerExample``,
the method is ``hello``, and it lives under ``commissaire_http.handlers``
then the controller would be
``commissaire_http.handlers.ClassHandlerExample.hello``.

The following example exposes ``hello`` in the same way as the above function
handler. It then uses ``hello_world`` to do the heavy lifting.

.. code-block:: python

   class ClassHandlerExample:
       """
       Example class based handlers.
       """

       def hello(self, message, bus):
           """
           Example method handler that simply says hello. If name is given
           in the query string it uses it.

           :param message: jsonrpc message structure.
           :type message: dict
           :returns: A jsonrpc structure.
           :rtype: dict
           """
           return hello_world(message, bus)

       def _ignored(self):
           """
           This method would not be loaded as a handler but could be used by
           handlers in this class.
           """
           return 'I am ignored.'


CommissaireHttpServer
---------------------

In the following example a ``CommissaireHttpServer`` is created which binds to
address 127.0.0.1 and port 8000 and uses a previously created dispatcher. It
then is set to run (block) until killed.

.. code-block:: python

   server = CommissaireHttpServer('127.0.0.1', 8000, dispatcher)
   server.serve_forever()


Code Example
------------

See `http_server <https://github.com/projectatomic/commissaire-http/blob/master/example/http_server.py>`_.
