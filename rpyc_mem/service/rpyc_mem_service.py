"""RPyC Memory Service"""

import threading
from importlib import import_module

import rpyc

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
