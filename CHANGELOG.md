# ChangeLog

### 1.0.1
- Handle __bool__ in proxy objects
- Other fixes

### 1.0.0

Breaking Changes:
  - The remote object creation through ``RemoteModule`` has seen some changes.
  - The visibility of few attributes are changed from protected to public.

Add Ons:
  - ``RpycMem`` and ``RemoteModule`` will accept callables for ``rmem_conn`` parameter
  - Sessions are introduced through ``RpycMemSession`` class.

### 0.0.1
- Initial Release
