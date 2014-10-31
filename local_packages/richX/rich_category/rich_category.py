import abc
import collections
import functools

import rich_core as rcore
from chainmap import Chainmap

"""
@todo: run pylint on this. Easiest way would be to pull local_packages to my local computer,
    and then use the PyLint inside Eclipse.
    
    
@todo: Change CategoryFunctor.exception --> accept arguments like .message(...)
    and have the abstractproperty be: .exception_type = 
    
    @classmethod
    def exception(cls,*args,**kwargs):
        msg = cls.message(*args,**kwargs)
        return cls.exception_type(msg)
    exception_type= abc.abstractmethod(lambda message: NotImplemented)
    


@todo: Add capability for additional keywords, like 'of' 'keys', etc
    by making Is(),Assert(), message() support **kwargs
        _Is(), _Assert()
    
    def is_of(cls,obj,of):
        #f_of  = True  if (of ==None) else all(of.Is(elm) for elm in obj)
        if (of == None):
            return True
        else:
            assert(isinstance(of,CategoryFunctor))
            assert(isinstance(obj,collections.Iterable))
            return all(of.Is(elm) for elm in obj)
"""


"""
@todo: Enable syntax like this:
Assert([1,2],Type(Sequence),neg=Type(basestring),of=Type(basestring))
IE    Allows categories to be passed in for pos & neg & of seperately
Ex.    Assert([1,2],pos=Attrs('__iter__'),neg=Type(basestring),of=Type(basestring))
...    Maybe wiser to build this as:    class Asserter():
    rather than changing Assert() or CategoryFunctor()
Problem: category constructors like Type() accept pos & neg on their own
    So I'm not sure how to hanlde this
"""


#------------------------------------------------------------------------------
#        Local Utility Functions
#------------------------------------------------------------------------------
def new_message(cls,obj,pos=None,neg=None,name=None):
    """
    "{name} of type '{typename}' should {verbiage} "
    "{pos_reducer} of {pos} and not {neg_reducer} of {neg}"
    -->
    "Object of type 'list' should be instance of "
    "any of ['Sequence','NoneType'] and not any of ['basestring']"
    """
    if name == None:    name = 'Object'
    else:               name = "'{0}'".format(name)
    if   (pos == None) and (neg == None):
        return none
    template = "{name} of type '{typename}' should "
    
    if (pos != None):
        template += "{verbiage} "
    else:
        template += "not {verbiage} "
    
    if (pos != None):
        template += "{pos_reducer} of {pos} "
        if (neg != None):
            template += "and not "
    if (neg != None):
        template += "{neg_reducer} of {neg} "
    
    return template.strip().format(
        name            = name,
        typename        = type(obj).__name__,
        verbiage        = cls.verbiage,
        pos_reducer     = cls.pos_reduce.__name__,
        pos             = map(cls.category_name,cls.handler(pos)),
        neg_reducer     = cls.neg_reduce.__name__,
        neg             = map(cls.category_name,cls.handler(neg))
    )

    
def category_message(cls,obj,pos=None,neg=None,name=None):
    """
    category_message(
        cls, obj
        pos         = cls.handler(pos),
        neg         = cls.handler(neg),
        name        = "myvarname"
    )
    """
    if name == None:    name = 'Object'
    else:               name = "'{0}'".format(name)
    
    if   (pos == None) and (neg == None):
        #Should not happen
        return None
    elif (pos != None) and (neg == None):
        msg = str.format(
            ("{name} of type '{typename}' should {verbiage} "
            "{reducer} of {pos}"),
            name            = name,
            typename        = type(obj).__name__,
            verbiage        = cls.verbiage,
            reducer         = cls.pos_reduce.__name__,
            pos             = map(cls.category_name,cls.handler(pos))
        )
    elif (pos == None) and (neg != None):
        msg = str.format(
            ("{name} of type '{typename}' should not {verbiage} "
            "{reducer} of {neg}"),
            name            = name,
            typename        = type(obj).__name__,
            verbiage        = cls.verbiage,
            reducer         = cls.neg_reduce.__name__,
            neg             = map(cls.category_name,cls.handler(pos))
        )
    else:
        msg = str.format(
            ("{name} of type '{typename}' should {verbiage} "
            "{pos_reducer} of {pos} and not {neg_reducer} of {neg}"),
            name            = name,
            typename        = type(obj).__name__,
            verbiage        = cls.verbiage,
            pos_reducer     = cls.pos_reduce.__name__,
            pos             = map(cls.category_name,cls.handler(pos)),
            neg_reducer     = cls.neg_reduce.__name__,
            neg             = map(cls.category_name,cls.handler(neg))
        )
    return msg

