"""RPyC Memory Session"""

import multiprocessing

from rpyc_mem.client import RemoteModule, RpycMem
from rpyc_mem.connect import RpycMemConnect
from rpyc_mem.errors import RpycMemError


class RpycMemSession:
    """
    ``RpycMemSession`` brings ``RpycMemConnect``, ``RemoteModule`` and ``RpycMem`` under one
    hood while enabling to create/manage remote objects efficiently. ``RpycMemSession`` will
    repurpose the connection object for different operations. A similar raw RPyC connection
    (underlying socket object is similar) when used in different processes may result in race
    conditions (Refer https://github.com/tomerfiliba-org/rpyc/issues/482). ``RpycMemSession``
    can deal with it by keeping track of processes. ``RpycMemSession`` has functionality for
    creating ``RemoteModule`` object (singleton, accessible via ``rmod``) and ``RpycMem`` objects.
    The underlying Rpyc Mem connection can be retrieved through ``rmem_conn`` property.

    :param str hostname: RPyC memory service hostname
    :param int port: RPyC memory service port
    :param int max_retry: Number of times to retry upon connection failure (at session level).
    :param int retry_delay: Retry delay in seconds between each re-connect attempt
    :param bool ignore_version: Do not validate the server RPyC version with the client
    :param bool process_safe: Create a new Rpyc Mem connection when the objects created by the
     session are accessed by the process who is not the actual creator of the session.
    """
    _DEFAULT = object()

    def __init__(self, hostname, port, max_retry=4, retry_delay=3, ignore_version=False,
                 process_safe=True):
        """Initialize RpycMemSession"""
        self.hostname = hostname
        self.port = port
        self.max_retry = max_retry
        self.retry_delay = retry_delay
        self.ignore_version = ignore_version
        self.process_safe = process_safe

        self._rmem_conn = None
        self._process = multiprocessing.current_process().pid

        self.rmod = RemoteModule(self._callable_rmem_conn)

    @property
    def rmem_conn(self):
        """
        Return RpycMemConnection in a process-safe way (if set to True)

        :return rpyc_mem.connect.RpycMemConnect:
        """
        init_conn = False
        # Check for process changes since the session creation
        if self.process_safe:
            curr_proc = multiprocessing.current_process().pid
            if curr_proc != self._process:
                self._process = curr_proc
                init_conn = True

        # Handle first time connection setup
        if not self._rmem_conn:
            init_conn = True

        if init_conn:
            self._rmem_conn = RpycMemConnect(
                hostname=self.hostname, port=self.port, max_retry=self.max_retry,
                retry_delay=self.retry_delay, ignore_version=self.ignore_version
            )

        return self._rmem_conn

    def _callable_rmem_conn(self):
        """Callable wrapper around rmem_conn"""
        return self.rmem_conn

    def rmem(self, unique_key, robj=_DEFAULT, robj_gen=_DEFAULT):
        """
        Create RpycMem object against the unique_key while using robj, robj_gen through
        session's Rpyc memory connection

        :param typing.Hashable unique_key: The unique-key for syncing the remote object with
         Rpyc memory service.
        :param typing.Any robj: The remote object to use for memoization (One among robj,
         robj_gen should be passed).
        :param typing.Callable robj_gen: The remote object generator to use for memoization
         (One among robj, robj_gen should be passed).

        :return:
        """
        if not self._validate_obj_sources(robj, robj_gen):
            raise RpycMemError('Either remote object or remote object generator should be passed')

        if robj is not self._DEFAULT:
            return RpycMem(
                rmem_conn=self._callable_rmem_conn, unique_key=unique_key, robj=robj
            )
        else:
            return RpycMem(
                rmem_conn=self._callable_rmem_conn, unique_key=unique_key, robj_gen=robj_gen
            )

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
