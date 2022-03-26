"""Remote Module Access"""


class RemoteModule:
    """
    Expose remote modules to create remote python objects

    :param Union[rpyc_mem.connect.RpycMemConnect, typing.Callable] rmem_conn: Rpyc memory connection
     or a callable that returns Rpyc memory connection

    .. automethod:: __call__
    """

    def __init__(self, rmem_conn):
        """Initialize RemoteModule with rpyc memory connection"""
        self._rmem_conn = rmem_conn

    @property
    def rmem_conn(self):
        """
        Return the Rpyc memory connection from ``_rmem_conn`` object. If ``_rmem_conn`` is
        callable return the result of ``_rmem_conn`` invocation else ``_rmem_conn``.

        :return:
        """
        if callable(self._rmem_conn):
            return self._rmem_conn()

        return self._rmem_conn

    def __call__(self, module='builtins', package=None):
        """
        Return ``modules`` of rpyc memory service hosts.

        :param str module: The module to import in absolute or relative terms (Ex: pkg.mod, ..mod).
         Defaults to ``builtins``.
        :param str package: The package which acts as a base for resolving the module (should be set
         when relative imports are used)

        :return:
        """
        return self.rmem_conn.remote_import(module, package)
