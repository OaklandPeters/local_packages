import collections, functools, abc
import types
import functools
#-----
from .. import rich_core



#==============================================================================
#        Decorators
#==============================================================================
def memoize(obj):
    """Decorator.
    Memoizing/cacheing function that works on functions, methods, or 
    classes, and exposes the cache publicly.
    """
    cache = obj.cache = {}

    @functools.wraps(obj)
    def memoizer(*args, **kwargs):
        key = str(args) + str(kwargs)
        if key not in cache:
            cache[key] = obj(*args, **kwargs)
        return cache[key]
    return memoizer

def deprecated(func):
    '''Decorator.
    Used to mark functions as deprecated, generating a warning Exception
    when the function is called.
    
    Use this to supress warnings:
        import warnings
        warnings.simplefilter("ignore")
    Or this to make each appear only once:
        warnings.simplefilter(
            "once",
            category=(PendingDeprecationWarning, DeprecationWarning)
        )
    '''
    @functools.wraps(func)
    def new_func(*args, **kwargs):
        warnings.warn(
            "Call to deprecated function {0}.".format(func.__name__),
            category=DeprecationWarning)
        return func(*args, **kwargs)
    new_func.__name__ = func.__name__
    new_func.__doc__ = func.__doc__
    new_func.__dict__.update(func.__dict__)
    return new_func

def AtlasDispatch(function):
    """Decorator. Dispatch (iterate) on the first argument.
    If mapping --> call function on it. If NonStringSequence, call
    function on each element of the sequence. Otherwise, generate
    an error.
    
    >>> aDict = {'a':1,'b':2}
    >>> bDict = {'a':3,'b':4}
    >>> atlas = [aDict,bDict]
    
    >>> def getA(mapping): return mapping['a']
    >>> @AtlasDispatch
    ... def getB(mapping): return mapping['b']
    
    >>> AtlasDispatch(getA)(aDict)
    1
    >>> AtlasDispatch(getA)([aDict,bDict])
    [1, 3]
    >>> getB([aDict,bDict])
    [2, 4]
    
    >>> getB(2)
    Traceback (most recent call last):
    TypeError: Expected Mapping or NonStringIterable.  Found <type 'int'>
    """
    @functools.wraps(function)
    def wrapper(*args,**kwargs):
        assert(len(args) > 0), "Missing first argument."
        call = lambda elm: function(elm,*args[1:],**kwargs)
        
        if isinstance(args[0],collections.Mapping):
            return call(args[0])
            #return function(*args,**kwargs)
        elif isinstance(args[0],rich_core.NonStringIterable):
            return [
                #function(mapping,*args[1:],**kwargs)
                call(mapping)
                for mapping in args[0]
            ]
        else:
            raise TypeError(("Expected Mapping or NonStringIterable. "
                " Found {0}").format(type(args[0])))
    return wrapper

def AssociationDispatch(function):
    """Dispatch on the first argument to a function. Map the function to:
    
    Mapping           --> return dict, with function applied to values
    NonStringSequence --> return list, ~standard: map(function,*sequence)
    Atomic (others)   --> return function(object)
    
    >>> mapping  = {'a':1,'b':2}
    >>> sequence = [1,2]
    >>> atomic   = 12
    >>> iterator = (x for x in [1,2])
    >>> @AssociationDispatch
    ... def repeater(elm):    return str(elm)+str(elm)+str(elm)
    

    >>> repeater(mapping)
    {'a': '111', 'b': '222'}
    >>> repeater(sequence)
    ['111', '222']
    >>> repeater(atomic)
    '121212'
    """
    @functools.wraps(function)
    def wrapper(*args,**kwargs):
        assert(len(args) > 0), "Missing first argument."
        call = lambda elm: function(elm,*args[1:],**kwargs)
        isa = lambda klass: isinstance(args[0],klass)
        
        #if Mapping Sequence and not basestring
        if isa(collections.Mapping):
            return dict((key,call(value)) for key,value in args[0].items())
        elif isa(collections.Sequence) and not isa(basestring):
            return [call(elm) for elm in args[0]]
        else:
            return call(args[0])
    return wrapper

def IterableDispatch(function):
    """
    >>> mapping  = {'a':1,'b':2}
    >>> sequence = [1,2]
    >>> atomic   = 12
    >>> iterator = (x for x in [1,2])
    >>> @IterableDispatch
    ... def repeater(elm):    return str(elm)+str(elm)+str(elm)
    
    >>> repeater(mapping)
    ['aaa', 'bbb']
    >>> repeater(sequence)
    ['111', '222']
    >>> repeater(atomic)
    '121212'
    >>> repeater(iterator)
    ['111', '222']
    """
    @functools.wraps(function)
    def wrapper(*args,**kwargs):
        assert(len(args) > 0), "Missing first argument."
        call = lambda elm: function(elm,*args[1:],**kwargs)
        isa = lambda klass: isinstance(args[0],klass)
        
        if isa(rich_core.NonStringIterable):
            return [call(elm) for elm in args[0]]
        else:
            return call(args[0])
    return wrapper




