import inspect




class Property(object):
    """Python's property() decorator, but also allows inputs to be specified
    via a class, for more compact input. For example:
    @Property
    class data(object):
        def getter(self):
            return self._data
        def setter(self, value):
            self._data = value
        def deleter(self):
            del self._data
        
    
    @TODO: Allow the function names for the class to be specified as
        either 'fget'/'getter', 'fset'/'setter', 'fdel'/'deleter'
    @TODO: Consider having the names on the class be:
        '_get', '_set', '_del' - so that pylint doesn't complain about them.
    """
    def __new__(cls, *fargs, **fkwargs):
        arguments = cls.validate(*fargs, **fkwargs)
        return property(*arguments)
    @classmethod
    def validate(self, *fargs, **fkwargs):
        if len(fargs)==1 and len(fkwargs)==0:
            if inspect.isclass(fargs[0]):
                return self._validate_from_class(fargs[0])
        return self._validate_from_args(*fargs, **fkwargs)
    @classmethod
    def _validate_from_args(self, fget=None, fset=None, fdel=None, doc=None):
        """Process arguments received conventionally."""
        if doc is None and fget is not None:
            doc = fget.__doc__
        return fget, fset, fdel, doc
    @classmethod
    def _validate_from_class(self, klass):
        fget= _tryget(klass, 'getter')
        fset=_tryget(klass, 'setter')
        fdel=_tryget(klass, 'deleter')
        doc=_tryget(klass, '__doc__')
        if doc is None and fget is not None:
            doc = fget.__doc__
        return fget, fset, fdel, doc





class VProperty(object):
    """Enchanced Python property, supporting 
    
    @TODO: Allow the function names for the class to be specified as
        either 'fget'/'getter', 'fset'/'setter', 'fdel'/'deleter', 'fval'/'validator'
    @TODO: Allow additional methods to be provided on a decorated class. Essentially
        anything not causing a conflict. basically I would like the class defined in
        the decorator to be in the method-resolution order for the new vproperty descriptor.
        (* complication: need to rename getter/setter/deleter/validator to fget/fset etc)
    @TODO: Consider having the names on the class be:
        '_get', '_set', '_del', '_validate' - so that pylint doesn't complain about them.
    
    """
    def __init__(self, *fargs, **fkwargs):
        """Check if used as a decorator for a class, or if used
        conventionally.
        """
        arguments = self.validate(*fargs, **fkwargs)
            
        (self.fget,
         self.fset,
         self.fdel,
         self.fval,
         self.__doc__) = arguments
         
    def validate(self, *fargs, **fkwargs):
        if len(fargs)==1 and len(fkwargs)==0:
            if inspect.isclass(fargs[0]):
                return self._validate_from_class(fargs[0])
        return self._validate_from_args(*fargs, **fkwargs)
    def _validate_from_args(self, fget=None, fset=None, fdel=None, fval=None, doc=None):
        """This is basically a validation function. Consider renaming?"""
        if doc is None and fget is not None:
            doc = fget.__doc__
        return fget, fset, fdel, fval, doc
    def _validate_from_class(self, klass):
        fget=_tryget(klass, 'getter')
        fset=_tryget(klass, 'setter')
        fdel=_tryget(klass, 'deleter')
        fval=_tryget(klass, 'validator')
        doc=_tryget(klass, '__doc__')
        if doc is None and fget is not None:
            doc = fget.__doc__
        return fget, fset, fdel, fval, doc
    #----- Descriptors
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        if self.fget is None:
            raise AttributeError("unreadable attribute")
        return self.fget(obj)
    def __set__(self, obj, value):
        if self.fset is None:
            raise AttributeError("can't set attribute")
        if self.fval is not None: #Validate, if possible
            value = self.fval(obj, value)
        self.fset(obj, value)
#         if self.fval is None:
#             self.fset(obj, value)
#         else:
#             self.fset(obj, self.fval(obj, value))
    def __delete__(self, obj):
        if self.fdel is None:
            raise AttributeError("can't delete attribute")
        self.fdel(obj)
    #----- Decorators
    def getter(self, fget):
        return type(self)(fget, self.fset, self.fdel, self.fval, self.__doc__)
    def setter(self, fset):
        return type(self)(self.fget, fset, self.fdel, self.fval, self.__doc__)
    def deleter(self, fdel):
        return type(self)(self.fget, self.fset, fdel, self.fval, self.__doc__)
    def validator(self, fval):
        return type(self)(self.fget, self.fset, self.fdel, fval, self.__doc__)



def SimpleProperty(klass):
    """*very* simple way to define a property via a nested class.
    Basically just instanciate the class. Works as a decorator
    
    class MyClass(object):
    def __init__(self, foo, bar):
        self.foo = foo
        print("I see self.bar == "+str(self.bar))
        self.bar = bar
    @SimpleProperty
    class bar(property):
        def __get__(self, obj, objtype=None):
            if obj is None: #Necessary for when MyClass.bar is called on the class
                return self
            if not hasattr(obj, '_bar'):
                obj._bar = self._default(obj)
            return obj._bar
        def __set__(self, obj, value):
            obj._bar = value
        def __del__(self, obj):
            del obj._bar
        def _default(self, obj):
            return "default bar property"

    myinst = MyClass('f','b') #will print 'default bar property'
    print(myinst.foo, myinst.bar) #will print '
    print(dir(MyClass.bar)) # test - confirm this tricky part works correctly
    
    @todo improved version - Works like VProperty, in that you don't specify
        __get__, __set__, __del__ directly
        ... also provides the decorators: getter, setter, deleter
        ... use fget/_get, fset/_set, fdel/_del, fval/_val, fdef/_def
        ... PROBABLY mark _val and _def as classmethods automatically
            --> through classmethods on the parent
    @todo Write a parent class for the property to inherit
    """
    #hasany = lambda sequence: any([hasattr(klass, elm) for elm in sequence])
    #assert(hasany('__get__','__set__','__del__'))
    #        -OR-
    #assert(issubclass(klass, property))
    return klass()


#==============================================================================
#    Local Utility Sections
#==============================================================================
def _tryget(klass, attr, default=None):
    """
    Note: object.__getattribute__(klass, attr), returns a subtly
    different object than getattr(klass, attr).
    The first will return a function, and the second an unbound method.
    """
    try:
        return object.__getattribute__(klass, attr)
    except AttributeError:
        return default