def _haskey(mapping,key):
    #Used by HasKeys()/AssertKeys()
    #    requires mapping is Mapping, and key is hashable
    return (key in mapping)
def _inside(obj,container):
    #Used by IsEnum()/AssertEnum()
    return (obj in container)

def _validate_category(category):
    if isinstance(category,CategoryFunctor):
        return True    #Instanced CategoryFunctor()   - Type(..), Attrs(...)
    elif issubclass(category,CategoryFunctor):
        return True    #subclass of CategoryFunctor() - Type, Attrs
    else:
        raise TypeError("'category' must be an instance or subclass "
            "of CategoryFunctor."
        )

def instance_partial(self,name,attrs):
    """Make an instance-specific version of a classmethod ('name'),
    using partial arguments ('attrs') drawn from 'self'.
    
    name:      method name
    attrs:     list of names of attributes to include
    
    Usage:
        self.Is = self.make_partial('Is',['pos','neg')
    """
    #@instance_partial(self,attrs)
    #def Is(*args,**kwargs):
    #
    #instance_partial(self.Is,pluck(self.__dict__,attrs))    
    cls = type(self)
    cl_method = getattr(type(self),'Is')
    root = self
    
    @functools.wraps(cl_method)
    def wrapper(*args,**kwargs):
        #This currently leads to errors, if any default argument
        #(~normally kwarg) is instead passed as args (positional).
        defaults = Chainmap(
            kwargs,
            self.__dict__,
            default = None
        )
        #Filter kwargs & defaults by 'attrs'
        new_kwargs = dict(
            (key,defaults[key])
            for key in attrs
        )
        return cl_method(*args,**new_kwargs)
    return wrapper


        
def kw_defaults(*maps,**kwargs):
    """
    #self.Is = kw_defaults(self.__dict__,attrs)(type(self).Is)
    #    -- or --
    #@kw_defaults(self.__dict__,attrs)
    #def Is(*args,**kwargs):
    #    return 
    #self.Is =
    
    >>> mydict = {}
    >>> @kw_defaults({'three':10,'four':20})
    ... def adder(one,two,three=0,four=0):
    ...      return one+two+three+four
    >>> adder(1,2,three=3,four=4)
    10
    >>> adder(1,2,three=3)
    26
    >>> adder(1,2)
    33
    >>> adder(1,2,3)
    Traceback (most recent call last):
    TypeError: adder() got multiple values for keyword argument 'three'
    
    >>> def raw_adder(one,two,three=0,four=0):
    ...      return one+two+three+four
    >>> wrapped_adder = kw_defaults({'three':10,'four':20})(raw_adder)
    >>> wrapped_adder(1,2,three=3,four=4)
    10
    >>> wrapped_adder(1,2)
    33
    """ 
    keys = kwargs.get('keys',None)
    if keys == None:        keyfunc = lambda key: True
    elif isinstance(keys,collections.Sequence):
        keyfunc = lambda key: key in keys
    elif isinstance(keys,collections.Callable):
        keyfunc = keys
    else:
        raise TypeError("Invalid 'keys' argument type: "+type(keys).__name__)
    
    def outer(func):
        @functools.wraps(func)
        def wrapper(*args,**kwargs):
            cm = Chainmap(kwargs,*maps,**{'default': None})
            #nkwargs = dict((k,cm[k]) for k in attrs)
            nkwargs = dict((k,cm[k]) for k in cm if keyfunc(k))
            return func(*args,**nkwargs)
        return wrapper
    return outer