def method_property(name):
    """
    Use to create a simple property which redirects
    >>> class Duck(object):
    ...     quack = property(*method_property("_quack"))
    ...     fly = property(*method_property("_fly"))
    >>> myDuck = Duck()
    >>> myDuck._quack = "wak"
    >>> myDuck.quack
    'wak'
    """
    def getter(self):
        return getattr(self, name)
    def setter(self, value):
        setattr(self, name, types.MethodType(value, self))
    return getter, setter

def basic_property(name):
    """Use to create a simple property which redirects to 'name'.
    >>> class Duck(object):
    ...     quack = property(*method_property("_quack"))
    ...     fly = property(*method_property("_fly"))
    >>> myDuck = Duck()
    >>> myDuck._quack = "wak"
    >>> myDuck.quack
    'wak'
    """
    def getter(self):
        return getattr(self,name)
    def setter(self,value):
        setattr(self,name, value)
    def deleter(self):
        delattr(self,name)
    return getter,setter,deleter


#--------------------------------------------------------
#    Basic Property as a Descriptor
#--------------------------------------------------------
from weakref import WeakKeyDictionary
class BasicProperty(object):
    """A descriptor that sets up basic property behavior."""
    def __init__(self, default=None):
        self.default = default
        self.data = WeakKeyDictionary()
    def __get__(self, instance, owner):
        # we get here when someone calls x.d, and d is a BasicProperty instance
        # instance = x
        # owner = type(x)
        return self.data.get(instance, self.default)
    def __set__(self, instance, value):
        # we get here when someone calls x.d = val, and d is a BasicProperty instance
        # instance = x
        # value = val
        #[] Validation would go here
        #if self.validation != None:
        #    self.validation(value)
        self.data[instance] = value
    def __delete__(self, instance):
        del self.data
        del self.default


def redirector(*args):
    """Decorator. Redirector ~ basic_property. Also an example
    of using optional arguments on decorators.
    
    >>> class MyClass(object):
    ...     url = redirector('_url')
    ...     @redirector
    ...     def html(self):
    ...         pass
    >>> mine = MyClass()
    >>> mine.url = "http://www.blah.com"
    >>> mine.url
    'http://www.blah.com'
    >>> mine.html = "<html><title>My Awesome Site</title></html>"
    >>> mine.html
    '<html><title>My Awesome Site</title></html>'
    """
    def _redirector(func):
        #@functools.wraps(func)
        def wrapper(*args,**kwargs):
            pass

    if len(args) == 1 and callable(args[0]):
        # No arguments --> this is the decorator
        # Set default values for the arguments
        def _getname(func):
            return property(*basic_property("_"+func.__name__))
        return _getname
    else:
        #Name has been supplied as argument
        name = args[0]
        return property(*basic_property(name))



class Redirector(object):
    """Variant of the redirector. Sets up a basic redirecting property,
    but much cleaner than the redirector() function.
    However... cannot be used as a function decorator (yet).
    
    Also: a good example of a basic descriptor.
    
    >>> class SQL(object):
    ...     where = Redirector('where','NANA')
    ...     def __init__(self,where_arg):
    ...         self.where = where_arg
    >>> mine = SQL('alksdjl')
    >>> mine.where
    'alksdjl'
    >>> mine.__dict__
    {'_where': 'alksdjl'}
    """
    def __init__(self, name, default=None):
        self.default = None
        rich_core.AssertKlass(name,basestring)
        self.name = name
    @property
    def rd_name(self):
        return "_"+self.name
    def __set__(self, instance, value):
        instance.__setattr__(self.rd_name,value)
    def __get__(self, instance, owner):
        return instance.__getattribute__(self.rd_name)

def validator(method):
    name = method.__name__
    @functools.wraps(method)
    def wrapped(self,value):
        if method(self,value) == False:
            raise TypeError("Invalid value for "+name)
        else:
            return value
    wrapped._validator = True
    return wrapped

def validated(cls):
    """Class decorator.
    >>> @validated
    ... class SQL(object):
    ...     def __init__(self,where,select):
    ...         #Use the validators...
    ...         self.where = self._validators['where'](self,where)
    ...         self.select = self._validators['select'](self,select)
    ...     @property
    ...     def where(self):
    ...         return self._where
    ...     @where.setter
    ...     def where(self,value):
    ...         self._where = value
    ...     @validator
    ...     def where(self,value):
    ...         return isinstance(value,basestring)
    ...     @validator
    ...     def select(self,value):
    ...         return rich_core.AssertKlass(value,basestring)
    
    >>> #Confirm that validator does not interfere with normal properties
    >>> mine = SQL('name','job')
    >>> mine.where
    'name'
    >>> thing = SQL('name',43)
    Traceback (most recent call last):
    TypeError: 'int' object should be instance of (basestring)
    >>> other = SQL(12,'job')
    Traceback (most recent call last):
    TypeError: Invalid value for where
    """
    cls._validators = {}
    original_methods = cls.__dict__.copy()
    for name, method in original_methods.iteritems():
        if hasattr(method, '_validator'):
            # Add entry to cls._validators for this method
            cls._validators[name] = method
    return cls





