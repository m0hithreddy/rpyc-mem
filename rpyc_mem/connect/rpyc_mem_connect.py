"""RPyC Memory Connect"""

import time

import rpyc

from rpyc_mem.errors import RpycMemConnError


class RpycMemConnect:
    """
    Wrapper around rpyc.connect to connect with 'RpycMemService'. RpycMemConnect does some basic
    error recovery and validations on behalf of the user.
    """

    _ROOT_ATTRS = [
        'memoize', 'get', 'update', 'is_memoized', 'remote_import', 'rpyc_version'
    ]
    _RMEM_CONN_ERROR = RpycMemConnError('Unable to connect to RPyC memory service')

    def __init__(self, hostname, port, max_retry=4, retry_delay=3, ignore_version=False):
        """
        Initialize RpycMemConnect object

        :param hostname: RPyC memory service hostname
        :param port: RPyC memory service port
        :param max_retry: Number of times to retry upon connection failure.
        :param retry_delay: Retry delay between each re-connect attempt
        :param ignore_version: Do not validate the server RPyC version with the client
        """
        self._hostname = hostname
        self._port = port
        self._max_retry = max_retry
        self._retry_delay = retry_delay
        self._ignore_version = ignore_version

        # Setup connection with RPyC memory service
        self._rmem_conn = None
        self._retry = 0
        self._is_closed = False

        self._setup_rmem_conn()

        # Verify client version with the server version
        if not ignore_version:
            srv_rpyc_ver = self.rpyc_version()
            if srv_rpyc_ver != rpyc.__version__:
                raise RpycMemConnError(
                    'Server RPyC version [%s] mismatches with the client version [%s]' %
                    (srv_rpyc_ver, rpyc.__version__)
                )

    def close(self):
        """Close underlying RPyC connection"""
        try:
            self._rmem_conn.close()
        except EOFError:
            pass

        self._is_closed = True

    def rmem_except_handler(self, rmem_fn=None, on_reconnect=None):
        """
        Function decorator for handling rpyc memory service related exceptions. Can be invoked as follows:
        | 1. @rmem_except_handler -> sets on_reconnect to None
        | 2. @rmem_except_handler(on_reconnect=reconnect_hook) -> sets on_reconnect to reconnect_hook
        | 3. @rmem_except_handler() -> Same as @rmem_except_handler
        | 4. @rmem_except_handler(func) -> Ambiguous case, breaks the code.

        :param rmem_fn: Function to be wrapped
        :param on_reconnect: Reconnect hook to be called when connection is re-established
        :return:
        """
        def fn_decorator(fn):
            def wrapped_fn(*args, **kwargs):
                # If connection is closed by calling close() dont handle any exceptions
                if self._is_closed:
                    return fn(*args, **kwargs)

                # Initiate rpyc memory connection setup if _rmem_conn is empty
                just_now = False
                if not self._rmem_conn:
                    self._setup_rmem_conn()
                    just_now = True

                try:
                    return fn(*args, **kwargs)
                except EOFError:
                    if just_now:
                        raise self._RMEM_CONN_ERROR

                    # Retry for once after setting up connection freshly
                    self._setup_rmem_conn()

                    if on_reconnect:
                        # Call on_reconnect hook for special handling
                        on_reconnect()

                    try:
                        return fn(*args, **kwargs)
                    except EOFError:
                        raise self._RMEM_CONN_ERROR

            return wrapped_fn

        if rmem_fn:
            return fn_decorator(rmem_fn)
        else:
            return fn_decorator

    def _setup_rmem_conn(self):
        """Setup RPyC memory connection"""

        # Try closing stagnant connection
        try:
            self._rmem_conn.close()
        except:  # noqa
            pass

        try:
            self._rmem_conn = rpyc.connect(self._hostname, self._port)
            self._is_closed = False
            self._retry = 0
        except:  # noqa
            # Reset retry if exceeded max_retry (For this attempt of connection setup)
            if self._retry > self._max_retry:
                self._retry = 0

            self._retry = self._retry + 1
            if self._retry > self._max_retry:
                raise self._RMEM_CONN_ERROR

            # Retry connection setup after sleep
            time.sleep(self._retry_delay)
            self._setup_rmem_conn()

    def __getattr__(self, name):
        """Expose attributes of _rmem_conn"""
        @self.rmem_except_handler
        def fn():
            if name in self._ROOT_ATTRS:
                return getattr(self._rmem_conn.root, name)

            return getattr(self._rmem_conn, name)

        return fn()
