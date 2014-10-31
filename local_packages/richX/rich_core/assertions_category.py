"""
Assertions portion of rich_core.
This could reasonably be packaged on it's own, however,
a LOT of other subpackages of richX/ use it, so it is left as
part of rich_core/

@TODO Consider: could streamlined AssertKlass-only part be made, and placed in rich_core?
"""


import abc
import collections
# ? Should this be a relative import
from rich_core import *
from rich_core import _hasattr


#--------------------------------------------------------------------
#    Local Utility
#--------------------------------------------------------------------
def _inside(obj,container):
    """Used by IsEnum()/AssertEnum()"""
    return (obj in container)
def _haskey(mapping,key):
    """Used by HasKeys()/AssertKeys()
    #    requires mapping is Mapping, and key is hashable"""
    return (key in mapping)
class _oldclass: pass
_OLD_CLASS_TYPE = type(_oldclass)


#==============================================================================
#        Type Checking, Validation, and Assertion
#==============================================================================
#Core functions occur in triplets: (1) Is/Has, (2) Assert, (3) Validate
#For a particular PredicateFunctor - defined by a single function
#
#(1) IsType/AssertType/ValidateType
#        the most commonly used. checks isinstance()
#(2) IsSubclass/AssertSubclass/ValidateSubclass
#        rarely used, but very similar to IsType. Checks issubclass()
#(3) HasAttrs
#        Underlyies the core concept of duck-typing.
#(4) HasKeys
#(5) IsEnum
#
def category_message(obj,pos=None,neg=None,name=None,namefunc=None,verb=None):
    """Forms a default message, used in assertions on categories. (IsCategoryABC)
    category_message(obj,
        pos         = cls.handler(pos),
        neg         = cls.handler(neg),
        namefunc    = cls.category_name,
        verb        = "be in",
    )
    """
    if verb == None:
        verb = "satisfies categories "
    if not callable(namefunc):
        namefunc = lambda category: str(category)[:40]

    msg = str.format(
        "{0} of type '{1}' should",
        "'"+name+"'" if (isinstance(name,basestring)) else 'Object',
        type(obj).__name__
    )
    if pos != None:
        msg += " {verb} {categories}".format(
            verb = verb,
            categories = map(namefunc,pos),
        )
    if neg != None:
        if pos != None:
            msg += " and"
        msg += " not {verb} {categories}".format(
            verb = verb,
            categories = map(namefunc,neg),
        )
    return msg
#-----------------   Ancestor Abstract Base Classes   -----------------
class IsCategoryABC(object):
    """
    @todo: replace .reducer() with .pos_reducer(),.neg_reducer()
        So their name can be used in message() -->
            be instance of {reducer.__name__} {group}
            --> be instance of any (Sequence, NoneType)
    def __new__(cls,obj,pos=None,neg=None):
        obj_pos = cls.pos_reducer(cls.mapper(obj,pos)) if (pos!=None) else True
        obj_pos = True  if (pos==None) else cls.pos_reducer(cls.mapper(obj,pos))
        obj_neg = cls.neg_reducer(cls.mapper(obj,neg)) if (neg!=None) else False
        obj_neg = False if (neg==None) else cls.neg_reducer(cls.mapper(obj,neg))
        return (obj_pos and not obj_neg)
    """
    __metaclass__ = abc.ABCMeta
    def __new__(cls,obj,pos=None,neg=None):
        obj_pos = cls.reducer(cls.mapper(obj,pos)) if (pos!=None) else True
        obj_neg = cls.reducer(cls.mapper(obj,neg)) if (neg!=None) else False
        #obj_pos = cls.mapper(obj,pos) if (pos != None) else True
        #obj_neg = cls.mapper(obj,neg) if (neg != None) else False

        return (obj_pos and not obj_neg)
    #------ Abstract Functions
#     definition = abc.abstractproperty(lambda self: NotImplemented)
#     meets = abc.abstractmethod(lambda self, category: NotImplemented)
#     predicate = abc.abstractmethod(lambda self, obj, category: NotImplemented)
    @abc.abstractproperty
    def definition(self):
        return NotImplemented
    @abc.abstractproperty
    def meets(cls, category):
        return NotImplemented
    @abc.abstractproperty
    def predicate(cls, obj, category):
        return NotImplemented
    #-------- Mixin Methods
    #reducer = all
    @classmethod
    def reducer(cls, sequence):
        """Reduce a sequence to a single value.
        Nearly always 'all' or 'any'."""
        return all(sequence)
    #-------- Strategy Functions
    @classmethod
    def mapper(cls, obj, group):
        """Map predicate onto group of categories, for a given object."""
        return [
            cls.predicate(obj, category) #pylint: disable=no-value-for-parameter
            for category in cls.handler(group)
        ]
    @classmethod
    def handler(cls, group):
        if group == None:
            #group: no categories provided
            return group
        elif isinstance(group,NonStringSequence):
            #group: a sequence of categories
            for category in group:
                #cls.meets(category)
                cls.confirm(category)
            return tuple(group)
        else:
            #group: a single category
            cls.meets(group) #pylint: disable=no-value-for-parameter
            return tuple([group])
    @classmethod
    def __subclasshook__(cls, subklass):
        if cls is IsCategoryABC:
            if meets(subklass, cls):
                return True
        return NotImplemented


