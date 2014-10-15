"""
Provides ready-to-use inheritable classes for giving your own classes
Sequence (tuple or list-like) or Mapping (dict-like) behavior.

BasicMutableSequence can be seen as a replacement for UserDict, which
relies much more closely on collections.MutableMapping.

"""

import collections
#---- Custom modules
#from richX.rich_property import rich_property
#from local_packages.richX.rich_property import rich_property
#from .rich_property import rich_property
#from .richX import rich_property
from .. import rich_property




#==============================================================================
#        Sequences
#==============================================================================
#tuple and list-like custom objects, intended for inheritance.
#


class BasicSequence(collections.Sequence):
    """The most common use-case for inheriting from Sequence.
    Redirects to an inner list property called 'data'. Data is stored
    internally, and returned, as a tuple.
        
    When inheriting from this, it is very common to override __init__,
    but __init__ is provided as a simple default.
    
    self._validate() is not part of the Sequence definition, but is
    so commonly used that I have elected to include it.
    """
    def __init__(self, data):
        self.data = data
    #------ Redirection property
    @rich_property.VProperty
    def data(self):
        if not hasattr(self, '_data'):
            self._data = self._empty #default
        return self._data
    @data.setter
    def data(self, value):
        self._data = value
    @data.deleter
    def data(self):
        del self._data
    @data.validator
    def data(self, value):
        """Type-checking and type-conversion before assignment.
        Ex. If you wish to convert: None --> tuple() """
        assert(isinstance(value, collections.Sequence)), "value is not a Sequence."
        return tuple(value) # Store as tuple
    #------ Sequence: Required Magic Methods
    def __getitem__(self, index):
        return self.data[index]
    def __len__(self):
        return len(self.data)
    #------ Type Related
    @property
    def _empty(self):
        """Constructed for empty collection. ~default"""
        return tuple()
    

    #------ Extended magic methods
    def __repr__(self):
        return repr(self.data)
    def __eq__(self, other):
        return (self.data == other)
    def __ne__(self, other):
        return (self.data != other)
    

class BasicMutableSequence(BasicSequence, collections.MutableSequence):
    """The most common use-case for inheriting from MutableSequence.
    Redirects to an inner list property called 'data'.
    """
    @property
    def _empty(self):
        return list()
    @BasicSequence.data.validator
    def data(self, data):
        """Type-checking and type-conversion before assignment.
        Ex. If you wish to convert: None --> [] """
        assert(isinstance(data, collections.MutableSequence)), "value is not a Sequence."
        return list(data) # Store as tuple
    #----- MutableSequence: Required Magic Methods
    def __setitem__(self, index, value):
        self.data[index] = value
    def __delitem__(self, index):
        del self.data[index]
    def insert(self, index, value):
        self.data.insert(index, value)



#==============================================================================
#        Mappings
#==============================================================================
#Dict-like custom objects, intended for inheritance.
#

class BasicMapping():
    """The most common use-case for inheriting from Mapping.
    Redirects to an inner dict property called 'data'.
    Consequently, this data is not actually Immutable (or hashable).
    
    @TODO: Have internal storage be immutable and Hashable (collections.namedtuple).
    @TODO: Allow __init__ to handle the case of being given an Iterable of
        (key, value) pairs. Look at MutableMapping.update() for inspiration.
    """
    def __init__(self, mapping=None, **kwargs):
        #Initialize as immutable mapping, although store as dict.
        self.data = dict(
            (key, value)
            for amapping in (mapping, kwargs)
            for key, value in amapping.items()
        )
        
    #------ Redirection property
    @rich_property.VProperty
    def data(self):
        return self._data
    @data.setter
    def data(self, data):
        self._data = data
    @data.deleter
    def data(self):
        del self._data
    @data.validator
    def data(self, data):
        """Type-checking and type-conversion before assignement."""
        assert(isinstance(data, collections.Mapping)), "'data' is not a Mapping."
        return data
    #------ Mapping Magic Methods
    def __getitem__(self, key):
        return self.data[key]
    def __len__(self):
        return len(self.data)
    def __iter__(self):
        return iter(self.data)
    #------ Extended magic methods
    def __repr__(self):
        return repr(self.data)
    def __eq__(self, other):
        return (self.data == other)
    def __ne__(self, other):
        return (self.data != other) 
        
class BasicMutableMapping(BasicMapping, collections.MutableMapping):
    """The most common use-case for inheriting from MutableMapping.
    Redirects to an inner list property called 'data'.
    """
    def __init__(self, mapping=None, **kwargs):
        #To actually dispatch as per dict() is hard:
        self.data = self._empty
        if mapping is not None:
            self.update(mapping)
        if len(kwargs):
            self.update(kwargs)
    #------
    @property
    def _empty(self):
        return dict()
    #------
    def __setitem__(self, key, value):
        self.data[key] = value
    def __delitem__(self, key):
        del self.data[key]
