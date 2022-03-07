"""Remote Module Access"""


class RemoteModule:
    """
    Expose remote modules to create remote python objects
    """

    def __init__(self, rmem_conn):
        self._rmem_conn = rmem_conn

    def __getattr__(self, name):
        """
        Return builtins/modules of 'rpyc memory service' hosts. Search in remote 'builtins'
        before attempting to import 'name' module.

        :param name: Remote builtins/module
        :return:
        """
        # Search in remote builtins
        try:
            return getattr(self._rmem_conn.remote_import('builtins'), name)
        except AttributeError:
            pass

        # Import 'name' module from rmem host
        return self._rmem_conn.remote_import(name)