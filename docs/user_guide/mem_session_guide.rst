RPyC Memory Session
-------------------

Juggling around the ``RpycMemConnect`` object across ``RemoteModule`` and ``RpycMem`` can be redundant. ``RpycMemSession``
brings all of them under one hood and re-purposes the connection object for different operations. ``RpycMemSession`` also
solves the problem of two processes using a similar ``RPyC`` connection object; this is documented at detail in this `issue
<https://github.com/tomerfiliba-org/rpyc/issues/482>`_. In breif, when a process forks a child, child gets the memory snapshot
of the parent, which includes the underlying socket object of rpyc connection. When both parent and child try to send data to
the server from same socket address, it corrupts the request message structure as defined by the rpyc protocol. To solve this,
``RpycMemSession`` passes callable for ``rmem_conn`` parameter of ``RemoteModule`` and ``RpycMem``. This callable acts as
generator of ``rmem_conn`` object. Every time a connection object is needed the callable is invoked. Now ``RpycMemSession``
keeps track of the processes and whenever a process change is detected a fresh ``rmem_conn`` object is returned. Consider the
same example as laid out in ``RPyC Memory`` guide but using ``RpycMemSession``::

    import multiprocessing
    from multiprocessing import Process

    from rpyc_mem.session import RpycMemSession

    """
    Assuming service is running on localhost:18813

    Defaults:
    max_retry=4 # Retry is at session level. In specific at session level for each connection object.
    retry_delay=3
    ignore_version=False
    process_safe=True # Make session to return new connection object upon process change.
    """
    rses = RpycMemSession('localhost', 18813)


    class Shared:
        lock = rses.rmem('lock-key', robj_gen=lambda: rses.rmod('threading').Lock())
        obj = rses.rmem('obj-key', robj_gen=lambda: rses.rmod().list([1, 2]))

        def __init__(self, title):
            self.title = title

        def describe(self):
            with self.lock:
                print('%s: %s' % (self.title, self.obj))

        @classmethod
        def run(cls):
            with cls.lock:
                if isinstance(cls.obj, list):
                    print(cls.obj)
                    cls.obj.rmem_update(rses.rmod().tuple([1, 2]))
                else:
                    print('Oops')


    if __name__ == '__main__':
        # multiprocessing.set_start_method('spawn')

        proc1 = Process(target=Shared.run)
        proc2 = Process(target=Shared.run)
        proc3 = Process(target=Shared('Cool-Class').describe)

        proc1.start()
        proc2.start()
        proc3.start()

        proc1.join()
        proc2.join()
        proc3.join()

    """
    Output (varied):
    Cool-Class: [1, 2]
    [1, 2]
    Oops
    """


Note the ``set_start_method`` being commented out (makes difference only on Unix based systems). ``RemoteModule`` of the session
can be accessed through ``rmod``; It is a singleton object.
