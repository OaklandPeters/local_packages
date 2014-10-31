from _abcoll import *
import types
import abc
import functools


MethodWrapper = type(list().__add__)

#@TODO: create a 'demote' function, which is the inverse companion to ABCView
#    ABCView  --> more general object, with less methods
#    'demote' --> less general object, with more methods  (ie should keep functions of obj)
#@TODO: create a 'wrap' function, companion to ABCView


#Note... I'm actually building a type of 'StrictEnsure'/'StrictView'
#    which has the properties of a Mapping, etc, but affects an underlying
#    object of a different type
#    ... not unlike MappingView, ItemsView, etc



#    Essentially a TypeRestriction(), 'type promotion' in C-terms
def ABCView(vog):
    """Create class which is the intersection of 'obj', with
    the abstract methods and properties of 'vog'; then inherits
    from 'vog' -- receiving its Mixin methods.    
    
    
    >>> obj = [0,1,2]
    >>> SeqView = ABCView(Sequence)
    >>> seq     = SeqView(obj)
      
    #Confirm that it DOES NOT have non-Sequence methods from list
    #    Such as .append (which list has, but Sequence does not)
    >>> seq.append(3)
    Traceback (most recent call last):
    AttributeError: 'SequencePromotion' object has no attribute 'append'
    
    #Observe: Changes to mutable view change the original object
    >>> MSeqView = ABCView(MutableSequence)
    >>> mseq     = MSeqView(obj)
    >>> mseq.append(3)
    >>> mseq
    [0, 1, 2, 3]
    >>> obj
    [0, 1, 2, 3]
    """
    assert(isinstance(vog,abc.ABCMeta)), "vog must be an abstract class."
    def init(self,obj):
        #@todo: self.__obj = weakref.weakref(obj)
        vog = self.__vog
        assert(isinstance(obj,vog)), str.format(
            "'obj' does not meet {0}.",vog.__name__)
        assert(not isinstance(obj,type)), str.format(
             "'obj' is not an instance.")
        self.__obj = obj
    redirector = lambda self: self.__obj
    
    
    
    new_attrs = {
        '__vog':vog,
        '__init__':init,
        #'__init__':lambda self,obj: setattr(self,'__obj',obj)
    }
    
    for name in get_abstracts(vog):
        vog_attr = getattr(vog,name)
        if isinstance(vog_attr,types.MethodType):
            new_attrs[name] = binding_wrapper(name,redirector)
        #abstractproperty ...
        else:   
            new_attrs[name] = property(lambda self: getattr(self.__obj,name))
    
    #Tentative: Add repr
    if hasattr(vog,'__repr__'):
        new_attrs['__repr__'] = binding_wrapper('__repr__',redirector)
    
            
    new_name = vog.__name__+'Promotion'
    #new_bases: will ensure that the new object inherits mixin methods from VOG
    new_bases = (vog,)
    new_cls = type(new_name,new_bases,new_attrs)
    return new_cls



#==============================================================================
#    Local Utility Functions
#==============================================================================
def binding_wrapper(name,redirector=None):
    """
    @binding_wrapper()
    """
    if redirector == None:
        redirector = lambda self: self
    assert(isinstance(redirector,Callable)), "Redirector not Callable."
        
    def wrapped(self,*args,**kwargs):
        #obj = self.__obj
        obj = redirector(self)
        attr = getattr(obj,name)
        return attr(*args,**kwargs)
    return wrapped
#    if wraps == None:
#        return wrapped
#    elif isinstance(wraps,Callable):
#        return functools.wraps(wraps)(wrapped)
#    else:
#        raise TypeError("Invalid 'wraps' of type: "+type(wraps).__name__)


def is_abstract(func):
    try:
        return func.__isabstractmethod__
    except AttributeError:
        return False
    
def get_abstracts(vog):
    """Where 'vog' is an abstract base class
    >>> 
    >>> get_abstracts(Sequence)
    ['__getitem__', '__len__']
    """
    return [
        name
        for name in dir(vog)
        if is_abstract(getattr(vog,name))
    ]
#    abstracts = []
#    for klass in vog.__mro__:
#        try:
#            for method in klass.__abstractmethods__:
#                abstracts.append(method)
#        except AttributeError:
#            pass
#    #make unique
#    return list(set(abstracts))


def OldABCView(obj,vog):
    """Create class which is the intersection of 'obj', with
    the abstract methods and properties of 'vog'; then inherits
    from 'vog' -- receiving its Mixin methods.
    
    >>> mylist = ['a','b','c']
    >>> MyView = OldABCView(mylist,Sequence)
    >>> myinst = MyView()
    >>> myinst.index('b')
    1
    >>> myinst.append('d')
    Traceback (most recent call last):
    AttributeError: 'SequenceWrapper' object has no attribute 'append'
    """
    assert(isinstance(obj,vog)), "Does not meet {0}.".format(vog.__name__)
    assert(not isinstance(obj,type)), "obj is not an instance."
    assert(isinstance(vog,type)), "vog is not a type."
    #??? --> assert(isinstance(vog,abc.ABCMeta))
    
    new_attrs = {'__vog':vog,'__obj':obj}
    for name in get_abstracts(vog):
        attr = getattr(obj,name)
        if isinstance(attr,types.MethodType):
            #functools.partial(attr,obj)
            #~ bind function to 'obj' as 'self'
            new_attrs[name] = lambda *args,**kwargs: attr(obj,*args,**kwargs)
        #abstractproperty ...
        else:   
            new_attrs[name] = attr
    new_name = vog.__name__+'Wrapper'
    new_bases = (vog,)
    new_cls = type(new_name,new_bases,new_attrs)
    return new_cls










    