class UniversalSetABC(abc.ABCMeta):
    def __instancecheck__(self,instance):
        return True
    def __subclasscheck__(self,klass):
        return True

class EmptySetABC(abc.ABCMeta):
    def __instancecheck__(self, instance):
        if self in type(instance).__mro__:
            return True
        return False
    def __subclasscheck__(self, klass):
        try:
            return (EmptySet in klass.__mro__)
        except:
            return False
#        if hasattr(klass,'__mro__'):
#            return (self in klass.__mro__)
#        return (self in klass.__mro__)


class UniversalSet(object):
    """
    >>> values = [None,tuple(),{},int,type(None),set('a'),(1,2),map, lambda x:x]
    >>> Aleph = UniversalSet()
    >>> [(v in Aleph) for v in values]
    [True, True, True, True, True, True, True, True, True]
    >>> [isinstance(v,UniversalSet) for v in values]
    [True, True, True, True, True, True, True, True, True]

    >>> import types
    >>> type_objs = [v for (k,v) in vars(types).items() if not k.startswith('__')]
    >>> all([issubclass(t,UniversalSet) for t in type_objs])
    True
    """
    __metaclass__ = UniversalSetABC
    def __contains__(self,other):
        try:
            return (UniversalSet not in other.__mro__)
        except:
            return True
        #return True
    def __len__(self):
        return float("inf")
    def __iter__(self):
        return iter([])
#collections.Set.register(UniversalSet)
     
class EmptySet(object):
    """
    >>> values= [None,tuple(),{},type,type(None),set('a'),(1,2),map, lambda x:x]
    >>> Nil = EmptySet()
    >>> [(v in Nil) for v in values]
    [False, False, False, False, False, False, False, False, False]
    >>> [isinstance(v,EmptySet) for v in values]
    [False, False, False, False, False, False, False, False, False]
    
    >>> import types
    >>> type_objs = [v for (k,v) in vars(types).items() if not k.startswith('__')]
    >>> any([issubclass(t,EmptySet) for t in type_objs])
    False
    """
    __metaclass__ = EmptySetABC
    def __contains__(self,other):
        return False
    def __len__(self):
        return 0
    def __iter__(self):
        return iter([])







