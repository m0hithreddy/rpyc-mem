"""RPyC Memory Service"""

import threading
from importlib import import_module

import rpyc
from rpyc.utils.server import ThreadedServer

from rpyc_mem.errors import RpycMemSvcError


class RpycMemService(rpyc.Service):
    """
    RPyC memory service provides functionality to create named and unnamed python objects on remote
    hosts (one which runs this service). The remote objects are created using remote modules (see
    ``remote_import``). By default all objects created are unnamed, they can be mapped against
    unique_key to make them named. named objects can be managed using unique_key. This service is
    intended to be run with ``rpyc.utils.server.ThreadingServer`` or variants of it to maintain one
    snapshot of the memory

    :param str hostname: Hostname on which the service is run. Runs on ``0.0.0.0`` by default.
    :param int port: Port on which the service is run. Picks a random by default. Can be queried
     back with ``self._server_obj.port`` (this is available only when the service is ran).
    :param args: Left for ``RPyC`` during ``Service`` initialization
    :param kwargs: Left for ``RPyC`` during ``Service`` initialization
    """

    _ALLOWED_GET_ATTRS = [
        'memoize', 'get', 'update', 'delete', 'is_memoized', 'remote_import',
        'rpyc_version'
    ]
    _DEFAULT = object()

    _memoize_lock = threading.Lock()
    _sharedmem = dict()

    def __init__(self, hostname=None, port=None, *args, **kwargs):
        """Initialize Rpyc memory service"""
        super().__init__(*args, **kwargs)

        self._hostname = hostname
        self._port = port
        self._server_obj = None

    def run(self, server=None, server_kwargs=None):
        """
        Run the RPyC memory service. The ``host`` and ``port`` used are picked from the ``__init__``
        configuration. By default ``ThreadingServer`` is used, however this can be altered by
        passing different ``server`` and associated ``server_kwargs``.

        :param server: The server to use for running the service.
        :param server_kwargs: Update the default server arguments with these.
        :return:
        """
        if not server:
            server = ThreadedServer

        kwargs = {
            'service': self.__class__,
            'protocol_config': {
                'allow_all_attrs': True,
                'allow_setattr': True,
                'allow_delattr': True
            }
        }
        if self._hostname:
            kwargs['hostname'] = self._hostname

        if self._port:
            kwargs['port'] = self._port

        if server_kwargs:
            kwargs.update(server_kwargs)

        self._server_obj = server(**kwargs)
        self._server_obj.start()

    @classmethod
    def memoize(cls, unique_key, robj=_DEFAULT, robj_gen=_DEFAULT):
        """
        Memoize the mapping of remote object or remote object returned by the generator against
        the unique_key

        :param unique_key: The unique_key for creating/querying the mapping
        :param typing.Any robj: The remote object for memoization (One among ``robj``, ``robj_gen``
         should be passed)
        :param typing.Callable robj_gen: The remote object generator for memoization (One among ``robj``,
         ``robj_gen`` should be passed)
        :return: The memoized object
        """
        if not cls._validate_obj_sources(robj, robj_gen):
            raise RpycMemSvcError('Either object or object generator should be passed')

        with cls._memoize_lock:
            if unique_key not in cls._sharedmem:
                if robj is not cls._DEFAULT:
                    cls._sharedmem[unique_key] = robj
                else:
                    cls._sharedmem[unique_key] = robj_gen() # noqa

            return cls._sharedmem[unique_key]

    @classmethod
    def get(cls, unique_key):
        """
        Get the remote object against the unique_key. Raise an exception if the mapping is not present

        :param unique_key: The unique_key for querying the mapping
        :return: The memoized object
        """
        with cls._memoize_lock:
            if unique_key not in cls._sharedmem:
                raise RpycMemSvcError('No remote object exists against the key')

            return cls._sharedmem[unique_key]

    @classmethod
    def update(cls, unique_key, robj=_DEFAULT, robj_gen=_DEFAULT):
        """
        Update the mapping with the remote object or remote object returned by the generator against
        the unique_key (create new mapping if it doesnt exist)

        :param unique_key: The unique_key for updating the mapping
        :param typing.Any robj: The remote object for update (One among ``robj``, ``robj_gen`` should
         be passed)
        :param typing.Callable robj_gen: The remote object generator for update (One among ``robj``,
         ``robj_gen`` should be passed)
        :return: The updated object
        """
        if not cls._validate_obj_sources(robj, robj_gen):
            raise RpycMemSvcError('Either object or object generator should be passed')

        with cls._memoize_lock:
            if robj is not cls._DEFAULT:
                cls._sharedmem[unique_key] = robj
            else:
                cls._sharedmem[unique_key] = robj_gen() # noqa

            return cls._sharedmem[unique_key]

    @classmethod
    def delete(cls, unique_key):
        """
        Delete the mapping against the unique_key. Raise an exception if the mapping is not present

        :param unique_key: The unique_key for deleting the mapping
        :return:
        """

        with cls._memoize_lock:
            if unique_key not in cls._sharedmem:
                raise RpycMemSvcError('No remote object exists against the key')

            del cls._sharedmem[unique_key]

    @classmethod
    def is_memoized(cls, unique_key):
        """
        Return ``True`` if a mapping exists against the unique_key

        :param unique_key: The unique_key for querying the mapping
        :return:
        """
        with cls._memoize_lock:
            return unique_key in cls._sharedmem

    @classmethod
    def remote_import(cls, module, package=None):
        """
        Make remote modules available to the clients, primarily for creating remote objects

        :param str module: The module to import in absolute or relative terms (Ex: pkg.mod, ..mod)
        :param str package: The package which acts as a base for resolving the module (should be set
         when relative imports are used)
        :return: Remote module
        """
        return import_module(module, package)

    @classmethod
    def rpyc_version(cls):
        """
        Return ``RPyC`` version of the server

        :return:
        """
        return rpyc.__version__

    @classmethod
    def _validate_obj_sources(cls, robj, robj_gen):
        """
        Validate the object sources. Return False if both robj, robj_gen are set/not-set else True

        :param robj: The remote object
        :param robj_gen: The remote object generator
        :return:
        """
        if (robj is cls._DEFAULT and robj_gen is cls._DEFAULT) or \
                (robj is not cls._DEFAULT and robj_gen is not cls._DEFAULT):
            return False

        return True

    def _rpyc_getattr(self, name):
        """RPyC get attribute"""
        if name in self._ALLOWED_GET_ATTRS:
            return getattr(self, name)

        raise AttributeError(
            "'%s' object has no attribute '%s'" % (self.__class__.__name__, name)
        )

    def _rpyc_setattr(self, name, value):
        """RPyC set attribute"""
        if name in self._ALLOWED_GET_ATTRS:
            raise AttributeError('access denied')

        raise AttributeError(
            "'%s' object has no attribute '%s'" % (self.__class__.__name__, name)
        )

    def _rpyc_delattr(self, name):
        """RPyC delete attribute"""
        if name in self._ALLOWED_GET_ATTRS:
            raise AttributeError('access denied')

        raise AttributeError(
            "'%s' object has no attribute '%s'" % (self.__class__.__name__, name)
        )
