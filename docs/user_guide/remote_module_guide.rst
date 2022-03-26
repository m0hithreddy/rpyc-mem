Remote Module
---------------

``RemoteModule`` invokes ``remote_import`` of ``RpycMemService`` to provide access to remote modules for creating remote
objects. The objects of the client machine can not be shared with other clients as they come with no guarantee on their
longevity. Moreover, ``RPyC`` internals does not support that either. ``RemoteModule`` accepts the ``RpycMemConnect``
object for creating remote objects. ::

    from rpyc_mem.connect import RpycMemConnect
    from rpyc_mem.client import RemoteModule

    # Assuming service running on localhost:18813
    rc = RpycMemConnect('localhost', 18813)

    rp = RemoteModule(rc)

    rlist = rp().list([1, 2])
    for i in rlist:
        print(i)

    print(rlist.__class__ == list)
    print(type(rlist) == type([1]))
    print(type(rlist))

    rlock = rp('threading').Lock()
    rlock.acquire()
    print(rlock.locked())
    rlock.release()

    with rlock:
        print('synchronized operation')

    """
    Output:
    1
    2
    True
    False
    <netref class 'rpyc.core.netref.type'>
    True
    synchronized operation
    """


``RemoteModule`` supports `importlib.import_module <https://docs.python.org/3/library/importlib.html#importlib.import_module>`_ 
style imports. When ``module`` parameter is not passed, ``builtins`` is assumed by default.