class AssertCategoryABC(object):
    """
    Intended to inherit from an instance of IsCategoryABC. Ex:
    class AssertType(AssertCategoryABC,IsType):
        ...
    """

    __metaclass__ = abc.ABCMeta
    def __new__(cls,obj,pos=None,neg=None,msg=None,name=None):
        if not cls.checker(obj,pos,neg):
            if msg == None:
                msg = cls.message(obj, pos=pos, neg=neg, name=name) #pylint: disable=no-value-for-parameter
            raise cls.exception(msg)
        else:
            return obj
    #-------    
    @abc.abstractmethod
    def checker(cls, obj, pos=None, neg=None):
        """Usually a related class, descended from IsCategoryABC()."""
        return NotImplemented
    @abc.abstractmethod
    def message(cls, obj, pos=None, neg=None, name=None):
        return NotImplemented    
    @abc.abstractmethod
    def exception(cls):
        return NotImplemented
    @classmethod
    def __subclasshook__(cls, subklass):
        if cls is AssertCategoryABC:
            if meets(subklass, cls):
                return True
        return NotImplemented

class ValidateCategoryABC(object):
    """Sugar. Partial for filling in arguments other than obj 
    to AssertCategoryABC."""
    __metaclass__ = abc.ABCMeta
    @abc.abstractproperty
    def asserter(self):
        return NotImplemented
    def __new__(cls,*args,**kwargs):
        @functools.wraps(cls.asserter)
        def wrapped(obj):
            return cls.asserter(obj, *args, **kwargs) #pylint: disable=star-args
        return wrapped
    @classmethod
    def __subclasshook__(cls, subklass):
        if cls is ValidateCategoryABC:
            if meets(subklass, cls):
                return True
        return NotImplemented

class PredicateFunctor(object):
    """
    PredicateFunctor():
        Gives:     confirm(), .name
        Requires:  .meets(), .predicate(), .definition
    """
    __metaclass__ = abc.ABCMeta
    #-------- Mixin
    @classmethod
    def confirm(cls,category):
        if not cls.meets(category):
            
            import pdb
            pdb.set_trace()
            print('--')
            
            
            raise TypeError(str.format(
                "Object of type {0} is not a valid category for {1}.",
                type(category).__name__,cls.__name__
            ))
        return category
    @classmethod
    def predicate(cls, obj, category):
        return cls.definition(obj, category)
    #-------- Abstract Properties
    @abc.abstractmethod
    def meets(self,category):
        return NotImplemented
    @abc.abstractproperty
    def definition(self):
        return NotImplemented
    @abc.abstractmethod
    def category_name(self,category):
        return NotImplemented
    @classmethod
    def __subclasshook__(cls, subklass):
        if cls is PredicateFunctor:
            if meets(subklass, cls):
                return True
        return NotImplemented


#-----------------   Instanced Predicate Functors   -----------------
class IsInstanceFunctor(PredicateFunctor):
    definition = staticmethod(isinstance)
    @classmethod
    def meets(cls,category):
        #return isinstance(category,type)
        # Is 'category' a new-style type, or old style class?
        return isinstance(category, (type, _OLD_CLASS_TYPE))
    @classmethod
    def category_name(cls,category):
        return category.__name__

class HasAttrsFunctor(PredicateFunctor):
    definition = staticmethod(_hasattr)
    @classmethod
    def meets(cls,category):
        return isinstance(category,basestring)
    @classmethod
    def category_name(cls,category):
        return category

class IsEnumFunctor(PredicateFunctor):
    definition = staticmethod(_inside)
    @classmethod
    def meets(cls,category):
        return isinstance(category,NonStringSequence)
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

class IsSubclassFunctor(PredicateFunctor):
    definition = staticmethod(issubclass)
    @classmethod
    def meets(cls,category):
        return isinstance(category, type)
    @classmethod
    def category_name(cls,category):
        return category.__name__

class HasKeysFunctor(PredicateFunctor):
    #category is a key
    definition = staticmethod(_haskey)
    @classmethod
    def meets(cls, category):
        return isinstance(category, collections.Hashable)
    @classmethod
    def category_name(cls, category):
        #category is a key
        return str(category)


