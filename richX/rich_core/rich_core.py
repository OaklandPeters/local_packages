"""
Functions from rich_X.py modules, which are used by other rich_X.py modules.
Moved here, so rich_X.py modules do NOT import each other -- preventing
circular dependencies.

This modules is not intended to be used by anything other than building
the rich_X.py modules.



@TODO for Associative - consider making it require __iter__
    so that Associative can Mixin/interact with pairs(),indexes(),elements()
@TODO pairs(), elements(), indexes(): ammend so that they apply exactly 
    to objects which match the Associative ABC.
    ... currently, pairs/elements/indexes only works for NonString
    Mappings and Sequences,
    but Associative is defined for any iterable with __getitem__
    ... perhaps: they should do:
    AssertKlass(container,Associative):
    if _hasattr(container,'keys'):    #~Mappings
        gen = ((key,container[key]) for key in container.keys())
    else:    #~Iterables
        gen = enumerate(container)
@TODO Associative(): also ammend so it closely matches conditions for the
    pairs(), elements(), indexes()
"""

import collections
import abc
import functools





#--------------------------------------------------------------------
#    Core Functions
#--------------------------------------------------------------------
# Used frequently by other rich_X modules.
def _hasattr(subklass, attr):
    """Determine if subklass, or any ancestor class, has an attribute.
    Copied shamelessly from the abc portion of collections.py.
    """
    try:
        return any(attr in B.__dict__ for B in subklass.__mro__)
    except AttributeError:
        # Old-style class
        return hasattr(subklass, attr)

def required(mapping, keys):
    """Throws error if mapping does not have all of keys."""
    assert(isinstance(mapping,collections.Mapping)), "Not a mapping."
    for key in keys:
        if key not in mapping:
            raise KeyError(key)
def defaults(*mappings):
    """Handles defaults for sequence of mappings (~dicts).
    The first (left-most) mapping is the highest priority."""
    return dict(
        (k, v)
        for mapping in reversed(mappings)
        for k, v in mapping.items()
    )

def meets(obj, abstract):
    """Determines if an object meets an abstract interface (from abc module)."""
    return all(
        _hasattr(obj, attr) for attr in abstract.__abstractmethods__
    )

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


#--------------------------------------------------------------------
#    Class support
#--------------------------------------------------------------------
class ClassProperty(property):
    """Provides a getter-property for classmethods. Due to complicated reasons,
    there is no way to make classmethod setter-properties work in Python
    """
    def __get__(self, cls, owner):
        return self.fget.__get__(None, owner)()

class abstractclassmethod(classmethod): #pylint: disable=invalid-name
    """A decorator indicating abstract classmethods, similar to abstractmethod.
    Requires that the class descend from abc.ABCMeta.
    This is a backport of the abstract-class-method from Python 3.2 to Python 2.6.
    """
    __isabstractmethod__ = True

    def __init__(self, a_callable):
        #assert(issubclass(callable, abc.ABCMeta)), "object is not a subclass of ABCMeta."
        #assert(callable(a_callable)), "object is not callable."
        a_callable.__isabstractmethod__ = True
        super(type(self), self).__init__(a_callable) #pylint: disable=bad-super-call


#--------------------------------------------------------------------
#    Abstract Base Classes
#--------------------------------------------------------------------
class NonStringIterable(object):
    '''Provides an ABC to duck-type check for iterables OTHER THAN strings.
    Includes Sequences (lists, tuples), Mappings (dicts), and Iterators but not
    strings (unicode or str).
    '''
    __metaclass__ = abc.ABCMeta
    __slots__ = ()
    @abc.abstractmethod
    def __iter__(self):
        while False:
            yield None
    @classmethod
    def __subclasshook__(cls, subklass):
        if cls is NonStringIterable:
            #if any("__iter__" in B.__dict__ for B in subklass.__mro__):
            if _hasattr(subklass, "__iter__"):
                return True
        return NotImplemented


