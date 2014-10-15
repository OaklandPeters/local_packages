import functools
import inspect
import sys
import abc


#==============================================================================
#        Examples of Decorators
#==============================================================================
#Some decorator variations are non-intuitive to write (for example, 
#decorators supporting fully optional arguments)
#
#Most of these examples drawn from:
#    https://wiki.python.org/moin/PythonDecoratorLibrary
#------
#DecoratorABC              - 
#propget                   - example of method decorator (getter property)
#Optional_Argument_Example - @decorator OR @decorator(...args...)
#foa_decorator             - another optional argument decorator
#accepts                   - specify types for positional arguments
#returns                   - specify types of return values

class DecoratorABC(object):
    """Abstract Base Class for building decorators.
    _setup(): records arguments to the decorator
    
    _before(): operates immediately before a function call
    _after(): operates immediately after a function call
    """
    __metaclass__ = abc.ABCMeta
    def __init__(self,*setup_args,**setup_kwargs):
        self._setup(*setup_args,**setup_kwargs)
    def __call__(self,function):
        #~strategy function
        self.function = function
        @functools.wraps(self.function)
        def wrapper(*args,**kwargs):
            self._before(*args,**kwargs)
            results = self.function(*args,**kwargs)
            self._after(*args,**kwargs)
            return results
        return wrapper
    #@abc.abstractmethod
    def _setup(self,*setup_args,**setup_kwargs):
        self.args = setup_args
        self.kwargs = setup_kwargs    
    #@abc.abstractmethod
    def _before(self,*args,**kwargs):
        pass    
    #@abc.abstractmethod
    def _after(self,*args,**kwargs):
        pass
 

def propget(func):
    """A readable way to define properties; also provides insight into how to
    build descriptor-like method decorators.
    propset/propdel() written almost identically.
   
    >>> class Example(object):
    ...     @propget
    ...     def myattr(self):
    ...         return self._half * 2
    """
    locals = sys._getframe(1).f_locals
    name = func.__name__
    prop = locals.get(name)
    if not isinstance(prop, property):
        #For popset()/propdel() - change following line
        prop = property(func, doc=func.__doc__)
    else:
        doc = prop.__doc__ or func.__doc__
        #For popset()/propdel() - change following line
        prop = property(func, prop.fset, prop.fdel, doc)
    return prop

def Optional_Argument_Example():
    #How to build a decorator which handles optional arguments.
    #you can use @trace or @trace('msg1','msg2') : nice !

    def trace(*args):
        def _trace(func):
            def wrapper(*args, **kwargs):
                print enter_string
                func(*args, **kwargs)
                print exit_string
            return wrapper
        if len(args) == 1 and callable(args[0]):
            # No arguments, this is the decorator
            # Set default values for the arguments
            enter_string = 'entering'
            exit_string = 'exiting'
            return _trace(args[0])
        else:
            # This is just returning the decorator
            enter_string, exit_string = args
            return _trace




def foa_decorator(func):
    '''Decorator with fully optional arguments. 
    Allows the decorator to be used either with arguments or not.
    
    
    >>> @foa_decorator
    ... def apply(func, *args, **kw):
    ...     return func(*args, **kw)

    #Tests for both versions:
    >>> @apply
    ... def test():
    ...     return 'test applied'
    >>> test
    'test applied'
    >>> @apply(2, 3)
    ... def test(a, b):
    ...     return a + b
    >>> test
    5


    >>> @foa_decorator
    ... class apply(object):
    ...     def __init__(self, *args, **kw):
    ...         self.args = args
    ...         self.kw   = kw
    ...     def __call__(self, func):
    ...         return func(*self.args, **self.kw)
    
    #Tests for both versions:
    >>> @apply
    ... def test():
    ...     return 'test applied'
    >>> test
    'test applied'
    >>> @apply(2, 3)
    ... def test(a, b):
    ...     return a + b
    >>> test
    5

    '''

    def isFuncArg(*args, **kw):
        return len(args) == 1 and len(kw) == 0 and (
            inspect.isfunction(args[0]) or isinstance(args[0], type))

    if isinstance(func, type):
        def class_wrapper(*args, **kw):
            if isFuncArg(*args, **kw):
                # create class before usage
                return func()(*args, **kw) 
            return func(*args, **kw)
        class_wrapper.__name__ = func.__name__
        class_wrapper.__module__ = func.__module__
        return class_wrapper

    @functools.wraps(func)
    def func_wrapper(*args, **kw):
        if isFuncArg(*args, **kw):
            return func(*args, **kw)

        def functor(userFunc):
            return func(userFunc, *args, **kw)

        return functor

    return func_wrapper





def accepts(*types, **kw):
    '''Function decorator. Checks decorated function's arguments are
    of the expected types.

    Parameters:
    types -- The expected types of the inputs to the decorated function.
             Must specify type for each parameter.
    kw    -- Optional specification of 'debug' level (this is the only valid
             keyword argument, no other should be given).
             debug = ( 0 | 1 | 2 )


    >>> @accepts(int, int, int,debug='STRONG')
    ... def average(x, y, z):
    ...     return (x + y + z) / 2
    
    >>> average(5, 10, 15)
    15
    
    >>> average(5.5, 10, 15.0)
    Traceback (most recent call last):
    TypeError: 'average' method accepts (int, int, int), but was given (float, int, float)
    
    

    >>> @accepts(int, debug=2)
    ... @returns(int, debug=2)
    ... def fib(n):
    ...     if n in (0, 1): return n
    ...     return fib(n-1) + fib(n-2)
    ...
    >>> fib(5.3)
    Traceback (most recent call last):
    TypeError: 'fib' method accepts (int), but was given (float)
    
    
    '''
    if not kw:
        # default level: MEDIUM
        debug = 1
    else:
        debug = kw['debug']
    debug_map = {'NONE':0,'MEDIUM':1,'STRONG':2}
    if debug in debug_map:
        debug = debug_map[debug]
    
    try:
        def decorator(f):
            def newf(*args):
                if debug is 0:
                    return f(*args)
                assert len(args) == len(types)
                argtypes = tuple(map(type, args))
                if argtypes != types:                    
                    msg = info(f.__name__, types, argtypes, 0)
                    if debug == 1:
                        print >> sys.stderr, 'TypeWarning: ', msg
                    elif debug == 2:
                        raise TypeError, msg
                return f(*args)
            newf.__name__ = f.__name__
            return newf
        return decorator
    except KeyError, key:
        raise KeyError, key + "is not a valid keyword argument"
    except TypeError, msg:
        raise TypeError, msg