class OptionalDecorator(object):
    """Create your decorator as a class, and inherit from this. Override:
    wrapper: Your actual decorator. Invokes self.function(*args,**kwargs)
    __init__: Assign decorator arguments to self
    
    Error case:  a single position callable argument
    @ExampleOptionalDecorator(callable)
    def my_function(...):
    """
    __metaclass__ = abc.ABCMeta
    wrapper = abc.abstractmethod(lambda: None) 
    __init__ = abc.abstractmethod(lambda: None)
    
    def __new__(cls,*args,**kwargs):
        """
        (1) Create instance.
        (2) No arguments?--> invoke __init__/__call__ manually.
        (3) Arguments   ?--> let __init__&__call__ be invoked automatically.
        """

        self = super(cls.__mro__[1],cls).__new__(cls)
        
        if len(args) == 1 and len(kwargs) == 0 and callable(args[0]):    
            cls.__init__(self)
            return self.__call__(args[0])
        
        else:
            return self
        
    def __call__(self,function): 
        """Wrap decorator around function - but preserve binding to self"""
        self.function = function
        return functools.wraps(self.function)(
            lambda *args,**kwargs: self.wrapper(*args,**kwargs)
        )

def optional_decorator(cls):
    """OptionalDecorator, itself as a class-decorator.
    @optional_decorator
    class ExampleOptionalDeco(object):
        def __init__
        def wrapper
    """
    cls.__new__ = OptionalDecorator.__new__
    cls.__call__ = OptionalDecorator.__call__
    cls.wrapper
    cls.__init__
    return cls




class ClassProperty(property):
    """Property which is also a classmethod. Due to bugs in Python, it's setter does not work.
    http://stackoverflow.com/questions/128573/using-property-on-classmethods
    
    >>> class Foo(object):
    ...     _var = 5

    >>> @ClassProperty
    ... @classmethod
    ... def var(cls):
    ...     return cls._var

    >>> @var.setter
    ... @classmethod
    ... def var(cls, value):
    ...     cls._var = value

    >>> foo.var == 5
    True
    """
    def __get__(self, cls, owner):
        return self.fget.__get__(None, owner)()








import inspect
#Back-port of inspect.getcallargs from Python 2.7 --> 2.6
#Usage: in modifying arguments in decorators
#def deco(func):
#    def wrapper(*args,**kwargs):
#        arguments = getcallargs(func,*args,**kwargs)
#        arguments['my_arg'] = processing(arguments['my_arg'])
#        return func(**arguments)
#    return wrapper
#
#Subtle Problem:
#    This processing translates all *args --> **kwargs
#    Python adapts to this OK, since all positional args can actually
#be passed in as Keywords.
#    However.... if func is expecting vargs (*args) it will receive
#nothing in that value.
def getcallargs(func, *positional, **named):
    """Back-port of inspect.getcallargs, from Python 2.7 to Python 2.6.
    
    Get the mapping of arguments to values.

    A dict is returned, with keys the function argument names (including the
    names of the * and ** arguments, if any), and values the respective bound
    values from 'positional' and 'named'."""
    args, varargs, varkw, defaults = inspect.getargspec(func)
    f_name = func.__name__
    arg2value = {}

    # The following closures are basically because of tuple parameter unpacking.
    assigned_tuple_params = []
    def assign(arg, value):
        if isinstance(arg, str):
            arg2value[arg] = value
        else:
            assigned_tuple_params.append(arg)
            value = iter(value)
            for i, subarg in enumerate(arg):
                try:
                    subvalue = next(value)
                except StopIteration:
                    raise ValueError('need more than %d %s to unpack' %
                                     (i, 'values' if i > 1 else 'value'))
                assign(subarg,subvalue)
            try:
                next(value)
            except StopIteration:
                pass
            else:
                raise ValueError('too many values to unpack')
    def is_assigned(arg):
        if isinstance(arg,str):
            return arg in arg2value
        return arg in assigned_tuple_params
    if inspect.ismethod(func) and func.im_self is not None:
        # implicit 'self' (or 'cls' for classmethods) argument
        positional = (func.im_self,) + positional
    num_pos = len(positional)
    num_total = num_pos + len(named)
    num_args = len(args)
    num_defaults = len(defaults) if defaults else 0
    for arg, value in zip(args, positional):
        assign(arg, value)
    if varargs:
        if num_pos > num_args:
            assign(varargs, positional[-(num_pos-num_args):])
        else:
            assign(varargs, ())
    elif 0 < num_args < num_pos:
        raise TypeError('%s() takes %s %d %s (%d given)' % (
            f_name, 'at most' if defaults else 'exactly', num_args,
            'arguments' if num_args > 1 else 'argument', num_total))
    elif num_args == 0 and num_total:
        if varkw:
            if num_pos:
                # XXX: We should use num_pos, but Python also uses num_total:
                raise TypeError('%s() takes exactly 0 arguments '
                                '(%d given)' % (f_name, num_total))
        else:
            raise TypeError('%s() takes no arguments (%d given)' %
                            (f_name, num_total))
    for arg in args:
        if isinstance(arg, str) and arg in named:
            if is_assigned(arg):
                raise TypeError("%s() got multiple values for keyword "
                                "argument '%s'" % (f_name, arg))
            else:
                assign(arg, named.pop(arg))
    if defaults:    # fill in any missing values with the defaults
        for arg, value in zip(args[-num_defaults:], defaults):
            if not is_assigned(arg):
                assign(arg, value)
    if varkw:
        assign(varkw, named)
    elif named:
        unexpected = next(iter(named))
        if isinstance(unexpected, unicode):
            unexpected = unexpected.encode(sys.getdefaultencoding(), 'replace')
        raise TypeError("%s() got an unexpected keyword argument '%s'" %
                        (f_name, unexpected))
    unassigned = num_args - len([arg for arg in args if is_assigned(arg)])
    if unassigned:
        num_required = num_args - num_defaults
        raise TypeError('%s() takes %s %d %s (%d given)' % (
            f_name, 'at least' if defaults else 'exactly', num_required,
            'arguments' if num_required > 1 else 'argument', num_total))
    return arg2value