#----------------------------------------------------------
#        Core ABC - Category Functor
#----------------------------------------------------------
class CategoryFunctor(object):
    """
    Required:    definition, meets, category_name, 
                 pos_reduce, neg_reduce, message(), verbiage, exception
    
    
    Required Methods: functor-related
        definition, meets(), category_name()
            These relate to the core predicate function itself.
    Required Methods: validation related
        pos_reduce, neg_reduce, message(), verbiage, exception
            These relate to mapping & message-writing for Is()/Assert(). 
    Mixin Methods & Strategy-Functions:
        confirm(), predicate(), mapper(), handler()
    Dispatch Methods:
        Is(), Assert()
    Instance Methods:
        _Is(), _Assert(), partials()
            These change behavior for functions for subclasses, 
            vs. instances of those subclasses, and relate to setting 
            'partials' via instances.
    -------------
    
    -------------
    @todo: remove/combine predicate+definition
    @consider: whether it is advantageous to seperate this into: 
    functor-part:        definition, meets, category_name, predicate, confirm
    mapper-part:         mapper, handler
    validator-part:      pos_reducer, neg_reduce, message, verbiage, exception
                         Is, Assert
    partials-part:       __init__, partials, _Is, _Assert
    """
    __metaclass__ = abc.ABCMeta
    #-------- Mixin
    @classmethod
    def confirm(cls, category):
        if not cls.meets(category):
            raise TypeError(str.format(
                "Object of type {0} is not a valid category for {1}.",
                type(category).__name__,cls.__name__
            ))
        return category
    @classmethod
    def predicate(cls, obj, category):
        return cls.definition(obj, category)
    @classmethod
    def message(cls,obj,pos=None,neg=None,name=None):
        """
        "{name} of type '{typename}' should {verbiage} "
        "{pos_reducer} of {pos} and not {neg_reducer} of {neg}"
        -->
        "Object of type 'list' should be instance of "
        "any of ['Sequence','NoneType'] and not any of ['basestring']"
        """
        if name == None:    name = 'Object'
        else:               name = "'{0}'".format(name)
        if   (pos == None) and (neg == None):
            return none
        template = "{name} of type '{typename}' should "
        
        if (pos != None):
            template += "{verbiage} "
        else:
            template += "not {verbiage} "
        
        if (pos != None):
            template += "{pos_reducer} of {pos} "
            if (neg != None):
                template += "and not "
        if (neg != None):
            template += "{neg_reducer} of {neg} "
        
        return template.strip().format(
            name            = name,
            typename        = type(obj).__name__,
            verbiage        = cls.verbiage,
            pos_reducer     = cls.pos_reduce.__name__,
            pos             = map(cls.category_name,cls.handler(pos)),
            neg_reducer     = cls.neg_reduce.__name__,
            neg             = map(cls.category_name,cls.handler(neg))
        )
    #-------- Strategy Functions
    @classmethod
    def mapper(cls,obj,group):
        return [
            cls.predicate(obj,category)
            for category in cls.handler(group)
        ]
    @classmethod
    def handler(cls,group):
        if group == None:
            #group: no categories provided
            return tuple()
        elif isinstance(group,rcore.NonStringSequence):
            #group: a sequence of categories
            for category in group:
                #cls.meets(category)
                cls.confirm(category)
            return tuple(group)
        else:
            #group: a single category
            cls.meets(group)
            return tuple([group])
    #-------- Abstract Properties & Methods
    definition    = abc.abstractproperty(lambda self: NotImplemented)
    verbiage      = abc.abstractproperty(lambda self: NotImplemented)
    pos_reduce    = abc.abstractproperty(lambda self: NotImplemented)
    neg_reduce    = abc.abstractproperty(lambda self: NotImplemented)
    meets         = abc.abstractmethod(lambda self,category: NotImplemented)
    category_name = abc.abstractmethod(lambda self,category: NotImplemented)
    #message       = abc.abstractmethod(lambda self,obj,**kw: NotImplemented)
    exception     = abc.abstractmethod(lambda message: NotImplemented)

    #-------- Dispatch Integration
    @classmethod
    def Is(cls,obj,pos=None,neg=None):
        is_pos = True  if (pos==None) else cls.pos_reduce(cls.mapper(obj,pos))
        is_neg = False if (neg==None) else cls.neg_reduce(cls.mapper(obj,neg))
        return (is_pos and not is_neg)
    @classmethod
    def Assert(cls,obj,pos=None,neg=None,msg=None,name=None):
        if not cls.Is(obj,pos,neg):
            if msg == None:
                msg = cls.message(obj,pos=pos,neg=neg,name=name)
            raise cls.exception(msg)
        else:
            return obj



    #--------- Extended Dispatching / Instancing
    def __init__(self,pos=None,neg=None,msg=None,name=None):
        """
        Is(Keys)(obj,pos=(...),neg=(...))
        
        mykeys = Keys(pos=(...),neg=(...))
        Is(mykeys)(obj)
        """
        self.pos  = pos
        self.neg  = neg
        self.msg  = msg
        self.name = name
        
        #Change Is/Assert - use partial arguments drawn from self
        
        #Using pre-built 'wrappers'
        self.Is     = self._Is
        self.Assert = self._Assert

        #Via a specialized decorator
