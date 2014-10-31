"""
Provides a metaclass which allows creation of functional-style 'Operators' -
classes which behave as functions.

Have no state.
    Calls to the class go directly to __call__, rather than __new__ or __init__
All methods defined at class creation are automatically converted to classmethods


@todo: OperatorMeta is not adding/setting abstractmethods properly
    ? Is this handled by the abc.abstractmethod() decorator?

@todo: Fix bug with abstracts and inheritance:
Bug: Description
grandparent-class declares abstracts, parent class implements some of them, then the child class i
mplements the remaining - then the ones implemented by the parent are still seen as 'abstract' -- leading to chi
ld class throwing an error during construction via Operator_Meta's __new__.

Algorithm for detecting unfilled abstracts:
-------------------------------------------
(1) Take count of all abstracts
    abstracts = _find_abstracts(namespace, bases)
(2) Create new class:
    cls = super(ABFMeta, mcls).__new__(mcls, cls_name, bases, namespace)
(3) To be an acceptable inheritance, each abstract must be one of:
        for name in abstracts:
    (I) In the new namespace  (note: namespace ~ cls.__dict__
            abstract_name in namespace
    (II) Not an abstract when called from cls:
            hasattr(getattr(cls, name), '__isabstractmethod__')

def unfilled_abstracts(abstracts, cls):
    for name in abstracts:
        if name in cls.__dict__:
            pass
        elif isabstractmethod(getattr(cls, name)):
            pass
        else:
            yield name

def isabstractmethod(method):
    return hasattr(method, '__isabstractmethod__')


Algorithm to inherit unfilled abstracts 
-----------------------------------------

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
    
    @todo: This neds to set abstratmethods
    
    @todo: Advanced - make these register as functions
    
    
    Future ideas for support for:
    __validate__
    __dispatch__
    __signature__
    __meets__    (compares signatures)
    """

    __abstractmethods__ = frozenset(['__call__'])
#     def __new__(mcls, cls_name, bases, namespace): #pylint: disable=C0202
#         """This is used to check for abstract methods.
#         OperatorMeta.__call__ is injected as an abstractmethod.
#         """        
#         # Handling abstracts        
#         _check_abstracts(cls_name, bases+(mcls,), namespace)
# 
#         # Convert all methods to classmethods
#         namespace = _force_classmethods(namespace)
#         
#         # Make class
#         cls = super(OperatorMeta, mcls).__new__(mcls, cls_name, bases, namespace)
#         return cls

    def __new__(mcls, cls_name, bases, namespace): #pylint: disable=C0202
        """This is used to check for abstract methods.
        OperatorMeta.__call__ is injected as an abstractmethod.
        """
        
        # Convert all methods to classmethods
        #namespace = _force_classmethods(namespace)
        
        # Construct class
        cls = super(OperatorMeta, mcls).__new__(mcls, cls_name, bases, namespace)
        
        # Record abstract methods
        cls.__abstractmethods__ = frozenset(all_abstracts(cls))
        
        # Check for unassigned-to abstract methods
        unassigned = unassigned_abstracts(cls)
        if unassigned: #If there are any unassigned abstract methods
            raise TypeError(str.format(
                ("Can't construct abstract function class {0} "
                "with abstract methods: {1}"),
                cls_name, ", ".join(unassigned)
            ))
        
        return cls
        
        
        # Make class
        cls = super(OperatorMeta, mcls).__new__(mcls, cls_name, bases, namespace)
        return cls

    
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
    """Does this have a problem with converting abstractmethods?"""
    for name, attr in namespace.items():
        #If function/lambda, but not if callable class
        if isinstance(attr, (types.FunctionType, types.LambdaType)):
            yield (name, classmethod(attr))
        else:
            yield (name, attr)



#--------------- New
def _namespace_abstracts(namespace):
    return set(name
        for name, value in namespace.items()
        if getattr(value, "__isabstractmethods__", False)
    )
def _bases_abstracts(namespace, bases):
    for base in bases:
        for name in getattr(base, "__abstractmethods__", set()):
            value = getattr(cls, name, None)
            if getattr(value, "__isabstractmethod__", False):
                abstracts.add(name)
    return abstracts

@_unroll(set)
def _find_abstracts(namespace, bases):
    # From namespace
    for name, value in namespace.items():
        if getattr(value, "__isabstractmethods__", False):
            yield name
    # From bases
    for base in bases:
        for name in getattr(base, "__abstractmethods__", set()):
            value = getattr(cls, name, None)
            if getattr(value, "__isabstractmethod__", False):
                yield name


def _find_abstracts_from_abc(namespace, bases, cls):
    """Taken from abc.py's ABCMeta.__new__
    My issue, is I need to draw this distinction:
    (1) All abstracts present in the current class
    (2) All abstracts NOT redefined in the current namespace
    ... since, unlike for classes inheriting from abcmeta
    ... OperatorMeta checks abstracts after every inheritance (not initialization)
    ... and so needs to allow you to restate methods as abstract, in order
        to 'pass-them-on' as abstracts
    
    """
    # From namespace
    abstracts = set(name
        for name, value in namespace.items()
        if getattr(value, "__isabstractmethod__", False)
    )
    # From bases - requires cls
    for base in bases:
        for name in getattr(base, "__abstractmethods__", set()):
            value = getattr(cls, name, None)
            if getattr(value, "__isabstractmethod__", False):
                abstracts.add(name)
    return abstracts
    # Now assign cls.__abstractmethods__ = frozenset(abstacts)

@_unroll(set)
def all_abstracts(cls):
    for name in dir(cls):
        if hasattr(getattr(cls, name),'__isabstractmethod__'):
            yield name

@_unroll(set)
def unassigned_abstracts(cls):
    for name in all_abstracts(cls):
        if name not in cls.__dict__:
            yield name