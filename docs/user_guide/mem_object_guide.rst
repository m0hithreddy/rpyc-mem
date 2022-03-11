RPyC Memory
------------

By default all the objects created through ``RemoteModule`` are unnamed. Once the reference is lost the object can not
be accessed anymore. In a distributed setup we need a definitive way to access or share the object across the processes.
For this we map the remote object against an unique-key. ``RpycMem`` exactly does that, it wraps around the remote object
acting as a proxy while creating or fetching the existing remote object against the mapping. ``RpycMem`` needs an
``RpycMemConnect`` object for performing the sync.  The same connection object can be re-purposed for both ``RemoteModule``
and ``RpycMem`` instead of creating a new connection. ::

    from multiprocessing import Process

    from rpyc_mem.connect import RpycMemConnect
    from rpyc_mem.client import RemoteModule, RpycMem


    def target_proc(unique_key):
        print('Child Process:')

        rc = RpycMemConnect('localhost', 18813)
        ro = RemoteModule(rc)

        # Generators allow delayed execution (dont create if mapping already exists)
        rm = RpycMem(rc, unique_key, robj_gen=lambda: ro.list([1, 2, 3]))
        print(rm)
        rm.append(3)

        print('---------')


    print('Parent Process:')

    # Assuming service is running on localhost:18813
    rc = RpycMemConnect('localhost', 18813)
    ro = RemoteModule(rc)

    rm = RpycMem(rc, 'unique-key', ro.list([1, 2])) # Either pass robj or robj_gen

    print(rm)
    print(len(rm))  # Python special method lookup

    proc = Process(target=target_proc, args=('unique-key',))
    proc.start()
    proc.join()

    print(rm)

    print('---------')

    """
    Output:
    Parent Process:
    [1, 2]
    2
    Child Process:
    [1, 2]
    ---------
    [1, 2, 3]
    ---------
    """


Till now we are able to create the objects of ``builtins/modules`` that remote has to offer. But often times we
need to share the objects of custom classes. ``RemoteModule`` has no direct way to create such objects since the remote
is not aware of your class declarations. The way around is to share the attributes (class attributes, in most cases) of
the class instead of the entire class. In the following code, the attributes ``lock`` and ``obj`` of ``Shared`` class
are shared instead of the entire class ::

    import multiprocessing
    from multiprocessing import Process

    from rpyc_mem.connect import RpycMemConnect
    from rpyc_mem.client import RemoteModule, RpycMem

    # Assuming service is running on localhost:18813
    rc = RpycMemConnect('localhost', 18813)
    ro = RemoteModule(rc)


    class Shared:
        lock = RpycMem(rc, 'lock-key', robj_gen=lambda: ro.threading.Lock())
        obj = RpycMem(rc, 'obj-key', robj_gen=lambda: ro.list([1, 2]))

        def __init__(self, title):
            self.title = title

        def describe(self):
            with self.lock:
                print("%s: %s" % (self.title, self.obj))

        @classmethod
        def run(cls):
            with cls.lock:
                if isinstance(cls.obj, list):
                    print(cls.obj)
                    cls.obj.rmem_update(ro.tuple([1, 2]))
                else:
                    print('Oops')


    if __name__ == '__main__':
        multiprocessing.set_start_method('spawn')  # Refer https://github.com/tomerfiliba-org/rpyc/issues/482

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
    [1, 2]
    Cool-Class: (1, 2)
    Oops
    """