class DecoratorABC(object):
    """Abstract Base Class for building decorators.
    _setup(): records arguments to the decorator
    
    _before(): operates immediately before a function call
    _after(): operates immediately after a function call
    """
    __metaclass__ = abc.ABCMeta
    def __init__(self,*setup_args,**setup_kwargs):
        self.args, self.kwargs = self._setup(*setup_args,**setup_kwargs)
    def __call__(self,function):
        #~strategy function
        self.function = function
        @functools.wraps(self.function)
        def wrapper(*args,**kwargs):
            function, args, kwargs = self._before(function, *args,**kwargs)
            results = self.function(*args,**kwargs)
            results = self._after(results, *args,**kwargs)
            return results
        return wrapper
    @abc.abstractmethod
    def _setup(self,*setup_args,**setup_kwargs):
        # Do things to generate args, kwargs here
        return args, kwargs
    @abc.abstractmethod
    def _before(self,function, *args,**kwargs):
        # Manipulate function, args, and kwargs
        return function, args, kwargs
    @abc.abstractmethod
    def _after(self, function, results, *args,**kwargs):
        # Manipulate/cleanup results
        return results



class VariantMethod(object):
    """Acts like a static method when called from a class, and an instance
    method when called from an instance. In Python 2.
    This is base behavior in Python 3.
    
    This is also the behavior of methods on builtin types in Python 2.
    mystr.format(value) -->    calls str.format(mystr, value)
    
    
    class Dumb(object):
        def __init__(self, base):
            self.base = base
    
    class MyClass(object):
        def __init__(self, base):
            self.base = base
        #@staticmethod
        @VariantMethod
        def method(self, value):
            print(self.base, value)
    
    dum = Dumb('dum dum')
    mine = MyClass('smart smart')
    
    print(mine.method('kk'))
    print(MyClass.method(dum, 'kk'))
    """
    def __init__(self, func):
        self.func = func #Pure function object - not unbound method
        
    def __get__(self, obj, klass=None):
        if obj is None and klass is not None: #called from klass
            return self.func
        elif obj is not None and klass is not None: #called from klass
            return functools.partial(self.func, obj)
        else:
            raise TypeError("Unrecognized input combination.")



#==============================================================================
#        Examples of Decorators
#==============================================================================
#        see rich_decorator_examples.py
#DecoratorABC              - 
#propget                   - example of method decorator (getter property)
#Optional_Argument_Example - @decorator OR @decorator(...args...)
#foa_decorator             - another optional argument decorator
#accepts                   - specify types for positional arguments
#returns                   - specify types of return values


if __name__ == "__main__":
    import doctest
    doctest.testmod()
    
    def doc_check(func):
        """Use to check specific functions, or get more information
        on why they failed the doctest."""
        doctest.run_docstring_examples(func,globals())
    
    
    import pdb
    pdb.set_trace()
    print('---')