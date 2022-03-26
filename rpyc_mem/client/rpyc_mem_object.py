"""RPyC Memory Object"""

import rpyc

from rpyc_mem.errors import RpycMemError, RpycMemSvcError
from rpyc_mem.utils.object_proxy import proxify

rpyc.core.vinegar._generic_exceptions_cache['rpyc_mem.errors.RpycMemSvcError'] = RpycMemSvcError  # noqa


@proxify(real_attr='real_obj', local_attrs=[
    'real_obj', '_DEFAULT', '_rmem_conn', 'rmem_conn', 'unique_key', 'robj', 'robj_gen',
    'rmem_memoize', 'rmem_get', 'rmem_update', 'rmem_delete', '_validate_obj_sources'
])
class RpycMem:
    """
    Proxy class for python objects residing on RPyC memory service hosts

    :param Union[rpyc_mem.connect.RpycMemConnect, typing.Callable] rmem_conn: Rpyc memory
     connection or a callable that returns Rpyc memory connection on which the remote object
     should be synced
    :param typing.Hashable unique_key: The unique-key for syncing the remote object with
     Rpyc memory service
    :param typing.Any robj: The remote object to use for memoization (One among robj,
     robj_gen should be passed).
    :param typing.Callable robj_gen: The remote object generator to use for memoization
     (One among robj, robj_gen should be passed).
    """
    _DEFAULT = object()

    def __init__(self, rmem_conn, unique_key, robj=_DEFAULT, robj_gen=_DEFAULT):
        """Initialize Rpyc(shared) memory object"""
        self._rmem_conn = rmem_conn
        self.unique_key = unique_key
        self.robj = robj
        self.robj_gen = robj_gen    # noqa

        # Memoize remote object
        self.rmem_memoize(robj, robj_gen)   # noqa

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

    @property
    def real_obj(self):
        """
        Property wrapper around rmem_get()

        :return:
        """
        try:
            return self.rmem_get()
        except RpycMemSvcError:
            raise RpycMemError('Can not recover remote object from RPyC memory service')

    def rmem_memoize(self, robj=_DEFAULT, robj_gen=_DEFAULT):
        """
        Memoize the remote object against the unique_key

        :param typing.Any robj: The remote object to use for memoization (One among robj,
         robj_gen should be passed).
        :param typing.Callable robj_gen: The remote object generator to use for memoization
         (One among robj, robj_gen should be passed).

        :return:
        """
        if not self._validate_obj_sources(robj, robj_gen):
            raise RpycMemError('Either remote object or remote object generator should be passed')

        if robj is not self._DEFAULT:
            return self.rmem_conn.memoize(self.unique_key, robj=robj)
        else:
            return self.rmem_conn.memoize(self.unique_key, robj_gen=robj_gen)

    def rmem_get(self):
        """
        Get the live remote object against the unique-key.

        :return:
        """
        return self.rmem_conn.get(self.unique_key)

    def rmem_update(self, robj=_DEFAULT, robj_gen=_DEFAULT):
        """
        Update remote object on RPyC memory service hosts

        :param typing.Any robj: The remote object to use for update (One among robj, robj_gen
         should be passed).
        :param typing.Callable robj_gen: The remote object generator to use for update (One
         among robj, robj_gen should be passed).

        :return:
        """
        if not self._validate_obj_sources(robj, robj_gen):
            raise RpycMemError('Either remote object or remote object generator should be passed')

        if robj is not self._DEFAULT:
            return self.rmem_conn.update(self.unique_key, robj=robj)
        else:
            return self.rmem_conn.update(self.unique_key, robj_gen=robj_gen)

    def rmem_delete(self):
        """
        Delete the mapping in RPyC memory service

        :return:
        """
        self.rmem_conn.delete(self.unique_key)

    @classmethod
    def _validate_obj_sources(cls, robj, robj_gen):
        """
        Validate object sources. Return False if both robj, robj_gen are set/not-set else True

        :param typing.Any robj: Remote object
        :param typing.Callable robj_gen: Remote object generator

        :return:
        """
        if (robj is cls._DEFAULT and robj_gen is cls._DEFAULT) or \
                (robj is not cls._DEFAULT and robj_gen is not cls._DEFAULT):
            return False

        return True