#-----------------   isinstance Category Predicates   -----------------
class IsType(IsInstanceFunctor,IsCategoryABC):
    """
    IsType(obj,pos=None,neg=None) -> bool
    -----
    @future: use UniversalSet/UniversalClass and EmptySet/Nil
        as default values.


    """
    reducer = any
#older code uses the name 'IsKlass' instead of 'IsType'
IsKlass = IsType

class AssertType(AssertCategoryABC,IsType):
    """

    """
    checker = IsType
    exception = TypeError
    @classmethod
    def message(cls,obj,pos=None,neg=None,name=None):
        return category_message(obj,
            pos     = cls.handler(pos),
            neg     = cls.handler(neg),
            name    = name,
            namefunc= cls.category_name,
            verb    = "be instance of",
        )
#older code uses the name 'AssertKlass' instead of 'AssertType'
AssertKlass = AssertType

class ValidateType(ValidateCategoryABC):
    asserter = AssertType

 
#-----------------   hasattr() Category Predicates   -----------------

class HasAttrs(HasAttrsFunctor,IsCategoryABC):
    """Check if object has attributes."""
    def __new__(cls,obj,pos=None,neg=None):
        obj_pos = all(cls.mapper(obj,pos)) if (pos!=None) else True
        obj_neg = any(cls.mapper(obj,neg)) if (neg!=None) else False

        return (obj_pos and not obj_neg)

class AssertAttrs(AssertCategoryABC,HasAttrs):
    """Run assertion that object has(or not has) certain attributes by name."""
    checker     = HasAttrs
    exception   = AttributeError
    @classmethod
    def message(cls,obj,pos=None,neg=None,name=None):
        return category_message(obj,
            pos     = cls.handler(pos),
            neg     = cls.handler(neg),
            name    = name,
            namefunc= cls.category_name,
            verb    = "have attributes",
        )


#-----------------   enum Category Predicates   -----------------
#    ~
class IsEnum(IsEnumFunctor,IsCategoryABC):
    """Is obj drawn from finite list of possibilities, and/or not from
    a list of possibilities."""
    reducer = any
    @classmethod
    def handler(cls,group):
        wrap = lambda cat: tuple(cat) if cls.meets(cat) else tuple([cat])        
        if group == None:
            #enum group: no categories provided
            return group
        #elif isinstance(group,NonStringSequence):
        elif cls.meets(group):
            #Two possible enum groups:
            #1: a sequence of enum categories
            #  NonStringSequence containing at least one NonStringSequence
            #    ex. [['a','b'],'c'] --> (('a','b'),('c',))
            #        [['a','b']] --> (('a','b'),)
            if any(cls.meets(category) for category in group):
                return tuple([wrap(category) for category in group])
            #2: a single category, which is a sequence
            #  whether: ['a','b']-->(('a','b'),)
            else:
                return tuple([wrap(group)])
        else:
            #enum group: single atom: 'a' --> ('a',)
            return tuple([wrap(group)])


class AssertEnum(AssertCategoryABC,IsEnum):
    """ """
    checker = IsEnum
    exception = ValueError
    @classmethod
    def message(cls,obj,pos=None,neg=None,name=None):
        return category_message(obj,
            pos     = cls.handler(pos),
            neg     = cls.handler(neg),
            name    = name,
            namefunc= cls.category_name,
            verb    = "be in",
        )


#-----------------   issubclass() Category Predicates   -----------------
class IsSubclass(IsSubclassFunctor,IsCategoryABC):
    """IsSubklass(obj,isklasses=None,notklasses=None) -> bool
    -----
    @future: use UniversalSet/UniversalClass and EmptySet/Nil
        as default values.
    """
    reducer = any

class AssertSubclass(AssertCategoryABC,IsSubclass):
    """ """
    checker = IsSubclass
    exception = ValueError
    @classmethod
    def message(cls,obj,pos=None,neg=None,name=None):
        return category_message(obj,
            pos     = cls.handler(pos),
            neg     = cls.handler(neg),
            name    = name,
            namefunc= cls.category_name,
            verb    = "be subclass of",
        )

#-----------------   haskeys Category Predicates   -----------------

class HasKeys(HasKeysFunctor, IsCategoryABC):
    """ """
class AssertKeys(AssertCategoryABC, HasKeys):
    """ """
    checker = HasKeys
    exception = KeyError
    @classmethod
    def message(cls,obj,pos=None,neg=None,name=None):
        return category_message(obj,
            pos     = cls.handler(pos),
            neg     = cls.handler(neg),
            name    = name,
            namefunc= cls.category_name,
            verb    = "have all of",
        )