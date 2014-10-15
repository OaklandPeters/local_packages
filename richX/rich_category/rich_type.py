import abc
import collections
import re
import functools
#----
import rich_core as rcore

#==============================================================================
#        Input Validation & Ontology
#==============================================================================
#Relates to Ontology functions
def validate(expression, response=None):
    '''
    Similar to 'assert', but appropriate for validating user-input.

    expression: may be a function or result of an expression.
    response:   may be None, string, or an Exception
    '''
    #@todo: Add example for this.
    if isinstance(expression, collections.Callable):
        expr_val = expression()
    else:
        expr_val = expression

    if not expr_val:
        if response is None:
            raise ValidationError()
        elif isinstance(response, basestring):
            raise ValidationError(response)
        if isinstance(response, Warning):
            warnings.warn(response)
        elif isinstance(response, Exception):
            raise response
        else:
            try:
                raise ValidationError(response)
            except:
                raise ValidationError()

class Nil(object):
    """Class which is not parent of anything.
    Used so this is True:
    >>> obj = object()
    >>> not issubclass(object,Nil)
    True
    >>> not isinstance(obj,Nil)
    True
    >>> not isinstance(None,Nil)
    True
    """
    __metaclass__ = abc.ABCMeta
    __slots__ = ()
    @classmethod
    def __subclasshook__(cls, subklass):
        if cls is Nil:
            return False
        return NotImplemented

def validate_type(obj, valid, invalid=Nil):
    '''Sugar for a special case of validate().
    If obj is not instance of class/type in valid (or instance of
    subclasses of those), raises an informative Exception.
    
    >>> validate_type("I am a string", [str, unicode])
    '''
    valid = rcore.ensure_tuple(valid)
    invalid = rcore.ensure_tuple(invalid)

    #[] Check obj
    if not isinstance(obj,valid):
        msg = ("Invalid object of type {0}\n."
            "Should be an instance of a class derived from: {1}."
            ).format(type(obj), valid)
        raise ValidationError(msg)
    if isinstance(obj,invalid):
        msg = ("Invalid object of type {0}\n."
            "Should NOT be an instance of a class derived from: {1}."
            ).format(type(obj), invalid)
        raise ValidationError(msg)
    #If no error - return nothing
    #return obj    


#class ValidationError(Exception):
class ValidationError(TypeError):
    #Future: have sugar for saying what is valid types, and what the type received was
    def __init__(self, message=None):
        if message == None:
            message = "Error during validation."
        super(type(self), self).__init__(message)

#class ElseError(TypeError):
class ElseError(ValueError):
    def __init__(self, message=None):
        if message == None:
            message = (
                "Logical error from missing 'else'. A condition was not "
                "caught for one of the if/elif cases."
            )
                #" and 'else' (fallthrough) invalid in this case.")
        super(type(self), self).__init__(message)





#Belongs with:         Extended Iterator Tools
#Belongs with:         Ontology, or VOG (Vague Ontological Groupings)
class StringEnum(object):
    '''
    @todo: This needs to become a class-factory.
        I have heard there are bugs in Python dealing with using a class
        to create classes.

    #@todo: make this callable, to the group-reduction/mapping
    #>>> myenum = Enum(('index', 'key'), ('element', 'value'))
    #>>> group_name = myenum('key')
    #>>> group_name
    #'key'
    #@todo: input: **namedEquivGroups:
        def __init__(self, *equivGroups, **namedEquivGroups):
    #@todo: generalize to class Enum() which allows functions, compiled regex
    '''
    __metaclass__ = abc.ABCMeta
    def __init__(self, *equivGroups):
        validate(equivGroups, Of(tuple, NonStringIterable))
        
        #[] Groups
        self.groups = dict(
            (eqgroup[0], eqgroup)
            for eqgroup in equivGroups
        )
    def __isinstancecheck__(self, instance):
        #Cannot define 'isinstance' via '__subclasshook__' method, because
        #    cannot determine membership in StringEnum via duck-typing alone.
        return any(
            (instance in group_aliases)
            for group_aliases in self.groups.values()
        )
    def __call__(self, instance):
        return first(
            group_name
            for group_name, group_aliases
            in self.groups.items()
            if instance in group_aliases
        )