def returns(ret_type, **kw):
    '''Function decorator. Checks decorated function's return value
    is of the expected type.

    Parameters:
    ret_type -- The expected type of the decorated function's return value.
                Must specify type for each parameter.
    kw       -- Optional specification of 'debug' level (this is the only valid
                keyword argument, no other should be given).
                debug=(0 | 1 | 2)
                
    
    >>> @returns(float,debug=2)
    ... def average(x, y, z):
    ...     return (x + y + z) / 2
    >>> average(5.5, 10, 15.0)
    15.25
    >>> average(5, 10, 15)
    Traceback (most recent call last):
    TypeError: 'average' method returns (float), but result is (int)
    '''
    try:
        if not kw:
            # default level: MEDIUM
            debug = 1
        else:
            debug = kw['debug']
        def decorator(f):
            def newf(*args):
                result = f(*args)
                if debug is 0:
                    return result
                res_type = type(result)
                if res_type != ret_type:
                    msg = info(f.__name__, (ret_type,), (res_type,), 1)
                    if debug == 1:
                        print >> sys.stderr, 'TypeWarning: ', msg
                        #print('TypeWarning:  '+msg)
                    elif debug == 2:
                        raise TypeError, msg
                return result
            newf.__name__ = f.__name__
            return newf
        return decorator
    except KeyError, key:
        raise KeyError, key + "is not a valid keyword argument"
    except TypeError, msg:
        raise TypeError, msg

def info(fname, expected, actual, flag):
    '''Convenience function returns nicely formatted error/warning msg.'''
    formatter = lambda types: ', '.join([str(t).split("'")[1] for t in types])
    msg = (
        "'{fname}' method {action} ({expected}), but {subject} ({actual})"
    ).format(fname=fname,
        expected    = formatter(expected),
        actual      = formatter(actual), 
        action      = ("accepts", "returns")[flag],
        subject     = ("was given", "result is")[flag],
    )
    return msg






    
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

        #self = super(cls.__mro__[1],cls).__new__(cls)
        self = object.__new__(cls)
        
        
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


#import types
#def optional_decorator(cls):
#    """OptionalDecorator, itself as a class-decorator.
#    @optional_decorator
#    class ExampleOptionalDeco(object):
#        def __init__
#        def wrapper
#    """
#
#
#    cls.__new__ = classmethod(lambda cls,*args,**kwargs: OptionalDecorator.__new__(cls))
#    #cls.__new__ = OptionalDecorator.__new__
#    cls.__call__ = OptionalDecorator.__call__
#    cls.wrapper
#    cls.__init__
#    
#    return cls

class ExampleOptionalDeco(OptionalDecorator):
    """
    #No Arguments
    >>> @ExampleOptionalDeco
    ... def no_args(one,two):
    ...     print(one,two)
    >>> no_args('#1','#2')
    before
    ('#1', '#2')
    after

    #With Arguments
    >>> @ExampleOptionalDeco('Early','Late')
    ... def has_args(one,two):
    ...     print(one,two)
    >>> has_args('#1','#2')
    Early
    ('#1', '#2')
    Late
    """
    def __init__(self,pre=None,post=None):
        if pre == None:
            pre = "before"
        if post == None:
            post = "after"
        self.pre, self.post = (pre,post)
    def wrapper(self,*args,**kwargs):
        """Your actual decorator. 
        It should invoke self.function(*args,**kwargs)."""
        print(self.pre)
        results = self.function(*args,**kwargs)
        print(self.post)
        return results




@optional_decorator
class OtherExample(object):
    """
    #No Arguments
    >>> @OtherExample
    ... def no_args(one,two):
    ...     print(one,two)
    >>> no_args('#1','#2')
    before
    ('#1', '#2')
    after

    #With Arguments
    >>> @OtherExample('Early','Late')
    ... def has_args(one,two):
    ...     print(one,two)
    >>> has_args('#1','#2')
    Early
    ('#1', '#2')
    Late
    """
    def __init__(self,pre=None,post=None):
        if pre == None:
            pre = "before"
        if post == None:
            post = "after"
        self.pre, self.post = (pre,post)
    def wrapper(self,*args,**kwargs):
        """Your actual decorator. 
        It should invoke self.function(*args,**kwargs)."""
        print(self.pre)
        results = self.function(*args,**kwargs)
        print(self.post)
        return results



if __name__ == "__main__":
    import doctest
    #doctest.testmod()
    
    def doc_check(func):
        """Use to check specific functions, or get more information
        on why they failed the doctest."""
        doctest.run_docstring_examples(func,globals())
    
    
    doc_check(OtherExample)
    doc_check(ExampleOptionalDeco)
    import pdb
    pdb.set_trace()
    print('---')