def demote(obj,vog):
    """Type 'demotion': return an object, based on obj, but which bears the
    mixin methods of vog, if possible.
    
    Note: I am using type 'promotion'/'demotion' in the OPPOSITE sense that
    they are used in languages like C. In those languages:
        'promotion'--> more general type (hence less methods)
        'demotion' --> less general type (hence more methods)
    
    
    """
    assert(isinstance(vog,type)), "vog is not a type."
    #??? --> assert(isinstance(vog,abc.ABCMeta))
    assert(isinstance(obj,vog)), "Does not meet {0}.".format(vog.__name__)
    assert(not isinstance(obj,type)), "obj is not an instance."
    
    
    #? How to get only the mixin methods?
    #IE not things like __abc_negative_cache, etc
    #... I basically want to create an object which inherits from obj, then vog
    #  But I cannot do this, since 'obj' is an instance
    #
    #Perhaps...
    #    create a new custom class, which 

def promote(obj,vog):
    """Type 'promotion': return restrictive subset of obj which 
    meets vog (an ABC).
    
    Note: I am using type 'promotion'/'demotion' in the OPPOSITE sense that
    they are used in languages like C. In those languages:
        'promotion'--> more general type (hence less methods)
        'demotion' --> less general type (hence more methods)
    """
    view = ABCView(vog)
    inst = view(obj)
    return inst
    
         
#==============================================================================
#    Thoughts / In-Development
#==============================================================================
def Restrict(obj,vog):
    return ABCView(vog)(obj)
def Ensure(obj,vog,wrap=None):
    """Not actually related to ABCView."""
    if isinstance(obj,vog):
        return obj
    else:
        pass


def Mapper(function, obj, category, wrap=tuple):
    """
    Map (function,obj) ---under criteria of---> Category
    Map function, onto obj, under the iteration criteria of Category
    
    Mapper(function,obj,category)
    
    ----
    isa = lambda elm: isinstance(obj,elm)
    
    Mapper(pos, isa,NonStringSequence)
        if isinstance(pos, NonStringSequence):
            return [isa(elm) for elm in pos]
        else:
            return [isa(pos)]
        
    """
    if isinstance(obj,category):
        view = ABCView(category)(obj)    
    else:
        view = ABCView(category)(wrap(obj))
    
    return map(function,view)

#==============================================================================
#        Tests
#==============================================================================

import unittest
class ConversionTests(unittest.TestCase):
    def setUp(self):
        class defaultlist(list):
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
            def default(self,func):
                """func: ex. initializers: int,list, etc."""
                self._default = func
        self.defaultlist = defaultlist
        deflist = defaultlist(list)
        deflist[3] = 'a'
        self.deflist = deflist
        
        
    def test_basic(self):
        obj = self.deflist
        vog = Sequence
        MyView = ABCView(vog)
        myinst = MyView(obj)
        
        self.assertEqual(myinst.__getitem__(3),obj.__getitem__(3))
        self.assertEqual(myinst.index('a'),3)
        self.assertEqual(str(list(myinst)),"[[], [], [], 'a']")
        
        #append is part of defaultlist, but not of Sequence
        #    hence, myinst.append should not be valid
        self.assertRaises(AttributeError,lambda: myinst.append('b'))



    


#==============================================================================
#    Crude Development
#==============================================================================
def redirecting_wrapper(name,redirector=None):
    """
    """
    if redirector == None:
        redirector = lambda self: self
    assert(isinstance(redirector,Callable)), "Redirector not Callable."
        
    def wrapped(self,*args,**kwargs):
        try:
            #obj = self.__obj
            obj = redirector(self)
        except Exception as exc:
            print(name)
            print(exc)
            import pdb; pdb.set_trace()
            print('----')
            raise exc

            
        attr = getattr(obj,name)
        if callable(attr):
            return attr(*args,**kwargs)
        else:
            return attr
    return wrapped

