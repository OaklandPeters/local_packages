"""
@author: Oakland John Peters
@institution: Dakshanamurthy Laboratory, at Georgetown University Medical Center
@contact: Oakland Peters: ojp4@georgetown.edu, Sivanesan Dakshanamurthy: sd233@georgetown.edu
@created: ~ 11/15/2013

An Implementation of Multimaps, written for Python 2.7



@todo remove() --> refers to __delitem__
@todo __delitem__ --> abstractmethod
"""
import collections
import abc


class MultimapABC(collections.MutableMapping):
    '''Abstract class for multimaps, implementing the MutableMapping interface.
    Holds data in a dictionary (self.data). For most subtypes, self.data will be
    a variety of defaultdict.
    '''
    __metaclass__ = abc.ABCMeta
    __init__ = abc.abstractmethod(lambda self, *args, **kwargs: NotImplemented)
    
    @property
    def data(self):
        """Access to the internal dictionary."""
        return self._data
    @data.setter
    def data(self, value):
        """Setter for data property."""
        if not hasattr(self,'_data'):
            self._data = value
        else:
            #For defaultdicts -- ie subclasses SetMultimap, ListMultimap
            if hasattr(self._data,'default_factory'):
                self._data = type(self._data)(
                    self._data.default_factory,value #pylint: disable=maybe-no-member
                )
            else:
                self._data = type(self._data)(value) #pylint: disable=attribute-defined-outside-init

    @abc.abstractmethod
    def __setitem__(self, key, value):
        self.data[key] = value
    @abc.abstractmethod
    def remove(self, key, value):
        """Delete a value from a key"""
        del self.data[key][value]

    def __delitem__(self, key):
        del self.data[key]
    def __getitem__(self, key):
        '''Uses self.data.get(key) instead of self.data[key] - because
        Bypasses default item creation, so getitem doesn't
        create a new item, but setitem does.
        '''
        if key not in self.data:     #BEST
            raise KeyError(str(key))
        else:
            return self.data.get(key)


    def __contains__(self, key):
        return key in self.data
    def __iter__(self):
        return iter(self.data)
    def __len__(self):
        return len(self.data.keys())
    def __str__(self):
        return "{0}: {1}".format(self.__class__.__name__,self.data)
    def __repr__(self):
        return "{0}({1})".format(self.__class__.__name__,repr(self.data))
    def setdefault(self, key, default=None):
        'D.setdefault(k[,d]) -> D.get(k,d), also set D[k]=d if k not in D'
        try:
            return self[key]
        except KeyError:
            self[key] = default
        #return default            #BUG - when self[key] != default AFTER assignment
        return self[key]

    def insert(self, key, values):
        """Used for implicit iteration."""
        if isinstance(values,collections.Iterable) and not isinstance(values,basestring):
            for val in values:
                self[key] = val
        else:
            self[key] = values

    def update(self, other=None, **kwds):
        '''takes advantage of implicit Iteration via self.insert()'''
        if other == None:
            other = tuple()

        if isinstance(other, collections.Mapping):
            for key in other:
                self.insert(key, other[key])
        elif hasattr(other, "keys"):
            for key in other.keys(): #pylint: disable=maybe-no-member
                self.insert(key, other[key])
        else:
            #(key, value) pairs
            for key, value in other:
                self.insert(key, value)
        for key, value in kwds.items():
            self.insert(key,other[key])


class SetMultimap(MultimapABC):
    '''Multimap of sets - prevents duplications. '''
    def __init__(self):
        self.factory = set
        self.data = collections.defaultdict(self.factory)
    def __setitem__(self, key, value):
        self.data[key].add(value)
    def remove(self,key,value):
        self.data[key].remove(value)

class ListMultimap(MultimapABC):
    ''' Multimap of lists - allows duplications.'''
    def __init__(self):
        self.factory = list
        self.data = collections.defaultdict(self.factory)
    def __setitem__(self, key, value):
        self.data[key].append(value)
    def remove(self,key,value):
        index = self.data[key].index(value)
        del self.data[key][index]


class DictMultimap(MultimapABC):
    '''Multimap of dicts - allows for fast membership checking.'''
    def __init__(self):
        self.factory = dict
        self.data = collections.defaultdict(self.factory)
    def __setitem__(self, key, value):
        self.data[key][value] = True
    def remove(self,key,value):
        del self.data[key][value]


class URLMultimap(MultimapABC):
    ''' Allow List-like behavior, but return size 0/1 lists
    as though they were NOT lists.'''
    def __init__(self):
        self.factory = list
        self.data = collections.defaultdict(self.factory)
    def __setitem__(self, key, value):
        self.data[key].append(value)
    def __getitem__(self,key):
        value = self.data[key]
        if isinstance(value,basestring):
            return value
        #Destructure -- so it doesn't look like a list
        elif len(value) == 0:
            return None
        elif len(value) == 1:
            return value[0]
        else:
            return value
    def remove(self,key,value):
        index = self.data[key].index(value)
        del self.data[key][index]