class NonStringSequence(collections.Sized, collections.Iterable, 
    collections.Container):
    '''Convenient ABC to duck-type check for sequences OTHER THAN strings.
    Includes Sequences (lists, tuples) but not strings (unicode or str), 
    Mappings (dicts), or Iterators.
    '''
    __metaclass__ = abc.ABCMeta
    @classmethod    
    def __subclasshook__(cls, subklass):
        if cls is NonStringSequence:
            if (issubclass(subklass, collections.Sequence)
                and not issubclass(subklass,basestring)):
                return True
        return NotImplemented

    @abc.abstractmethod
    def __getitem__(self, index):
        raise IndexError

    def __iter__(self):
        i = 0
        try:
            while True:
                val = self[i]
                yield val
                i += 1
        except IndexError:
            return
    def __contains__(self, value):
        for val in self:
            if val == value:
                return True
        return False
    def __reversed__(self):
        for i in reversed(range(len(self))):
            yield self[i]
    def index(self, value):
        """Return index of first element matching 'value'."""
        for ind, val in enumerate(self):
            if val == value:
                return ind
        raise ValueError
    def count(self, value):
        """Count instances of value."""
        return sum(1 for v in self if v == value)
NonStringSequence.register(tuple)
NonStringSequence.register(xrange)


class Associative(object): #pylint: disable=abstract-class-not-used, incomplete-protocol
    '''Abstract Base Class for objects which are Iterable, and respond to
    item-retreival (__getitem__).
    Includes Mappings and Sequences, but not Iterators or strings (strings
    intentionally excluded).

    Importantly, this indicates objects on which the generic iterator functions
        pairs(),elements(),indexes() can operate.
    @TODO ammend pairs/elements/indexes() so that this is actually true.
    @TODO also ammend Associative so this is true.
        ... currently, pairs/elements/indexes only works for NonString
        Mappings and Sequences,
        but Associative is defined for any iterable with __getitem__
    ... perhaps: they should do one of two:

        AssertKlass(container,Associative):
        if HasAttr(container,'keys'):    #~Mappings
            gen = ((key,container[key]) for key in container.keys())
        else:    #~Iterables
            gen = enumerate(container)
    '''
    __metaclass__ = abc.ABCMeta
    __slots__ = ()
    @abc.abstractmethod
    def __iter__(self):
        while False:
            yield None
    @abc.abstractmethod
    def __getitem__(self, key):
        raise KeyError
    @classmethod
    def __subclasshook__(cls, subklass):
        if cls is Associative:            
            #'has': simple syntactic sugar
            _has = lambda name: _hasattr(subklass,name)
            if _has("__getitem__") and _has("__iter__"):
                return True
        return NotImplemented




#==============================================================================
#        Basic Iterator Tools - widely used
#==============================================================================

#pairs/indexes/elements ~~ items/keys/values , but for sequences AND mappings
#These correspond to iteration over objects which are Associative (see class).
def pairs(container, iterator=False):
    '''.items()-like iterator function, generalized for Sequence and Mappings,
    while not iterating over strings.

    ?? Question: for non-Sequence, non-Mapping 'container', should this:
        (1) raise TypeError, or (2) return iter([]) for
    '''
    if isinstance(container, collections.Mapping):
        #Not all Mappings have an iteritems method.
        gen = collections.Mapping.iteritems(container)


    elif (isinstance(container, collections.Sequence)
        and not isinstance(container, basestring)):
    #@todo:
    #elif IsKlass(container,Sequence,notklasses=basestring):
        gen = enumerate(container)
    else:
        raise TypeError("Cannot build a pairs() iterator because '{0}' object"
            " is either not a Mapping or a Sequence, or is a basestring."
            .format(type(container)))

    if iterator:
        return gen
    else:
        return list(gen)

def indexes(container, iterator=False):
    """Return keys or numeric indexes (if a sequence)."""
    gen = (index for index, element in pairs(container, iterator=True))

    if iterator:
        return gen
    else:
        return list(gen)

def elements(container, iterator=False):
    """Returns all values from mappings, and all elements of sequences."""
    gen = (element for index, element in pairs(container, iterator=True))

    if iterator:
        return gen
    else:
        return list(gen)