class NonStringIterable(object):
    '''Provides an ABC to duck-type check for iterables OTHER THAN strings.
    Ex. isinstance(myvar, NonStringIterable)

    Addendum: I believe this class is not necessary in Python 3, which makes
    isinstance('aksl', collections.Iterable) == False
    
    >>> issubclass(int,NonStringIterable)
    False
    >>> isinstance(1,NonStringIterable)
    False
    >>> isinstance(["a"],NonStringIterable)
    True
    >>> issubclass(list,NonStringIterable)
    True
    >>> isinstance("a",NonStringIterable)
    False
    >>> isinstance(unicode('abc'),NonStringIterable)
    False
    >>> isinstance(iter("a"),NonStringIterable)
    True
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
            if rcore._hasattr(subklass, "__iter__"):
                return True
        return NotImplemented



class NonStringSequence(collections.Sized, collections.Iterable, 
    collections.Container):
    '''Convienent ABC to duck-type check for sequences OTHER THAN strings.
    This is almost an exact copy of Sequence from collections, except that
    it uses the ABCMeta, __subclasshook__, and does not register basestring
    or buffer as virtual subclasses.

    
    >>> issubclass(int,NonStringSequence)
    False
    >>> isinstance(1,NonStringSequence)
    False
    >>> isinstance(["a"],NonStringSequence)
    True
    >>> issubclass(list,NonStringSequence)
    True
    >>> isinstance("a",NonStringSequence)
    False
    >>> isinstance(unicode('abc'),NonStringSequence)
    False
    >>> isinstance(iter("a"),NonStringSequence)
    False
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
        #__iter__ from collections.Sequence
        i = 0
        try:
            while True:
                v = self[i]
                yield v
                i += 1
        except IndexError:
            return
    def __contains__(self, value):
        for v in self:
            if v == value:
                return True
        return False
    def __reversed__(self):
        for i in reversed(range(len(self))):
            yield self[i]
    def index(self, value):
        for i, v in enumerate(self):
            if v == value:
                return i
        raise ValueError
    def count(self, value):
        return sum(1 for v in self if v == value)
NonStringSequence.register(tuple)
NonStringSequence.register(xrange)





#--------------------------------------------------------------------
#    'One-Trick Pony' Abstract Classes
#--------------------------------------------------------------------
class Indexed(object):
    """A 'One-Trick Pony' class for __getitem__. 
    Similar to collections: Iterable, Sized, Hashable, etc. 
    """
    __metaclass__ = abc.ABCMeta
    __slots__ = ()
    @abc.abstractmethod
    def __getitem__(self, key):
        raise KeyError
    @classmethod
    def __subclasshook__(cls, subklass):
        if cls is Indexed:
            if rcore._hasattr(subklass, "__getitem__"):
                return True
        return NotImplemented



