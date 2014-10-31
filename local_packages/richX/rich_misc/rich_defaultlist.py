import collections

#==============================================================================
#            Unclassified
#==============================================================================
class defaultlist(list):
    """Similar to collections.defaultdict, but a list.
    First argument ('default') is a constructor which creates default values.
    This defaults to int (integers). Special case - if default is not
    a callable object, then a lambda returning that value is used.
        .update() - acts as the update() function of a mapping/dict
    
    #Provide default value as constructor function (list,int,dict,etc)
    >>> deflist = defaultlist(list)
    >>> deflist[3] = 'a'
    >>> deflist
    [[], [], [], 'a']
    >>> deflist.update({0:1,5:6})
    >>> deflist
    [1, [], [], 'a', [], 6]
        
    #Can also provide instance as default (None,'user',23, etc)
    >>> nullablelist = defaultlist(None)
    >>> nullablelist.update((0,1),(3,4))
    >>> nullablelist
    [1, None, None, 4]
    >>> nullablelist.update(enumerate(5,10))
    >>> nullablelist
    [5, 6, 7, 8, 9]
    
    #Deletion removes an element, rather than setting it to default
    >>> del mydeflist[3]
    >>> mydeflist
    [5, 6, 7, 9]
    """
    def __init__(self,default=int):
        #Call __init__ of parent -- list()
        super(type(self),self).__init__()   #list.__init__(self)
        if not callable(default):
            self.default = lambda : default
        else:
            self.default = default
        
    def __setitem__(self, index, value):

        size = len(self)
        if index >= size:
            self.extend(self.default for _ in range(size, index + 1))
        list.__setitem__(self, index, value)
    @property
    def default(self):
        return self._default()
    @default.setter
    def default(self, func):
        """func: ex. initializers: int,list, etc."""
        assert(callable(func)), "'func' is not callable."
        self._default = func
    def update(*args, **kwargs):
        """Taken from _abcoll.py Mapping.update()
        D.update([E, ]**F) -> None.  Update D from mapping/iterable E and F.
        If E present and has .keys():     for k in E: D[k] = E[k]
        If E present and lacks .keys():   for (k, v) in E: D[k] = v
        In either case, followed by:      for k, v in F.items(): D[k] = v
        
        TLDR: Arguments ~ (self,other,*args,**kwargs)
            except other may not be specified
        """    
        if len(args) > 2:
            raise TypeError("update() takes at most 2 positional "
                            "arguments ({} given)".format(len(args)))
        elif not args:
            raise TypeError("update() takes at least 1 argument (0 given)")
        self = args[0]
        other = args[1] if len(args) >= 2 else ()
    
        if isinstance(other, collections.Mapping):
            for key in other:
                self[key] = other[key]
        elif hasattr(other, "keys"):
            for key in other.keys():
                self[key] = other[key]
        else:
            for key, value in other:
                self[key] = value
        for key, value in kwargs.items():
            self[key] = value