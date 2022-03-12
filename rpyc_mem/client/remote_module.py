"""Remote Module Access"""


class RemoteModule:
    """
    Expose remote modules to create remote python objects

    :param rpyc_mem.connect.RpycMemConnect rmem_conn: Rpyc memory connection

    .. automethod:: __getattr__
    """

    def __init__(self, rmem_conn):
        """Initialize RemoteModule with rpyc memory connection"""
        self._rmem_conn = rmem_conn

    def __getattr__(self, name):
        """
        Return ``builtins``/``modules`` of rpyc memory service hosts. Search in remote
        ``builtins`` before attempting to import ``name`` module.

        :param str name: Name of the remote builtins/module
        :return:
        """
        # Search in remote builtins
        try:
            return getattr(self._rmem_conn.remote_import('builtins'), name)
        except AttributeError:
            pass

        # Import 'name' module from rmem host
        return self._rmem_conn.remote_import(name)
