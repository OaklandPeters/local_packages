

# Declarations and Utility Functions
import abc
import collections

def _hasattr(C, attr):
    try:
        return any(attr in B.__dict__ for B in C.__mro__)
    except AttributeError:
        # Old-style class
        return hasattr(C, attr)
def _hasall(C, attrs):
    return all(
        _hasattr(C, name) for name in attrs
    )
def _nonfunc(*args, **kwargs):
    return NotImplemented
def _abstractmethod(func=_nonfunc):
    return abc.abstractmethod(func)
def ensure_tuple(obj):
    """Ensure that object is a tuple, or is wrapped in one. 
    Also handles some special cases.
    Tuples are unchanged; NonStringSequences and Iterators are converted into
    a tuple containing the same elements; all others are wrapped by a tuple.
    """
    #Tuples - unchanged
    if isinstance(obj, tuple):
        return obj
    #Sequences - convert to tuple containing same elements.
    #elif isinstance(obj, NonStringSequence):
    elif isinstance(obj, collections.Sequence) and not isinstance(obj, basestring):
        return tuple(obj)
    #Iterators & Generators - consume into a tuple
    elif isinstance(obj, collections.Iterator):
        return tuple(obj)
    #Other Iterables, Strings, and non-Iterables - wrap in iterable first
    else:
        return tuple([obj])
    

# Core class

class VOG(object):
    pass

def ducktype(abstracts):
    pass





# class DuckMeta(abc.ABCMeta):
#     """Metaclasses inherit from type.
#     This version descended from ABCMeta"""
#     def __new__(mcls, cls_name, bases, namespace): #pylint: disable=C0202
#         
#         # Create function stubs
#         # ... is this unnecessary ???
#         for name in namespace.get('__abstractmethods__', frozenset([])):
#             namespace[name] = abc.abstractmethod(lambda *a,**kw: NotImplemented)
#         
#         cls = super(DuckMeta, mcls).__new__(mcls, cls_name, bases, namespace)
#         return cls



class DuckMeta(type):
    """Metaclasses inherit from type.
    This version NOT descended from ABCMeta."""
    #__metaclass__ = abc.ABCMeta
    def __new__(mcls, cls_name, bases, namespace): #pylint: disable=C0202
         
         
        if not '__abstractmethods__' in namespace:
            raise TypeError("{0} missing required property: __abstractmethods__")
        # Create function stubs
        # ... is this unnecessary ???
        for name in namespace.get('__abstractmethods__', frozenset([])):
            namespace[name] = abc.abstractmethod(lambda *a,**kw: NotImplemented)
         
        cls = super(DuckMeta, mcls).__new__(mcls, cls_name, bases, namespace)
        return cls

    def __instancecheck__(self, instance):
        #classes are instances of type, instancesof classes are not
        if isinstance(instance, type):
            return False
        else:
            return all(
                _hasattr(instance, name) for name in self.__abstractmethods__
            )
    def __subclasscheck__(self, subklass):
        #print('subclasscheck', self, instance)
        #classes are instances of type, instancesof classes are not
        if isinstance(subklass, type):
            return all(
                _hasattr(instance, name) for name in self.__abstractmethods__
                )
        else:
            return False
    
    #@classmethod
#     def inherit(cls, *abstracts, **keywords):
#         return cls(*abstracts, **keywords)



class DuckType(object):
    """A metaclass for type-checking.

    # IDEA: __instancecheck__ & __subclasscheck__ not operating on DuckType itself
    # only on Ducklings descended from DuckType

    @todo: During __new__, actually construct the methods
    @todo: Allow this to accept other classes.
    @todo: Type checking on abstracts (sequence of strings)
    """
    __abstractmethods__ = frozenset([])
    __metaclass__ = DuckMeta
    def __new__(cls, *abstracts, **keywords):
        
        return DuckMeta(
            keywords.get('name', 'Duckling'),
            (cls, ),
            {'__abstractmethods__': cls.__abstractmethods__.union(frozenset(abstracts))}
        ) 
    @classmethod
    def branch(cls, *abstracts, **keywords):
        return cls(*abstracts, **keywords)


# IDEA: __instancecheck__ & __subclasscheck__ not operating on DuckType itself
# only on Ducklings descended from DuckType




import unittest

class DuckTypeTests(unittest.TestCase):
    def test_basic(self):
        pop = DuckType('pop')
        popget = DuckType('pop', 'get')
        popinsert = DuckType('pop', 'insert')

        self.assert_(isinstance([], pop))
        self.assert_(not isinstance([], popget))
        self.assert_(isinstance([], popinsert))
        
        self.assert_(isinstance({}, pop))
        self.assert_(isinstance({}, popget))
        self.assert_(not isinstance({}, popinsert))

    def test_structure(self):
        attrs = ['foo', 'bar', 'baz']
        quack = DuckType(*attrs)
        for name in attrs:
            self.assert_(hasattr(quack, name))
            
    def test_blank(self):
        nullduck = DuckType()
        self.assert_(not isinstance(dict, nullduck))
        
    
    def test_type(self):
        self.assert_(not isinstance(dict, DuckType))
        self.assert_(isinstance(DuckType, DuckMeta))
        self.assert_(isinstance(DuckType, type))
        self.assert_(isinstance(DuckMeta, type))
        
        attrs = ['foo', 'bar', 'baz']
        quack = DuckType(*attrs)
        self.type_bank(quack)

    
    def type_bank(self, quack):
        # quack is not an instance (it is a class)
        self.assert_(not isinstance(quack, DuckType))
        self.assert_(issubclass(quack, DuckType)) 
        self.assert_(isinstance(quack, type))
        self.assertEqual(quack.__metaclass__, DuckMeta)
        self.assert_(DuckType in quack.__mro__)
        self.assert_(object in quack.__mro__)
        
    def test_inheritance(self):         
        class MyDuckClass(DuckType):
            __abstractmethods__ = frozenset(['get'])

        self.assert_(isinstance({}, MyDuckClass))
        self.assert_(not isinstance([], MyDuckClass))

        def erroring_class():
            class ErroringDuckClass(DuckType):
                def irrelevant_methods(self):
                    pass
            return ErroringDuckClass
        self.assertRaises(TypeError,
            lambda: erroring_class()
        )

    def test_branch(self):
        pop = DuckType('pop', '__str__')
        popget = pop('get')
        popinsert = pop('insert', 'index')
        
        self.assertEqual(
            frozenset(['pop', '__str__', 'insert', 'index']),
            popinsert.__abstractmethods__
        )
        
        # Test branching
        self.type_bank(popget)
        self.type_bank(popinsert)

        self.assert_(isinstance([], pop))
        self.assert_(not isinstance([], popget))
        self.assert_(isinstance([], popinsert))
        
        self.assert_(isinstance({}, pop))
        self.assert_(isinstance({}, popget))
        self.assert_(not isinstance({}, popinsert))


if __name__ == "__main__":
    unittest.main()
