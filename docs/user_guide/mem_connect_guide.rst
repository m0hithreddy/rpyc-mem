RPyC Memory Connect
-------------------

``RpycMemConnect`` is a wrapper around `rpyc.connect <https://rpyc.readthedocs.io/en/latest/api/core_protocol.html#rpyc.
core.protocol.Connection>`_ to connect with ``RpycMemService``. ``RpycMemConnect`` performs some basic error recovery
and validations. ::

        import rpyc

        from rpyc_mem.connect import RpycMemConnect

        """
        Assuming RpycMemService running on localhost:18813

        Defaults: max_retry=4
                  retry_delay=3
                  ignore_version=False
        """
        rc = RpycMemConnect('localhost', 18813)

        print(rc.rpyc_version())    # (5, 1, 0)
        print(rpyc.__version__ == rc.rpyc_version())    # True
        print(rc.root.memoize == rc.memoize)    # True
        print(rc.is_memoized('not_memoized'))    # False


``RPyC`` `warns <https://rpyc.readthedocs.io/en/latest/install.html#cross-interpreter-compatibility>`_ against having
different versions for client and server; when the ``ignore_version`` is ``False``, having different versions will raise
an exception during ``__init__``. The attributes that are not defined by ``RpycMemConnect`` are searched in the underlying
RPyC connection object, Ex: ``rc.root`` will invoke ``getattr(self._rmem_conn, 'root')``. The ``RpycMemService``
attributes can be accessed as if they were defined under ``RpycMemConnect`` namespace, Ex: ``rc.memoize == rc.root.memoize``

``RpycMemConnect`` performs some basic error recovery as configured by ``max_retry`` and ``retry_delay``. If you want to
bypass this you can work with raw connection object ``rc._rmem_conn``. ``RpycMemConnect`` has these additional attributes:

    * ``rc.setup_rmem_conn()`` - Re-setup the connection (attempt-close and open).
    * ``rc.rmem_except_handler()`` - Function decorator for handling the connection errors when working with raw
      connection object
    * ``rc.close()`` - Close the underlying RPyC connection. Connection errors are no more handled (until the connection
      is re-setup)

The following snippet shows their usage::

    from rpyc_mem.connect import RpycMemConnect

    rc = RpycMemConnect('localhost', 18813, max_retry=1)
    rc.close()

    # Working with raw connection object
    try:
        rc._rmem_conn.root.rpyc_version()
    except EOFError:
        rc.setup_rmem_conn()    # Re-setup the connection ([attempt] close and open)
        print(rc._rmem_conn.root.rpyc_version())

    # Recovery from connection failures
    rc._rmem_conn.close()   # With rc.close() connection errors are no more handled
    print(rc.rpyc_version())

    # Using exception handlers when working with raw connection object
    rc._rmem_conn.close()

    def reconnect_hook():
        print('re-connected')

    @rc.rmem_except_handler(on_reconnect=reconnect_hook)
    def rmem_fn():
        """Function that uses rpyc connection object"""
        print(rc._rmem_conn.root.is_memoized('not_memoized'))

    rmem_fn()

    """
    Output:
    (5, 1, 0)
    (5, 1, 0)
    re-connected
    False
    """


