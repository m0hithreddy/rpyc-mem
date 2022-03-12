# RPyC Mem
**(RPyC) (Mem)ory**

## Overview

- RPyC-Mem is a light weight shared memory alternative for Python implemented using [``RPyC``](https://github.com/tomerfiliba-org/rpyc)
- RPyC-Mem has a ready to run service, which hosts network based shared memory to be consumed by different processes.
- RPyC-Mem has proxy classes to interact with the shared memory objects effectively.

## Getting Started

1. Install RPyC-Mem from [``pypi``](https://pypi.org/project/rpyc-mem)

    ```shell
    pip install rpyc-mem
    ```

2. Run the RPyC-Mem server

   ```python
   from rpyc_mem.service import RpycMemService
   
   rs = RpycMemService('localhost', 18813)
   rs.run()
   ```

3. Share data between processes
   
   *Client 1:*
   
   ```python
   from rpyc_mem.connect import RpycMemConnect
   from rpyc_mem.client import RemoteModule, RpycMem
   
   rc = RpycMemConnect('localhost', 18813)
   ro = RemoteModule(rc)
   rm = RpycMem(rc, 'unique-key', robj_gen=lambda: ro.list([1, 2]))
   
   print(rm)    # [1, 2]
   ```
   *Client 2:*
   
   ```python
   from rpyc_mem.connect import RpycMemConnect
   from rpyc_mem.client import RemoteModule, RpycMem
   
   rc = RpycMemConnect('localhost', 18813)
   ro = RemoteModule(rc)
   rm = RpycMem(rc, 'unique-key', robj_gen=lambda: ro.list([1, 2, 3]))
   
   print(rm)    # [1, 2]
   rm.append(3)
   ```
   
   *Client 1 continued... :*
   
   ```python
   print(rm)    # [1, 2, 3]
   ```

4. For more details, check out the [API-Reference, User-Guide](http://rpyc-mem.readthedocs.io/)