#        self.Is     = instance_partial(self,'Is',
#            ['pos','neg'])
#        self.Assert = instance_partial(self,'Assert',
#            ['pos','neg','name','msg'])

        #Via a generalized decorator
#        self.Is = kw_defaults(self.__dict__,
#            keys=['pos','neg']
#            )(self.Is)
#        self.Assert = kw_defaults(self.__dict__,
#            keys=['pos','neg','name','msg']
#            )(self.Assert)

    def _Is(self,obj,**kwargs):
        nkwargs = self.partials(['pos','neg'],**kwargs)
        return type(self).Is(obj,**nkwargs)

    def _Assert(self,obj,**kwargs):
        nkwargs = self.partials(['pos','neg','name','msg'],**kwargs)
        return type(self).Is(obj,**nkwargs)
    
    def partials(self,attrs,**kwargs):
        """Approximately, a wrapper/decorator that draws keyword defaults
        from self (self: as it is when partials called, not when declared).
        attrs: sequence of strings"""
        #cm = Chainmap(kwargs,self.__dict__,default = None)
        #return dict((k,cm[k]) for k in attrs)
        grab = lambda attr: kwargs.get(attr,self.__dict__.get(attr,None))
        nkwargs = dict((attr,grab(attr)) for attr in attrs)
        return nkwargs
    
    def __repr__(self):
        repr_str = (
            "{classname}(\n"
            "    pos  = {pos},\n"
            "    neg  = {neg},\n"
            "    name = {name},\n"
            "    msg  = {msg},\n"
        ).format(
            classname       = type(self).__name__,
            pos             = self.pos,
            neg             = self.neg,
            name            = self.name,
            msg             = self.msg,
        )
        return repr_str
    

    


#----------------------------------------------------------
#        Category Instances
#----------------------------------------------------------
class Type(CategoryFunctor):
    #__metaclass__ = abc.ABCMeta
    definition      = staticmethod(isinstance)
    verbiage        = "be instance of"
    pos_reduce      = any
    neg_reduce      = any
    exception       = TypeError
    message         = classmethod(category_message)
    @classmethod
    def meets(cls,category):
        return isinstance(category,type)
    @classmethod
    def category_name(cls,category):
        return category.__name__
    aleph           = UniversalSet
    nil             = EmptySet
#    @classmethod
#    def message(cls,obj,pos=None,neg=None,name=None):
#        return category_message(cls, obj,
#            pos = pos, neg = neg, name = name
#        )

class Keys(CategoryFunctor):
    definition  = staticmethod(_haskey)
    verbiage    = "have"
    pos_reduce  = all
    neg_reduce  = all
    exception   = KeyError
#    message     = classmethod(category_message)
    @classmethod
    def meets(cls, category):
        return isinstance(category, collections.Hashable)
    @classmethod
    def category_name(cls, category):
        return str(category)
#    aleph       = UniversalSet()
#    nil         = EmptySet()

class Attrs(CategoryFunctor):
    definition  = staticmethod(rcore._hasattr)
    verbiage    = "have attributes"
    pos_reduce  = all
    neg_reduce  = any
    exception   = AttributeError
#    message = category_message
    @classmethod
    def meets(cls,category):
        return isinstance(category,basestring)
    @classmethod
    def category_name(cls,category):
        return category
#    aleph       = UniversalSet()
#    nil         = EmptySet()


class Enum(CategoryFunctor):
    definition = staticmethod(_inside)
    verbiage   = "be"
    pos_reduce = any
    neg_reduce = any
    exception  = ValueError
    message    = classmethod(category_message)
    @classmethod
    def meets(cls,category):
        return (
            isinstance(category,collections.Container)
            and not isinstance(category,basestring)
        )
