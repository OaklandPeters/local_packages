"""
I do not actually like this module, and would like to remove it.
However, some CCCID tools require it, in a way which is not trivial to remove.

"""
import collections
from .. import rich_core
from .. import rich_misc


class Options(object):
    def __init__(self,required=None,defaults=None,allowed=None):
        self._required = required
        self._defaults = defaults
        self._allowed = allowed
        
    #------ Properties
    @property
    def required(self):
        return self._required
    @required.setter
    def required(self,value):
        if value == None:
            value = []
        rich_core.AssertKlass(value,collections.Sequence)
        for elm in value:
            rich_core.AssertKlass(elm,basestring)
        self._required = value
    
    @property
    def defaults(self):
        return self._defaults
    @defaults.setter
    def defaults(self,value):
        if value == None:
            value = {}
        rich_core.AssertKlass(value,collections.Mapping)
        
        self._defaults = value
    
    @property
    def allowed(self):
        #Return all unique keys from required,defaults,and allowed
        return list(set(
            self._required + self._allowed + self._defaults.keys()
        ))
    @allowed.setter
    def allowed(self,value):
        if value == None:
            value = []
        rich_core.AssertKlass(value,collections.Sequence)
        for elm in value:
            rich_core.AssertKlass(elm,basestring)
        self._allowed = value
    def permitted(self,key):
        return (key in self.allowed)
    #--------
    def chainmap(self,*maps):
        rich_core.AssertKlass(maps,collections.Sequence)
        for elm in maps:
            rich_core.AssertKlass(elm,collections.Mapping)
        all_maps = maps + (self.defaults,)
        
        filt_maps = [
            dict(
                (key,value) for key,value in amap.items()
                if self.permitted(key)
            )
            for amap in all_maps
        ]
        
        options = Chainmap(*filt_maps)

        for key in self.required:
            assert(key in options), (
                "Missing key: "+key
            )

        return options
    options = chainmap


    

#Belongs with:         Ontology, or VOG (Vague Ontological Groupings)
class Que(object):
    '''Custom Null-type intended to distinguish optional arguments
    INTENTIONALLY not provided, and arguments with 'None' passed in.

    ~ a subset of None, useful when you want to distinguish between two or more
    possible subsets of None. Usage examples:

    Example #1: In assembling partial function calls - (1) 'Que' is a value
    stored for an argument which means that the argument is intentionally
    being left open, to be filled in by the later (partial) function
    call. Whereas, (2) 'None' can now refer to values which have not

    Example #2: Consider filling in a list from (index, value) pairs. Not all
    indexes are present, and they mot not be in order.

    Origin of the Name: Que, refers to 'que', the spanish word for 'what'.
    ------------------------------------
    @future: Set this to use __metaclass__ = abc.ABCMeta
        Then make this a virtual subclass of types.NoneType via:
            types.NoneType.register(Que)
    @future: allow Que to be initialized with a type object
       (for isinstance() calls) which specifies the eventual objects that can
       be filled into its place.

    #-----------------------------------
    @problem: this breaks a lot of tests which rely on: 'if obj is None:',
        which may be a problem if variables == Que() are pased down to
        other/later functions not created with Que() in mind.
        --> Solution: only use Que() for variables meant to be immediately
            distinguished INSIDE the function creating/using Que.

    #--------------     Usage:
    def myFunc(
    -------------
    @future: allow support for valid_types AND invalid_types, for compatability to
        assertklass(obj,isklasses,notklasses,msg)
        UNSPECIFIED is and isnot klasses:  via isinst(), handle_klasses()
            - ontology utility functions
    '''
    def __init__(self, *valid_types):
        #@future: def __init__(self,valid=None,invalid=None)
        #    klass_types = (Of(NonStringIterable,type),type(None))
        #    assert(isinstance(valid,klass_types))
        #    assert(isinstance(invalid,klass_types))
        #    self.valid_types = handle_klasses(valid)
        #    self.invalid_types = handle_klasses(invalid)
        #@THEN: 
        #--> def __instancecheck__(self, instance):
        #    return isinst(instance,self.valid_types,self.invalid_types)
        if len(valid_types) == 0:
            self.valid_types = (object, )    #~everything is valid
        else:
            assert(all(isinstance(vtype, type) for vtype in valid_types))
            self.valid_types = valid_types
    def __iter__(self):
        return iter(self.valid_types)
#    def __cmp__(self, other):
#        if isinstance(other, type(self)):
#            return set(self) == set(other)
#        elif isinstance(other, type(None)):
#        return False
    def __instancecheck__(self, instance):
        return isinstance(instance, self.valid_types)
        #@future: return isinst(instance,self.valid_types,self.invalid_types)
    def __repr__(self):
        return '{name}({vtypes})'.format(
            name=self.__class__.__name__,
            vtypes=self.valid_types)
    def __eq__(self, other):
        if other == None:
            return True
        elif isinstance(other, Que):
            return True
        else:
            return False
    def __call__(self, obj, **options):
        '''Only supported 'options' is currently options['default'].'''
        #@todo: allow support for valid_types AND invalid_types, for compatability to
        #    assertklass(obj,isklasses,notklasses,msg)
        #    --> 
        if isinstance(obj, self):
            return obj
        elif 'default' in options:
            return options['default']
        else:
            raise TypeError((
                "Invalid {0} assignment attempt. Object of type '{1}' is not "
                "an instance of one of the valid types: '{2}'.")
                .format(self.__class__.__name__, type(obj), self.valid_types))



