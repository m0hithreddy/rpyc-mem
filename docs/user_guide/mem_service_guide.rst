RPyC Memory Service
-------------------

Often in distributed computing their is a need for sharing state (data) between multiple parallel running processes.
``RpycMemService`` allows to host a shared memory service on a network, which can be used to share state (objects) among
multiple processes. The RpycMemService is an ``RPyC`` service tailored to offer memory management routines. Hosting a
service is straight-forward::

    from rpyc_mem.service import RpycMemService

    rs = RpycMemService('localhost', 18813) # Defaults: host='0.0.0.0', port=random
    rs.run()


For maintaining a single snapshot of the memory, RpycMemService is supposed to be ran with a ``ThreadedServer`` or
variants of it. ``run()`` method can take an optional ``server`` argument; by default ``ThreadedServer`` is used. The
kwargs used to run the server can be updated by passing ``server_kwargs`` argument. ::

    default_kwargs = {
                        'service': self.__class__,
                        'hostname': self._hostname,  # from __init__
                        'port': self._port,  # from __init__
                        'protocol_config': {
                            'allow_all_attrs': True,
                            'allow_setattr': True,
                            'allow_delattr': True
                        }
                      }

    default_kwargs.update(server_kwargs)


Refer to `RPyC documentation <https://rpyc.readthedocs.io/en/latest/api/utils_server.html>`_ for the servers that come
inbuilt. If the port is left out, a random port is assigned which can be accessed through ``self.server_obj.port``
(this is available only after the service is ran).

In the background, ``RpycMemService`` maintains a mapping between the key and the object in a dict. All management
routines need the unique-key for operating on the corresponding object. The RpycMemService comes with all basic memory
management routines; ``memoize``, ``get``, ``update``, ``delete``, ``is_memoized`` (``remote_import``, ``rpyc_version``).
Most of them are self explanatory, refer to the API documentation for the specifics of each routine.

There is a concept of remote object and remote object generator in RpycMemService. The term **remote** signifies that the
object is remote to the client machine. The remote machine where the object resides can be any remote machine, but in
general we use the remote objects of one service with the same. The client objects should not be used as shared objects
(reasons and creating remote objects are explained in the ``Remote Module`` guide). The remote object generator is simply
a callable which returns a remote object, this is primarily for delayed execution, particularly in the case of memoization
(dont need to create a new object if the mapping already exists against the key).