class Associative(object):
    '''
    Abstract Base Class for objects which are Iterable, and respond to 
    item-retreival.
    
    Importantly, this indicates objects on which the following generic
        iterator functions can operate:
        pairs(),elements(),indexes()

    >>> isinstance({},Associative)
    True
    >>> isinstance([],Associative)
    True
    >>> isinstance("",Associative)
    False
    >>> issubclass(int,Associative)
    False
    >>> from collections import defaultdict
    >>> issubclass(defaultdict,Associative)
    True
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
            _has = lambda name: rcore._hasattr(subklass,name)
            if _has("__getitem__") and _has("__iter__"):
                return True
        return NotImplemented



#NOTE: I have read that ABCs should generally NOT have both __subclasshook__ and
#    non-abstract methods.
#    .... for some reason's I truly don't recall
class Of(object):
    '''
    ----------------
    @todo: Check if OUTER is an iterator
        @todo: develop plan for handling OUTER Iterator's
        --> 'Promise' wrapper: wraps iterator, and applies 
            isinstance() check before yielding in iter
        Example of Class-Wrapper:
        http://code.activestate.com/recipes/577555-object-wrapper-class/
        
        def promise(iterator,innertype):
            """
            @todo: Allow this to more cleanly wrap the Iterator
                IE copy the names etc
            """
            
            class Promise(collections.Iterator):
                def __getattr__(self,attr):
                    if attr == 'next':
                        return self.next()
                    elif attr == '__iter__':
                        return self.__iter__()
                    else:
                        return iterator.__getattr__(attr)
                def __iter__(self):
                    print("In iter()")
                    for elm in iter(iterator):
                        assert(isinstance(elm,innertype)), (
                            "{0} is not instance of {1}".format(elm,innertype)
                        )
                        yield elm
                    
            return Promise()
        
    #Simple container check
    >>> isinstance([1, 2, 3], Of(list, int))
    True
    >>> isinstance(['a','b'], Of(collections.Sequence,basestring))
    True
    
    #How to check nested containers
    >>> mytuple = (['one', 'two'], ('three', 'four', 'five'))
    >>> Iter_Of_Strs = Of(NonStringIterable, basestring)
    >>> Tuple_Of_Iter_Of_Strs = Of(tuple, Iter_Of_Strs)
    >>> isinstance(mytuple, Iter_Of_Strs)
    False
    >>> isinstance(mytuple, Tuple_Of_Iter_Of_Strs)
    True
    
    #Mappings - inner type check is against the VALUES - not keys
    #    Since keys are *nearly* always strings.
    >>> isinstance({'a':1},Of(collections.Mapping,int))
    True
    >>> isinstance({'a':'a'},Of(collections.Mapping,int))
    False
    >>> isinstance({'a':'a'},Of(collections.Mapping,basestring))
    True
    '''
    __metaclass__ = abc.ABCMeta
    def __new__(cls, outer, inner):
        '''cls: this class. the metaclass Of()'''

        #[] Validation
        #outer/inner should be containers of types
        #Ensure outer/inner are iterable, nonmutable sequences
        outer = rcore.ensure_tuple(outer)   
        inner = rcore.ensure_tuple(inner)
        
        assertklass(outer,NonStringIterable)
        for o_type in outer:
            assert(isinstance(o_type, type)), "All outer types must be types."
            assert(issubclass(o_type, NonStringIterable)), (
                "All outer types should be NonStringIterables")
        assertklass(inner,NonStringIterable)
        for i_type in inner:
            assert(isinstance(i_type, type)), (
                "All inner types must be types. {0}".format(itype))

        #[] Build Names
        try:
            inner_name = cls._parse_name(inner[0].__name__)
            outer_name = cls._parse_name(outer[0].__name__)
            new_name = '{0}_Of_{1}s'.format(outer_name, inner_name)
        except AttributeError as exc:
            #Primarily if inner[0]/outer[0] are missing .__name__
            new_name = 'XOfYs'

        class new_class(object):
            __metaclass__ = abc.ABCMeta
            outer_types = outer
            inner_types = inner
            @classmethod
            def __instancecheck__(cls, obj):
                assert(isinstance(obj, NonStringIterable))

                #[] Check Outer Types
                if not isinstance(obj, cls.outer_types):
                    return False
                
                
                #[] Check Inner Types
                #@todo: for obj isa Mappings, have the inner type check,
                #    check VALUES and not KEYS
                #    elements() --> get values, not keys for dict
                
                #if not all(
                #    isinstance(elm, cls.inner_types)
                #    for elm in rcore.elements(obj)
                #    ):
                isall = lambda seq: all(map(isa(cls.inner_types),seq))
                if not isall( rcore.elements(obj) ):
                    return False
                
                #[] Nothing Triggered --> True
                return True
                #return check_instance_oi(obj, cls.outer_types, cls.inner_types)
        new_class.__name__ = new_name
        return new_class
    @classmethod
    def _parse_name(cls, instring, maxsz=20):
        outstring = re.sub('[\W_]+', '', instring)
        if not outstring[0].isupper():
            outstring = outstring[0].upper() + outstring[1:]
        if len(outstring) > maxsz: #limit size
            outstring = outstring[:maxsz]
        return outstring

def is_of(obj,inner,outer):
    #@todo: rewrite to allow multiple inner and outer
    
    assert(isinstance(obj,collections.Iterable))
    #checking inner exhausts iterator
    assert(not isinstance(obj,collections.Iterator))
    assert(isinstance(outer,type))
    assert(issubclass(outer,collections.Iterable))
    assert(isinstance(inner,type))
    
    if not isinst(obj,inner):
        return False
    if not all(isinst(elm,outer) for elm in obj):
        return False
    return True



class MinimalOf(object):
    #Same idea as Of() - but just pseudocode to illustrate the concept.
    __metaclass__ = abc.ABCMeta
    def __new__(cls, outer, inner):
        #Ensure outer/inner are iterable, nonmutable sequences
        outer = rcore.ensure_tuple(outer)   
        inner = rcore.ensure_tuple(inner)

        class new_class(object):
            __metaclass__ = abc.ABCMeta
            outer_types = outer
            inner_types = inner
            @classmethod
            def __instancecheck__(cls, obj):
                if not isinstance(obj, cls.outer_types):
                    return False
                if not all( isinstance(elm, cls.inner_types) for elm in obj):
                    return False
                return True
        new_class.__name__ = '{0}_Of_{1}s'.format(
            parse_name(inner[0].__name__),
            parse_name(outer[0].__name__))
        return new_class
    

#==============================================================================
#        Ontology-Related Convience
#==============================================================================
def handle_klasses(klasses):
    if klasses == None:
        return klasses
    elif isinstance(klasses,(list,tuple)):
        #return tuple(handle_elm(elm) for elm in klasses)
        return tuple(klasses)
    else:
        #return tuple([handle_elm(klasses)])
        return tuple([klasses])
        

def assertklass(obj,isklasses=None,notklasses=None,msg=None):
    """
    Type checking use-case for assert
    uses: handle_klasses(), isinst()
    ----
    assertklass(obj,isklasses=None,notklasses=None,msg=None) -> bool
    -----
    """
    
    #[] Validation - ignoring asserts etc for now
    
    def typenames(klasses):
        return ', or '.join(
            klass.__name__ for klass in klasses
        )
    def construct_message(obj,handled_is,handled_not):
        msg = "'{0}' object should".format(type(obj).__name__)
        
        if isklasses != None:
            msg += " be instance of ({0})".format(
                typenames(handled_is)
            )
            
        if notklasses != None:
            if isklasses != None:
                msg += " and"
            msg += " not be instance of ({0})".format(
                typenames(handled_not)
            )
        return msg
            
    #[] Validation - Formatting
    handled_is = handle_klasses(isklasses)
    handled_not = handle_klasses(notklasses)
    
    if isinst(obj,isklasses,notklasses):
        return
    else:        
        #[] Construct message
        if msg == None:
            msg = construct_message(obj,handled_is,handled_not)
        
        raise TypeError(msg)
        #raise AssertionError(msg)

def isinst(obj,isklasses=None,notklasses=None):
    """
    isinst(obj,isklasses=None,notklasses=None) -> bool
    -----
    
    >>> obj = object()
    >>> isinst(obj,isklasses=object,notklasses=type(None))
    True
    >>> non = None
    >>> isinst(non,isklasses=(object,),notklasses=type(None))
    False

    >>> isinst('mystr',[basestring,type(None)],notklasses=[int,unicode])
    True
    >>> isinst(None,[type(None),int],notklasses=(basestring,))
    True
    
    >>> isinst((1,2,3),basestring)
    False
    >>> isinst((1,2,3),(collections.Sequence,type(None)))
    True
    >>> isinst((1,2,3),(collections.Sequence,type(None)),tuple)
    False
    >>> isinst("asda",str)
    True
    >>> isinst(unicode("asda"),basestring,str)
    True
    >>> isinst("asda",basestring,str)
    False
    >>> isinst(['a',1,'b'],NonStringSequence)
    True
    
    
    """
    #[] Validation - ignoring asserts etc for now
    #iscklasses/notklasses - Of(Sequence,types) or None
    handled_is = handle_klasses(isklasses)
    handled_not = handle_klasses(notklasses)
    
    if isklasses != None:
        obj_is  = isinstance(obj,handled_is)
    else:
        obj_is  = True
    
    if notklasses != None:
        obj_not = isinstance(obj,handled_not)
    else:
        obj_not = False
    
    return obj_is and not obj_not
isklass = isinst


def isa(klass):
    """Pure functional-style syntactic sugar for isinstance(,klass).
    >>> myvars = ["21","askl",unicode("name"),123,"A B C"]
    >>> map(isa(basestring),myvars)
    [True, True, True, False, True]
    """
    @functools.wraps(isinstance)
    def wrapper(value):
        return isinstance(value,klass)
    return wrapper


class Inverted(object):
    """Metaclass to identify inverted klasses and types.
    
    >>> isinstance("aa",Inverted(basestring))
    False
    >>> isinstance(1,Inverted(basestring))
    True
    >>> isinstance(unicode('name'),Inverted(basestring))
    False
    >>> isinstance({},Inverted(collections.Mapping))
    False
    >>> isinstance({},Inverted(collections.Sequence))
    True
    
    >>> isinstance(Inverted(list),Inverted)
    False
    >>> issubclass(Inverted(list),Inverted)
    True
    
    >>> isinstance([],Inverted(Inverted(list)))
    True
    >>> issubclass(dict,Inverted(Inverted(collections.Mapping)))
    True
    >>> issubclass(str,Inverted(Inverted(collections.Mapping)))
    False
    
    >>> isinstance({},Inverted(Inverted(Inverted(dict))))
    False
    >>> isinstance([],Inverted(Inverted(Inverted(dict))))
    True
    
    >>> class MyClass(object):  pass
    >>> isinstance(MyClass(),Inverted(MyClass))
    False
    >>> isinstance(None,Inverted(MyClass))
    True
    >>> isinstance(MyClass(),Inverted(Inverted(MyClass)))
    True
    """
    __metaclass__ = abc.ABCMeta
    @classmethod
    def __subclasshook__(cls, subklass):
        if cls is Inverted:
            return cls in subklass.__mro__
        return NotImplemented
    def __new__(cls,base_klass):        
        assertklass(base_klass,type)
        
        if issubclass(base_klass,Inverted):
            return base_klass.base
        else:
            base_name = base_klass.__name__        
            class InvertedKlass(Inverted):
                __metaclass__ = abc.ABCMeta
                #_base_klass = base_klass
                base = base_klass
                @classmethod
                def __subclasshook__(cls, subklass):
                    is_base = issubclass(subklass,cls.base)
                    if isinstance(is_base,bool):
                        return not is_base
                    #Ex. is_base == NotImplemented
                    else:
                        return is_base
            InvertedKlass.__name__ = "Not"+base_name
            return InvertedKlass
Inv = Inverted





if __name__ == "__main__":
    import doctest
    doctest.testmod()
    
    def doc_check(func):
        """Use to check specific functions, or get more information
        on why they failed the doctest."""
        doctest.run_docstring_examples(func,globals())

    import pdb
    pdb.set_trace()
    print('--')