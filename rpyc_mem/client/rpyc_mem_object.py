"""RPyC Memory Object"""

import rpyc

from rpyc_mem.errors import RpycMemError, RpycMemSvcError
from rpyc_mem.utils.object_proxy import proxify

rpyc.core.vinegar._generic_exceptions_cache['rpyc_mem.errors.RpycMemSvcError'] = RpycMemSvcError  # noqa


@proxify(real_attr='_real_obj', local_attrs=[
    '_real_obj', '_DEFAULT', '_rmem_conn', '_unique_key', '_robj', '_robj_gen',
    'rmem_memoize', 'rmem_get', 'rmem_update', 'rmem_delete', '_validate_obj_sources'
])
class RpycMem:
    """
    Proxy class for python objects residing on RPyC memory service hosts

    :param rpyc_mem.connect.RpycMemConnect rmem_conn: Rpyc memory connection on which the remote
     object should be synced
    :param unique_key: The unique-key for syncing the remote object with Rpyc memory service
    :param typing.Any robj: The remote object to use for memoization (One among robj, robj_gen
     should be passed).
    :param typing.Callable robj_gen: The remote object generator to use for memoization (One among robj,
     robj_gen should be passed).

     .. autoproperty:: _real_obj
    """
    _DEFAULT = object()

    def __init__(self, rmem_conn, unique_key, robj=_DEFAULT, robj_gen=_DEFAULT):
        """Initialize Rpyc(shared) memory object"""
        self._rmem_conn = rmem_conn
        self._unique_key = unique_key
        self._robj = robj
        self._robj_gen = robj_gen

        # Memoize remote object
        self.rmem_memoize(robj, robj_gen)   # noqa

    @property
    def _real_obj(self):
        """
        The remote object property.

        :return:
        """
        try:
            return self._rmem_conn.get(self._unique_key)
        except RpycMemSvcError:
            raise RpycMemError('Can not recover remote object from RPyC memory service')

    def rmem_memoize(self, robj=_DEFAULT, robj_gen=_DEFAULT):
        """
        Memoize the remote object against the unique_key

        :param typing.Any robj: The remote object to use for memoization (One among robj, robj_gen should be
         passed).
        :param typing.Callable robj_gen: The remote object generator to use for memoization (One among robj,
         robj_gen should be passed).
        :return:
        """
        if not self._validate_obj_sources(robj, robj_gen):
            raise RpycMemError('Either remote object or remote object generator should be passed')

        if robj is not self._DEFAULT:
            return self._rmem_conn.memoize(self._unique_key, robj=robj)
        else:
            return self._rmem_conn.memoize(self._unique_key, robj_gen=robj_gen)

    def rmem_get(self):
        """
        Get the remote object against the unique-key

        :return:
        """
        return self._rmem_conn.get(self._unique_key)

    def rmem_update(self, robj=_DEFAULT, robj_gen=_DEFAULT):
        """
        Update remote object on RPyC memory service hosts

        :param typing.Any robj: The remote object to use for update (One among robj, robj_gen should be
         passed).
        :param typing.Callable robj_gen: The remote object generator to use for update (One among robj,
         robj_gen should be passed).
        :return:
        """
        if not self._validate_obj_sources(robj, robj_gen):
            raise RpycMemError('Either remote object or remote object generator should be passed')

        if robj is not self._DEFAULT:
            return self._rmem_conn.update(self._unique_key, robj=robj)
        else:
            return self._rmem_conn.update(self._unique_key, robj_gen=robj_gen)

    def rmem_delete(self):
        """
        Delete the mapping in RPyC memory service

        :return:
        """
        self._rmem_conn.delete(self._unique_key)

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