class ArgDict(collections.MutableMapping):
#class ArgDict(object):
    '''
    Compare to argdict - which bypasses this complexity.
    '''
    #... I don't know if it's valid to inherit from both MutableMapping and MutableSequence
    _keymsg = "KeyError: Cannot {0} key of type '{1}'. Must be basestring or int."
    def __init__(self,*args,**kwargs):
        #[] Validate
        #isa(kwargs,MappingOf(Mapping,keys=basestring))
        for key,value in kwargs.items():
            assert(isinstance(key,basestring))
        self.args = args
        self.kwargs = kwargs
        #self.default = utility.Que()
    #--------------------------- Container Magic Methods
    def __iter__(self):
        for index in rich_core.indexes(self.args):
            yield index
        for index in rich_core.indexes(self.kwargs):
            yield index
    def __len__(self):
        return len(self.args)+len(self.kwargs) 
    def __contains__(self,x):
        if x in self.indexes():
            return True
        return False
    def __repr__(self):
        return repr(dict(self))
    #-------------------------- Properties
    @property
    def args(self):
        if not hasattr(self,"_args"):
            self._args = []
        return self._args
    @args.setter
    def args(self,values):
        assert(isinstance(values,collections.Sequence))
        self._args = values
    @property
    def kwargs(self):
        if not hasattr(self,"_kwargs"):
            self._kwargs = {}
        return self._kwargs
    @kwargs.setter
    def kwargs(self,mapping):
        assert(isinstance(mapping,collections.Mapping))
        for key in mapping:
            assert(isinstance(key,basestring))
        self._kwargs = mapping

    
    #-------------------------- Associative Functions (Items)
    def __getitem__(self,key):
        if isinstance(key,basestring):      return self.kwargs[key]
        elif isinstance(key,int):           return self.args[key]
        else:                               raise KeyError(self._keymsg.format('get',type(key)))
    def __setitem__(self,key,value):
        if isinstance(key,basestring):      self.kwargs[key] = value
        elif isinstance(key,int):           self.args[key] = value
        else:                               raise KeyError(self._keymsg.format('set',type(key)))
    def __delitem__(self,key):
        if isinstance(key,basestring):      del self.kwargs[key]
        elif isinstance(key,int):           del self.args[key]
        else:                               raise KeyError(self._keymsg.format('delete',type(key)))
    
    def pairs(self,iterator=False):
        return (rich_core.pairs(self.args,iterator) + 
                rich_core.pairs(self.kwargs,iterator) )
    def items(self):
        return self.pairs()
    def elements(self,iterator=False):
        return (rich_core.elements(self.args,iterator) +
                rich_core.elements(self.kwargs,iterator) )
    def values(self):
        return self.elements()
    def indexes(self,iterator=False):
        return (rich_core.indexes(self.args,iterator) +
                rich_core.indexes(self.kwargs,iterator) )
    def keys(self):
        return self.indexes()



class SimpleArgDict(dict):
    """Simple implementation of an argument dictionary.
    Keys must be int or basestring. Primarily used like:
    def myfunc(*args,**kwargs):
        argdict = ArgDict(*args,**kwargs)
        #... allows args to be passed around and iterated-over as single unit
    #-----
    >>> mine = ArgDict(123,'abc',user='Foo',kind='Bar')
    >>> mine
    {0: 123, 1: 'abc', 'kind': 'Bar', 'user': 'Foo'}
    
    >>> mine[23.9] = 'a'
    Traceback (most recent call last):
    KeyError: "KeyError: Cannot set key of type '<type 'float'>'. Must be basestring or int."
    
    >>> AG,KG = mine.args,mine.kwargs
    >>> AG
    (123, 'abc')
    >>> KG
    {'kind': 'Bar', 'user': 'Foo'}
    """
    default = None
    def __init__(self,*args,**kwargs):
        keypairs = (
            (key,value)
            for it in [enumerate(args),kwargs.items()]
            for key,value in it
        )
        dict.__init__(self,keypairs)
        #super(type(self),self).__init__(keypairs)
    def __setitem__(self,key,value):
        rich_core.AssertKlass(key,(int,basestring),msg=(
            "invalid argdict key type: '{0}'".format(
            type(key).__name__)))
        dict.__setitem__(self,key,value)
    @property
    def args(self):
        args = rich_misc.defaultlist(self.default)
        args.update((k,v) for k,v in self.items() if isinstance(k,int))
        return tuple(args)
    @property
    def kwargs(self):
        itempairs = ((k,v) for k,v in self.items() if isinstance(k,basestring))
        return dict(itempairs)



#-------------------------------------------
#Chainmap actually from another package, but moved here for simplicity
# and to prevent package reference.
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
    
    def doc_check(func):
        """Use to check specific functions, or get more information
        on why they failed the doctest."""
        doctest.run_docstring_examples(func,globals())

    import pdb
    pdb.set_trace()
    print('----')