#        _is = lambda klass: isinstance(category,klass)
#        return _is(collections.Container) and not _is(basestring)
    @classmethod
    def category_name(cls,category):
        try:
            return category.__name__
        except AttributeError:
            try:
                return category.name
            except AttributeError:
                try:
                    assert(len(str(category)) < 80)
                    return str(category)
                except (AttributeError, AssertionError):
                    return str(category)[:80]+"..."
    #Overwrite handler():
    @classmethod
    def handler(cls,group):        
        wrap = lambda cat: tuple(cat) if cls.meets(cat) else tuple([cat])        
        if group == None:
            #enum group: no categories provided
            return set()
        elif cls.meets(group):
            #Possibility 1: a sequence of enum categories
            #    ex. [['a','b'],'c'] --> (('a','b'),('c',))
            if any(cls.meets(category) for category in group):
                return tuple([wrap(category) for category in group])
            #Possibility #2: a single category, which is a sequence
            #  ex: ['a','b']-->(('a','b'),)
            else:
                return tuple([group])
        else:
            #enum group: single atom: 'a' --> ('a',)
            return set([wrap(group)])
    aleph       = UniversalSet()
    nil         = EmptySet()

class Subclass(CategoryFunctor):
    definition = staticmethod(issubclass)
    verbiage   = "be subclass of"
    pos_reduce      = any
    neg_reduce      = any
    exception       = TypeError
    message         = classmethod(category_message)
    @classmethod
    def meets(cls,category):
        return isinstance(category, type)
    @classmethod
    def category_name(cls,category):
        return category.__name__
    aleph       = UniversalSet
    nil         = EmptySet


#----------------------------------------------------------
#        Dispatching Functions
#----------------------------------------------------------    
def Is(category):
    _validate_category(category)
    return category.Is
IsType      = Is(Type)
HasKeys     = Is(Keys)
HasAttrs    = Is(Attrs)
IsEnum      = Is(Enum)
IsSubclass  = Is(Subclass)

def Assert(category):
    _validate_category(category)
    return category.Assert
AssertType      = Assert(Type)
AssertKeys      = Assert(Keys)
AssertAttrs     = Assert(Attrs)
AssertEnum      = Assert(Enum)
AssertSubclass  = Assert(Subclass)



#def AssertKindOf(obj,pos=None,neg=None,msg=None,name=None,of=None):
#    """
#    >>> 
#    Assert(Type)([1,2],Sequence,of=basestring)
#    """
#    #Assert(cls,obj,**kwargs)
#    #pos        = kwargs.get('pos',  None)
#    #neg        = kwargs.get('neg',  None)
#    #msg        = kwargs.get('msg',  None)
#    #name       = kwargs.get('name', None)
#    #of         = kwargs.get('of',   None)
#    
#    #is_pos = True  if (pos==None) else cls.pos_reduce(cls.mapper(obj,pos))
#    is_pos = cls.is_pos(cls,obj,pos)
#    is_neg = cls.is_neg(cls,obj,neg)
#    
#    is_of = cls.is_of(cls,obj,of)
#def is_pos(cls,obj,pos):
#    if (pos==None):
#        return True
#    else:
#        return cls.pos_reduce(cls.mapper(obj,pos))
#def is_of(cls,obj,of):
#    #f_of  = True  if (of ==None) else all(of.Is(elm) for elm in obj)
#    if (of == None):
#        return True
#    else:
#        assert(isinstance(of,CategoryFunctor))
#        assert(isinstance(obj,collections.Iterable))
#        return all(of.Is(elm) for elm in obj)
        



if __name__ == "__main__":
#    nonstringsequence = Attrs(pos=['__len__','__iter__','__contains__','__getitem__'])
#    
#    
#    print(Is(nonstringsequence)("alksak"))
#    import pdb; pdb.set_trace()
#    print('----')

    
    
    
    
    
    import rich_category_test
    import doctest
    doctest.testmod(rich_category_test)
    
    def doc_check(func):
        """Use to check specific functions, or get more information
        on why they failed the doctest."""
        doctest.run_docstring_examples(func,globals())
        
    import pdb
    pdb.set_trace()
    print('-----')