"""
Taken from: http://code.activestate.com/recipes/305268/
    By: Created by Raymond Hettinger on Mon, 13 Sep 2004 (PSF)
and then modified, given different default handling, and slightly expanded
    By: Oakland Peters on Thu, 06 Mar 2014
"""

import collections

#class Chainmap(UserDict.DictMixin):
class Chainmap(collections.Mapping):
    """Combine multiple mappings for sequential lookup.
    Does not support item assignment. To get item assignment, first
    convert to a dict.

    For example, to emulate Python's normal lookup sequence:

        import __builtin__
        pylookup = Chainmap(locals(), globals(), vars(__builtin__))

    >>> d1 = {'a':1, 'b':2}
    >>> d2 = {'a':3, 'd':4}
    >>> cm = Chainmap(d1, d2, default=KeyError)
    >>> dm = Chainmap(d1, d2, default=None)
    >>> em = Chainmap(d1, d2, default=5)

    >>> cm['a'],cm['b'],cm['d']
    (1, 2, 4)

    >>> cm['f']
    Traceback (most recent call last):
    KeyError: 'f'
    >>> dm['f']
    >>> em['f']
    5


    >>> ('f' in cm, 'f' in dm, 'f' in em)
    (False, False, False)
    >>> em
    ({'a': 1, 'b': 2}, {'a': 3, 'd': 4})

    >>> cm.get('a', 10)
    1
    >>> cm.get('f', 40)
    40


    Example:
    class SQLClass(object):
        defaults = {
            'driver':               'com.mysql.jdbc.Driver',
            'dburl':                'jdbc:mysql://localhost/drug_db',
            'proptable':            'testproptb',
            'login':                'Peters',
            'password':             'tsibetcwwi'
        }
        def __init__(self,table=None,**options):
            self.table = table

            self._parameters = Chainmap(options,
                self.defaults,
                default=None
            )
    """

    def __init__(self, *maps, **kwargs):
        self._maps = maps

        if 'default' in kwargs:
            self._default = kwargs['default']
        else:
            self._default = KeyError
    def __simpleget(self, key):
        """Look for a key in self._maps. If not found, raise KeyError."""
        for mapping in self._maps:
            try:
                return mapping[key]
            except KeyError:
                pass
        raise KeyError(key)
    def __getitem__(self, key):
        """As __simpleget(), except accounts for possibility of a default value."""
        try:
            return self.__simpleget(key)
        except KeyError:
            if isinstance(self._default, type):
                if issubclass(self._default, Exception):
                    raise self._default(key)
            return self._default
    def keys(self):
        accumulator = []
        for mapping in self._maps:
            accumulator.extend(mapping.keys())
        return list(set(accumulator))
    def __iter__(self):
        return iter(self.keys())
    def __contains__(self, key):
        return key in self.keys()
    def __len__(self):
        return len(self.keys())
    def __repr__(self):
        return repr(self._maps)
    def get(self, key, default=None):
        #Overrides keyword default
        if default == None:
            return self[key]
        else:
            try:
                return self.__simpleget(key)
            except KeyError:
                return default
    def append(self, new_map):
        """Add a new mapping to the end of the mappings to be chained."""
        assert(isinstance(new_map, collections.Mapping)),(
            "New maps must be Mapping objects."
        )
        self._maps = self._maps + (new_map, )

if __name__ == "__main__":
    import doctest
    doctest.testmod()