def ClassView(obj):
    """Metaclass for copying and redicting to obj.
    
    >>> obj = [1,2,3]
    >>> view = ClassView(obj)
    >>> inst = view(obj)
    >>> inst.append(4)
    >>> inst
    [1, 2, 3, 4]
    >>> obj
    [1, 2, 3, 4]

    """
    def init(self,obj):
        #self.__obj --> tries to access self.__setattr__ --> self.__obj.__setattr__
        #    BEFORE it actually exists.
        super(type(self),self).__setattr__('__obj',obj)
        
    redirector = lambda self: self.__obj    
    new_attrs = {}
    new_attrs['__class_template'] = obj,
    new_attrs['__init__'] = init
    new_attrs['__redirector'] = redirector
    
    
    #Do not wrap these methods, and allow them to be inherited
    ignore = ['__new__','__init__','__getattr__','__getattribute__']
    
    for name in dir(obj):
        attr = getattr(obj,name)
        if name in ignore:
            continue
        else:
            new_attrs[name] = redirecting_wrapper(name,redirector)
            
    parent = type(obj)
    new_name = parent.__name__+'ClassView'
    #new_bases: will ensure that the new object inherits mixin methods from VOG
    new_bases = (parent,)
    new_cls = type(new_name,new_bases,new_attrs)
    return new_cls


def ABCDemotion(obj,vog):
    """ClassView is similar to what I want the demotion process to do.
    It creates an instance, which:
    (1) has some methods which redirect to another object
    (2) inherits other methods from parent(s)
    
    A demotion is very similar (inheriting from the obj passed in), EXCEPT:
    It should also receive a 'vog' which provides methods, if they do not already
    exist in the obj.
    
    #this doesn't really test much, since list already has all arguments from Sequence
    >>> obj = [1,2,3]
    >>> view = ABCDemotion(obj,Sequence)
    >>> inst = view(obj)
    >>> inst.append(4)
    >>> inst
    [1, 2, 3, 4]
    >>> obj
    [1, 2, 3, 4]
    
    
    #This does test things, since MutableSequence has methods tuple does not
#    obj = (1,2,3)
#    view = ABCDemotion(obj,MutableSequence)
#    inst = view(obj)
#    inst.append(4)
    """
    assert(isinstance(vog,abc.ABCMeta)), "vog must be an abstract class."
    assert(isinstance(obj,vog)), "obj is not an instance of vog: "+vog.__name__
    
    def init(self,obj):
        #self.__obj --> tries to access self.__setattr__ --> self.__obj.__setattr__
        #    BEFORE it actually exists.
        super(type(self),self).__setattr__('__obj',obj)
        
    redirector = lambda self: self.__obj    
    new_attrs = {}
    new_attrs['__class_template'] = obj,
    new_attrs['__init__'] = init
    new_attrs['__redirector'] = redirector
    
    
    #Do not wrap these methods, and allow them to be inherited
    ignore = ['__new__','__init__','__getattr__','__getattribute__']
    
    def handle(name,attr):
        if name in ignore:
            continue
        else:
            new_attrs[name] = redirecting_wrapper(name,redirector)
    
    for name in dir(obj):
        attr = getattr(obj,name)
        handle(name,attr)
#        if name in ignore:
#            continue
#        else:
#            new_attrs[name] = redirecting_wrapper(name,redirector)
            
    for name in dir(vog):
        if name in new_attrs:
            continue
        else:
            attr = getattr(vog,name)
            handle(name,attr)
            
    parent = type(obj)
    new_name = parent.__name__+'ClassView'
    #new_bases: will ensure that the new object inherits mixin methods from VOG
    new_bases = (parent,)
    new_cls = type(new_name,new_bases,new_attrs)
    return new_cls



#Make a class which satisfies MutableSequence, but does not have its Mixins
class MySequence(Sequence):
    def __init__(self,*args):
        self.data = args
    def __getitem__(self,key):
        return self.data[key]
    def __len__(self):
        return len(self.data)
    def __iter__(self):
        return iter(self.data)
    def __setitem__(self,key,value):
        self.data[key] = value
    def __delitem__(self,key):
        del self.data[key]
    def insert(self,index,value):
        self.data.insert(index,value)
    #------- Extra functions not part of MutableSequence
    def sum(self):
        accumulator = 0
        for elm in self:
            accumulator += int(elm) 

#!! Idea for a decorator:
#    Makes a function redirect to another object.
#@redirect(lambda self: self.data)
#def __getitem__(*args,**kwargs)
#    --> (self.data).__getitem__(*args,**kwargs)
#def redirect(redirector):
#    """
#    @redirect(lambda self: self.data)
#    def __getitem__(self,key):    pass
#
#    __getitem__ = redirect(lambda self:self.data)()
#    """
#    assert(callable(redirector)), "Redirector is not callable."
#    def outer(method=None):
#        name = method.__name__ if hasattr(method,'__name__') else 'lambda'
#        def wrapped(self,*args,**kwargs):
#            obj = redirector(self)
#            attr = getattr(obj,name)
#            #Following statement may not be necessary:
#            if callable(attr):
#                return attr(*args,**kwargs)
#            else:
#                return attr

obj = MySequence(1,2,3)
vog = MutableSequence


if __name__ == "__main__":
    import doctest
    import unittest
    doctest.testmod()
    
    def doc_check(func):
        """Use to check specific functions, or get more information
        on why they failed the doctest."""
        doctest.run_docstring_examples(func,globals())
    
    
    import pdb
    pdb.set_trace()
    print('---')
     
    unittest.main()