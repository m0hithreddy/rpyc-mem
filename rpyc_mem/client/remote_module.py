"""Remote Module Access"""


class RemoteModule:
    """
    Expose remote modules to create remote python objects

    :param rpyc_mem.connect.RpycMemConnect rmem_conn: Rpyc memory connection

    .. automethod:: __call__
    """

    def __init__(self, rmem_conn):
        """Initialize RemoteModule with rpyc memory connection"""
        self._rmem_conn = rmem_conn

    def __call__(self, module=None, package=None):
        """
        Return the ``modules`` of rpyc memory service hosts. If module is ``None`` assume ``builtins``.

        :param str module: The module to import in absolute or relative terms (Ex: pkg.mod, ..mod).
         Defaults to ``builtins``.
        :param str package: The package which acts as a base for resolving the module (should be set
         when relative imports are used)
        :return:
        """
        if not module:
            module = 'builtins'

        return self._rmem_conn.remote_import(module, package)
