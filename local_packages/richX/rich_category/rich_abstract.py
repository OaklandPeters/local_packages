import abc
import collections


class UniversalSet(collections.Set):
    """UniversalSet of sets, and also a universal parent
    for classes. This is really just an experiment.
    
    Universal = UniversalSet()
    X in Universal
        --> True for all X
    isinstance(X,Universal)
        --> True for all X
    
    >>> issubclass(object,UniversalSet)
    True
    >>> isinstance(object(),UniversalSet)
    True
    >>> isinstance(None,UniversalSet)
    True
    >>> issubclass(basestring,UniversalSet)
    True
    >>> isinstance('a',UniversalSet)
    True
    
    >>> Universal = UniversalSet()
    >>> 'a' in Universal
    True
    >>> [3,2,5] in Universal
    True
    """
    __metaclass__ = abc.ABCMeta
    def __contains__(self,other):
        return True
    #@property
    def __len__(self):
        return float("inf")
    def __iter__(self):
        return iter([])
    @classmethod
    def __subclasshook__(cls, subklass):
        if cls is UniversalSet:
            return True
        return NotImplemented


class EmptySet(collections.Set):
    """
    
    Nil = EmptySet()
    X in Nil
        --> False for all X
    isinstance(X,Nil)
        --> False for all X
    
    . . . EXCEPT that Nil contains Nil
    
    >>> issubclass(object,EmptySet)
    False
    >>> isinstance(object(),EmptySet)
    False
    >>> isinstance(None,EmptySet)
    False
    
    
    >>> Nil = EmptySet()
    >>> 'a' in Nil
    False
    """
    __metaclass__ = abc.ABCMeta
    def __contains__(self,other):
        if EmptySet in type(other).__mro__:
            return True
        return False
    def __len__(self):
        return 0
    def __iter__(self):
        return iter([])
    @classmethod
    def __subclasshook__(cls, subklass):
        if cls is Nil:
            return False
        return NotImplemented

Universal = UniversalSet()
Nil = EmptySet()




if __name__ == "__main__":
    
    [3,2,5] in Universal
    
    import doctest
    doctest.testmod()
    
    def doc_check(func):
        """Use to check specific functions, or get more information
        on why they failed the doctest."""
        doctest.run_docstring_examples(func,globals())

    import pdb
    pdb.set_trace()
    print()