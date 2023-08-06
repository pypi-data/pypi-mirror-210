# This file was automatically generated by SWIG (https://www.swig.org).
# Version 4.1.0
#
# Do not make changes to this file unless you know what you are doing - modify
# the SWIG interface file instead.

from sys import version_info as _swig_python_version_info
# Import the low-level C/C++ module
if __package__ or "." in __name__:
    from . import _openstudiosdd
else:
    import _openstudiosdd

try:
    import builtins as __builtin__
except ImportError:
    import __builtin__

def _swig_repr(self):
    try:
        strthis = "proxy of " + self.this.__repr__()
    except __builtin__.Exception:
        strthis = ""
    return "<%s.%s; %s >" % (self.__class__.__module__, self.__class__.__name__, strthis,)


def _swig_setattr_nondynamic_instance_variable(set):
    def set_instance_attr(self, name, value):
        if name == "this":
            set(self, name, value)
        elif name == "thisown":
            self.this.own(value)
        elif hasattr(self, name) and isinstance(getattr(type(self), name), property):
            set(self, name, value)
        else:
            raise AttributeError("You cannot add instance attributes to %s" % self)
    return set_instance_attr


def _swig_setattr_nondynamic_class_variable(set):
    def set_class_attr(cls, name, value):
        if hasattr(cls, name) and not isinstance(getattr(cls, name), property):
            set(cls, name, value)
        else:
            raise AttributeError("You cannot add class attributes to %s" % cls)
    return set_class_attr


def _swig_add_metaclass(metaclass):
    """Class decorator for adding a metaclass to a SWIG wrapped class - a slimmed down version of six.add_metaclass"""
    def wrapper(cls):
        return metaclass(cls.__name__, cls.__bases__, cls.__dict__.copy())
    return wrapper


class _SwigNonDynamicMeta(type):
    """Meta class to enforce nondynamic attributes (no new attributes) for a class"""
    __setattr__ = _swig_setattr_nondynamic_class_variable(type.__setattr__)


import weakref

class SwigPyIterator(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc="The membership flag")

    def __init__(self, *args, **kwargs):
        raise AttributeError("No constructor defined - class is abstract")
    __repr__ = _swig_repr
    __swig_destroy__ = _openstudiosdd.delete_SwigPyIterator

    def value(self):
        return _openstudiosdd.SwigPyIterator_value(self)

    def incr(self, n=1):
        return _openstudiosdd.SwigPyIterator_incr(self, n)

    def decr(self, n=1):
        return _openstudiosdd.SwigPyIterator_decr(self, n)

    def distance(self, x):
        return _openstudiosdd.SwigPyIterator_distance(self, x)

    def equal(self, x):
        return _openstudiosdd.SwigPyIterator_equal(self, x)

    def copy(self):
        return _openstudiosdd.SwigPyIterator_copy(self)

    def next(self):
        return _openstudiosdd.SwigPyIterator_next(self)

    def __next__(self):
        return _openstudiosdd.SwigPyIterator___next__(self)

    def previous(self):
        return _openstudiosdd.SwigPyIterator_previous(self)

    def advance(self, n):
        return _openstudiosdd.SwigPyIterator_advance(self, n)

    def __eq__(self, x):
        return _openstudiosdd.SwigPyIterator___eq__(self, x)

    def __ne__(self, x):
        return _openstudiosdd.SwigPyIterator___ne__(self, x)

    def __iadd__(self, n):
        return _openstudiosdd.SwigPyIterator___iadd__(self, n)

    def __isub__(self, n):
        return _openstudiosdd.SwigPyIterator___isub__(self, n)

    def __add__(self, n):
        return _openstudiosdd.SwigPyIterator___add__(self, n)

    def __sub__(self, *args):
        return _openstudiosdd.SwigPyIterator___sub__(self, *args)
    def __iter__(self):
        return self

# Register SwigPyIterator in _openstudiosdd:
_openstudiosdd.SwigPyIterator_swigregister(SwigPyIterator)
SHARED_PTR_DISOWN = _openstudiosdd.SHARED_PTR_DISOWN
from .import openstudioutilities
from .import openstudioutilitiescore
from .import openstudioutilitiestime
from .import openstudioutilitiesdata
from .import openstudioutilitiesunits
from .import openstudioutilitiesplot
from .import openstudioutilitiesgeometry
from .import openstudioutilitiessql
from .import openstudioutilitiesbcl
from .import openstudioutilitiesidd
from .import openstudioutilitiesidf
from .import openstudioutilitiesfiletypes
from .import openstudioutilitiesxml
from .import openstudiomodel
from .import openstudiomodelcore
from .import openstudiomodelsimulation
from .import openstudiomodelresources
from .import openstudiomodelgeometry
from .import openstudiomodelhvac
from .import openstudiomodelzonehvac
from .import openstudiomodelavailabilitymanager
from .import openstudiomodelplantequipmentoperationscheme
from .import openstudiomodelstraightcomponent
from .import openstudiomodelairflow
from .import openstudiomodelrefrigeration
from .import openstudiomodelgenerators
class SddReverseTranslator(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc="The membership flag")
    __repr__ = _swig_repr

    def __init__(self, masterAutosize=False):
        _openstudiosdd.SddReverseTranslator_swiginit(self, _openstudiosdd.new_SddReverseTranslator(masterAutosize))
    __swig_destroy__ = _openstudiosdd.delete_SddReverseTranslator

    def loadModel(self, path, progressBar=None):
        return _openstudiosdd.SddReverseTranslator_loadModel(self, path, progressBar)

    def warnings(self):
        return _openstudiosdd.SddReverseTranslator_warnings(self)

    def errors(self):
        return _openstudiosdd.SddReverseTranslator_errors(self)

# Register SddReverseTranslator in _openstudiosdd:
_openstudiosdd.SddReverseTranslator_swigregister(SddReverseTranslator)
class SddForwardTranslator(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc="The membership flag")
    __repr__ = _swig_repr

    def __init__(self):
        _openstudiosdd.SddForwardTranslator_swiginit(self, _openstudiosdd.new_SddForwardTranslator())
    __swig_destroy__ = _openstudiosdd.delete_SddForwardTranslator

    def modelToSDD(self, model, path, progressBar=None):
        return _openstudiosdd.SddForwardTranslator_modelToSDD(self, model, path, progressBar)

    def warnings(self):
        return _openstudiosdd.SddForwardTranslator_warnings(self)

    def errors(self):
        return _openstudiosdd.SddForwardTranslator_errors(self)

# Register SddForwardTranslator in _openstudiosdd:
_openstudiosdd.SddForwardTranslator_swigregister(SddForwardTranslator)

