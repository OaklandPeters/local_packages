"""
Provides a metaclass which allows creation of functional-style 'Operators' -
classes which behave as functions.

Have no state.
    Calls to the class go directly to __call__, rather than __new__ or __init__
All methods defined at class creation are automatically converted to classmethods


"""

#import abc
import types

class OperatorMeta(type):
    """
    Inheriting from this creates a class which is callable (__call__),
    but whose __init__ or __new__ are NOT called by 'cls(arguments)' calls.
    
    It also does:
    () Checks for abstract methods during class inheritance (not instantiation).
        ... to temporarily override this behavior, simply 
            redeclare the attribute as abstract.
    () Coerces all function/lambda attributes into classmethods automatically.
    
    Note: this has __abstractmethods__ to imitate abc.ABCMeta, but it does
    not actually inherit from it.
    
    @todo: Advanced - make these register as functions
    
    
    Future ideas for support for:
    __validate__
    __dispatch__
    __signature__
    __meets__    (compares signatures)
    """

    __abstractmethods__ = frozenset(['__call__'])
    def __new__(mcls, cls_name, bases, namespace): #pylint: disable=C0202
        """This is used to check for abstract methods.
        OperatorMeta.__call__ is injected as an abstractmethod.
        """        
        
        # Handling abstracts        
        _check_abstracts(cls_name, bases+(mcls,), namespace)

        # Convert all methods to classmethods
        namespace = _force_classmethods(namespace)
        
        # Make class
        return super(OperatorMeta, mcls).__new__(mcls, cls_name, bases, namespace)
        
    
    def __call__(cls, *args, **kwargs):
        """
        This IS triggered for:      MyClass('foo')
        But NOT for:                MyClass.__call__('foo')
        """
        return cls.__call__(*args, **kwargs)

#==============================================================================
#    Local Utility functions
#==============================================================================
def _find_abstracts_and_bases(bases):
    return [
        (name, base.__name__)
        for base in bases
        for name in getattr(base, "__abstractmethods__", set())
    ]

def _check_abstracts(cls_name, bases, namespace):
    for name, base in _find_abstracts_and_bases(bases):
        if name not in namespace:
            raise TypeError(
                "{0} is missing abstract method: {1} from {2}".format(
                cls_name, name, base
            ))

def _unroll(converter=iter):
    def outer(func):
        def inner(*args, **kwargs):
            return converter(func(*args, **kwargs))
        return inner
    return outer    

@_unroll(dict)
def _force_classmethods(namespace):
    for name, attr in namespace.items():
        #If function/lambda, but not if callable class
        if isinstance(attr, (types.FunctionType, types.LambdaType)):
            yield (name, classmethod(attr))
        else:
            yield (name, attr)
