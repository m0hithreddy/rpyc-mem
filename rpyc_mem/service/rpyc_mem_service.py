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
    remote_import). By default all objects created are unnamed, they can be mapped against unique_key
    to make them named. This service is intended to be run with 'rpyc.server.ThreadingServer' to maintain
    one snapshot of the memory
    """

    DEFAULT = object()

    _memoize_lock = threading.Lock()
    _sharedmem = dict()

    def __init__(self, hostname=None, port=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._hostname = hostname
        self._port = port

    def run(self, server=None, server_kwargs=None):
        """
        Run the RPyC memory service. The host and port used are picked from the __init__ configuration.
        By default ThreadingServer is used, however this can be altered by passing different 'server' and
        associated 'server_kwargs'.

        :param server:
        :param server_kwargs:
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

        server(**kwargs).start()

    @classmethod
    def memoize(cls, unique_key, robj=DEFAULT, robj_gen=DEFAULT):
        """
        Memoize the remote object or remote object returned by the generator against the unique_key

        :param unique_key:
        :param robj:
        :param robj_gen:
        :return:
        """
        if not cls._validate_obj_sources(robj, robj_gen):
            raise RpycMemSvcError('Either object or object generator should be passed')

        with cls._memoize_lock:
            if unique_key not in cls._sharedmem:
                if robj is not cls.DEFAULT:
                    cls._sharedmem[unique_key] = robj
                else:
                    cls._sharedmem[unique_key] = robj_gen() # noqa

            return cls._sharedmem[unique_key]

    @classmethod
    def get(cls, unique_key):
        """
        Get the remote object against the unique_key. Raise an exception if the key is not present

        :param unique_key:
        :return:
        """
        with cls._memoize_lock:
            if unique_key not in cls._sharedmem:
                raise RpycMemSvcError('No remote object exists against the key')

            return cls._sharedmem[unique_key]

    @classmethod
    def update(cls, unique_key, robj=DEFAULT, robj_gen=DEFAULT):
        """
        Update the remote object or remote object returned by the generator against the unique_key (create
        one if it doesnt exist)

        :param unique_key:
        :param robj:
        :param robj_gen:
        :return:
        """
        if not cls._validate_obj_sources(robj, robj_gen):
            raise RpycMemSvcError('Either object or object generator should be passed')

        with cls._memoize_lock:
            if robj is not cls.DEFAULT:
                cls._sharedmem[unique_key] = robj
            else:
                cls._sharedmem[unique_key] = robj_gen() # noqa

            return cls._sharedmem[unique_key]

    @classmethod
    def is_memoized(cls, unique_key):
        """
        Return True if a remote object exists against the unique_key

        :param unique_key:
        :return:
        """
        with cls._memoize_lock:
            return unique_key in cls._sharedmem

    @classmethod
    def remote_import(cls, module, package=None):
        """
        Make remote modules available to the clients, primarily for creating remote objects

        :param module:
        :param package:
        :return:
        """
        return import_module(module, package)

    @classmethod
    def rpyc_version(cls):
        """
        Return RPyC version of the remote
        :return:
        """
        return rpyc.__version__

    @classmethod
    def _validate_obj_sources(cls, robj, robj_gen):
        """
        Validate the object sources

        :param robj:
        :param robj_gen:
        :return:
        """
        if (robj is cls.DEFAULT and robj_gen is cls.DEFAULT) or \
                (robj is not cls.DEFAULT and robj_gen is not cls.DEFAULT):
            return False

        return True
