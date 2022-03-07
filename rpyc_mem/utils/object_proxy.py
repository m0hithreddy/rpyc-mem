"""
Object Proxying Utils

Initial Credits: Inspired by Tomer Filiba's Python recipe:
(https://code.activestate.com/recipes/496741-object-proxying/)
"""


# Python special methods (Few methods which need special handling are excluded)
special_methods = {
    '__abs__', '__add__', '__and__', '__call__', '__cmp__', '__coerce__', '__contains__',
    '__delitem__', '__delslice__', '__div__', '__divmod__', '__enter__', '__eq__', '__exit__',
    '__float__', '__floordiv__', '__ge__', '__getitem__', '__getslice__', '__gt__', '__hex__',
    '__iadd__', '__iand__', '__idiv__', '__idivmod__', '__ifloordiv__', '__ilshift__', '__imod__',
    '__imul__', '__int__', '__invert__', '__ior__', '__ipow__', '__irshift__', '__isub__', '__iter__',
    '__itruediv__', '__ixor__', '__le__', '__len__', '__long__', '__lshift__', '__lt__', '__mod__',
    '__mul__', '__ne__', '__neg__', '__oct__', '__or__', '__pos__', '__pow__', '__radd__', '__rand__',
    '__rdiv__', '__rdivmod__', '__reduce__', '__reduce_ex__', '__repr__', '__reversed__', '__rfloordiv__',
    '__rlshift__', '__rmod__', '__rmul__', '__ror__', '__rpow__', '__rrshift__', '__rshift__', '__rsub__',
    '__rtruediv__', '__rxor__', '__setitem__', '__setslice__', '__sub__', '__truediv__', '__xor__', 'next',
}


def proxify(real_attr, local_attrs=()):
    """
    Class decorator for making a class a proxy class

    :param real_attr: The attribute which is holding the real object that is being proxied
    :param local_attrs: The attributes which should be treated as local attributes for the class
    :return:
    """
    if real_attr not in local_attrs:
        local_attrs = (real_attr,) + tuple(local_attrs)

    def cls_decorator(cls):
        """The actual class decorator """
        def real_obj(self):
            return object.__getattribute__(self, real_attr)

        # Handle __getattribute__
        orig_getattribute = cls.__getattribute__

        def _getattribute(self, name):
            if name in local_attrs:
                return orig_getattribute(self, name)

            return getattr(real_obj(self), name)

        cls.__getattribute__ = _getattribute

        # Handle __delattr__
        orig_delattr = cls.__delattr__

        def _delattr(self, name):
            if name in local_attrs:
                orig_delattr(self, name)
            else:
                delattr(real_obj(self), name)

        cls.__delattr__ = _delattr

        # Handle __setattr__
        orig_setattr = cls.__setattr__

        def _setattr(self, name, value):
            if name in local_attrs:
                orig_setattr(self, name, value)
            else:
                setattr(real_obj(self), name, value)

        cls.__setattr__ = _setattr

        # Handle __str__
        def _str(self):
            return str(real_obj(self))

        cls.__str__ = _str

        # Handle __repr__
        def _repr(self):
            return repr(real_obj(self))

        cls.__repr__ = _repr

        # Handle __hash__
        def _hash(self):
            return hash(real_obj(self))

        cls.__hash__ = _hash

        # Handle remaining special methods
        def make_special_method(name):
            def special_method(self, *args, **kwargs):
                return getattr(real_obj(self), name)(*args, **kwargs)

            return special_method

        for method in special_methods:
            setattr(cls, method, make_special_method(method))

        return cls

    return cls_decorator
