import collections
import os
import sys
import fnmatch
#-----
from .. import rich_core


#==============================================================================
#        Recursion
#==============================================================================

#@todo: remove this method='iterative'/'recursive' choice
#    It was placed here originally to test the relative
#    efficiency, but is no longer needed.
def getter(container, keypath, method='iterative'):
    """
    container: a sequence or mapping
    indices is a list or tuple of indices (~keypath) in the data.
    
    >>> mydict = {
    ... 'A':{
    ...     'a':{
    ...         1:'Aa1',
    ...         2:'Aa2'
    ...     },
    ...     'b':{
    ...         3:'Ab3',
    ...         4:'Ab4'
    ...     }
    ...    }
    ... }
    >>> getter(mydict,['A','a',2])
    'Aa2'
    >>> getter(mydict,['A','b',3])
    'Ab3'
    """
    assert(isinstance(container,rich_core.Associative))
    assert(method in ('iterative', 'recursive')), (
        "Invalid getter method. Must be 'iterative' or 'recursive'.")
    keypath = rich_core.ensure_tuple(keypath)
    #if not isinstance(keypath, rich_core.NonStringIterable):
    #    keypath = [keypath]

    if method == 'iterative':
        for k in keypath:
            container = container[k]
        return container
    elif method == 'recursive':
        if len(keypath) == 0:
            return container #~the value being sought
        else:   #at least one key left
            first, rest = keypath[0], keypath[1:]
            return getter(container[first], rest, method)


#@todo: remove this method='iterative'/'recursive' choice
#    It was placed here originally to test the relative
#    efficiency, but is no longer needed.
def setter(container, keypath, value, method='iterative'):
    """
    >>> mydict = {
    ... 'A':{
    ...     'a':{
    ...         1:'Aa1',
    ...         2:'Aa2'
    ...     },
    ...     'b':{
    ...         3:'Ab3',
    ...         4:'Ab4'
    ...     }
    ...    }
    ... }
    >>> setter(mydict,['A','a',3],'Aa3')
    >>> getter(mydict,['A','a',3])
    'Aa3'
    >>> setter(mydict,['A','a',1],'111')
    >>> getter(mydict,['A','a',1])
    '111'
    """
    #assert(isinstance(container, collections.Sequence, collections.Mapping)
    #    and not isinstance(container, basestring))
    assert(isinstance(container,rich_core.Associative))
    assert(method in ('iterative', 'recursive')), (
        "Invalid getter method. Must be 'iterative' or 'recursive'.")

    if method == 'iterative':
        front, last = keypath[:-1], keypath[-1]
        for k in front:
            #Create key if necessary, and assign's its value to container
            container = container.setdefault(k, {})
        #Assignment to container[] should modify it in caller's context
        container[last] = value
    elif method == 'recursive':
        if len(keypath) == 0:
            return value

        first, rest = keypath[0], keypath[1:]
        #if first not in container.keys():
        if first not in indexes(container, iterator=False):
            container[first] = {}
        else:
            #tempD = container[first]
            #res = setter(tempD, rest, value, method='recursive')
            #container[first] = res
            container[first] = setter(
                container[first], rest, value, method='recursive')
        return container

def rec_iter(obj, path=None, history=None):
    '''
    Inspired by Yaniv Aknin's objwalk():
    http://code.activestate.com/recipes/577982-recursively-walk-python-objects/
    Changes:
    [] handling of 'Set'
        removed enumeration over Sets -- because this function should return
        'path' which can be used to retreive nested elements - which is not
        true for sets.
    [] string_types = (str, unicode) if str is bytes else (str, bytes)
        needs to be replaced by utility.NonStringIterable
    [] isinstance(obj, (Sequence, Set)) and not isinstance(obj, string_types):
        --> [Mapping, Iterable] and not basestring
    [] Reorganized logical flow:
        does not set 'iterator', then check if it is set,
    -------- Example
    defaults = {...complicated nested dict,
        containing lists, strings, sets, dicts, numbers...    }
    for keypath, value in rec_iter(defaults):
        print(keypath, value)
        assert(getter(defaults, keypath)==value)
        
    
    >>> mydict = {
    ... 'A':{
    ...     'a':{
    ...         1:'Aa1',
    ...         2:'Aa2'
    ...     },
    ...     'b':{
    ...         3:'Ab3',
    ...         4:'Ab4'
    ...     }
    ...    }
    ... }
    >>> for path,elm in rec_iter(mydict):
    ...     print(path,elm)
    (('A', 'a', 1), 'Aa1')
    (('A', 'a', 2), 'Aa2')
    (('A', 'b', 3), 'Ab3')
    (('A', 'b', 4), 'Ab4')
    '''
    if path is None:        path=tuple()
    if history is None:     history=set()

    #if (isinstance(obj, [collections.Mapping, collections.Sequence])
    #and not isinstance(obj, basestring)):
    if isinstance(obj, rich_core.Associative):
        iterator = rich_core.pairs(obj, iterator=True)
        if id(obj) not in history:
            history.add(id(obj))
            for index, elm in iterator:
                for result in rec_iter(elm, path+(index, ), history):
                    yield result
            history.remove(id(obj))
    else:
        yield path, obj
        
def rec_pairs(obj, iterator=False):
    gen = rec_iter(obj)
    if iterator:        return gen
    else:               return list(gen)
def rec_indexes(obj, iterator=False):
    gen = (keypath for keypath, value in rec_iter(obj))
    if iterator:        return gen
    else:               return list(gen)
def rec_elements(obj, iterator=False):
    gen = (value for keypath, value in rec_iter(obj))
    if iterator:        return gen
    else:               return list(gen)
def RecursionItemMapper(obj, func, makeCopy=True):
    mutableassociative = (collections.MutableMapping, collections.MutableSequence)
    rich_core.AssertKlass(obj, mutableassociative, name='obj')
    if makeCopy:
        obj = copy.deepcopy(obj)
        makeCopy = False
    for k, v in rec_pairs(obj):
        obj[k] = RecursionItemMapper(v, func, makeCopy)
    return func(obj)
def basic_recursive_iterator(input_iterable):
    '''Returns values from potentially nested iterable objects,
    such as nested lists or dicts.
    Limitation: does not allow modification IN-PLACE.
    (ie you still need a mapper function)
    '''
    for elm in iter(input_iterable):
        if hasattr(elm, "__iter__"): #is following better??  hasattr(elm, "iter")
            basic_recursive_iterator(elm)
        else:
            yield elm


def mapping_equality(A,B):
    if mapping_compare(A,B) == False:
        return False
    if mapping_compare(B,A) == False:
        return False
    return True

def mapping_compare(A,B):
    """One-way recursive comparison of A to B."""
    assert(isinstance(A,collections.Mapping)), "A is not a Mapping."
    assert(isinstance(B,collections.Mapping)), "B is not a Mapping."
    for path,value_A in rec_iter(A):
        try:
            value_B = getter(B,path)
        except KeyError:
            return False
        except IndexError:
            return False
        if value_A != value_B:
            return False
    return True



def walk_directory(directory, match='*'):
    #Validate... directory-->basestring, directory, exists
    #Validate... match, basestring 
    for root, dirnames, filesnames in os.walk(directory):
        for filename in fnmatch.filter(filesnames, match):
            yield os.path.join(root, filename)


class dirwalk(object):
    """Operator (~function).
    Find all files in directory which match a given string.
    """
    def __new__(cls, *args, **kwargs):
        return cls.__call__(*args, **kwargs)
    @classmethod
    def __call__(cls, directory=None, match='*'):
        directory, match = cls.validate(directory, match)
        
        for root, dirnames, filesnames in os.walk(directory):
            for filename in fnmatch.filter(filesnames, match):
                yield os.path.join(root, filename)
        
    @classmethod
    def validate(cls, directory=None, match='*'):
        if isinstance(directory, type(None)):
            directory = os.getcwd()
        rich_core.AssertKlass(directory, basestring, name='directory')
        if not os.path.isdir(directory):
            raise ValueError("'{0}' is not an existing directory.".format(directory))
        
        rich_core.AssertKlass(match, basestring, name='match')
        return directory, match






def rage_import(package, directory=None):
    """Somewhat comical function, useful while developing packages, to
    get around 'relative-import' related importation issues.
    It tries to import a package name, and if that doesn't work, then
    recursively walks out one directory level and tries again.
    Terminates when it's no longer in a package (defined by not having
    an __init__.py in that directory)."""
    
    if isinstance(directory, type(None)):
        curdir = os.getcwd()
    try:
        return __import__(package)
    except ImportError:
        return _rage_import(package, curdir)        

def _rage_import(package, curdir):
    newdir = os.path.abspath(os.path.join(curdir,'..'))
    # Termination condition - no __init__.py in 'newdir'
    init_exists = os.path.exists(os.path.join(newdir, '__init__.py'))
    if not init_exists:
        raise ImportError("Could not find module {0} inside a package".format(package))
    # Recursion: try again one directory higher
    
    if newdir in sys.path:
        raise RuntimeError("Directory already in path, continuing will cause errors.")
    sys.path.append(newdir)
    try:
        return __import__(package)
    except ImportError:
        return _rage_import(package, newdir)    
    finally:
        sys.path.remove(newdir)




class RageImport(object):
    """Operator
    Somewhat comical function, useful while developing packages, to
    get around 'relative-import' related importation issues.
    It tries to import a package name, and if that doesn't work, then
    recursively walks out one directory level and tries again.
    Terminates when it's no longer in a package (defined by not having
    an __init__.py in that directory).
    """
    def __new__(cls, *args, **kwargs):
        return cls.__call__(*args, **kwargs)
    @classmethod
    def __call__(cls, package, directory=None):
        package, directory = cls.validate(package, directory)
        
        try:
            return __import__(package)
        except ImportError:
            return cls.recurse(package, directory)
    @classmethod
    def recurse(cls, package, directory):
        """Try to find the package, one directory higher."""
        newdir = os.path.abspath(os.path.join(curdir,'..'))
        cls._check_termination(newdir)
        
        # Recursion: try again one directory higher
        sys.path.append(newdir)
        try:
            return __import__(package)
        except ImportError:
            return cls.recurse(package, newdir)    
        finally:
            sys.path.remove(newdir)
    @classmethod
    def _check_termination(cls, newdir):
        if cls._termination_condition(newdir):
            raise ImportError(str.format(
                "Could not find module {0}, terminated inside non-package '{1}'.",
                package, newdir
            ))
    @classmethod
    def _termination_condition(cls, newdir):
        return os.path.exists(os.path.join(newdir, '__init__.py'))
    @classmethod
    def validate(cls, package, directory=None):
        """"Validate input. 
        Does not use standardized AssertKlass, because rage_import
        is intended to be defined before that function."""
        if not isinstance(package, basestring):
            raise TypeError("'package' must be a basestring.")
        
        if isinstance(directory, type(None)):
            directory = os.getcwd()
        if not isinstance(directory, basestring):
            raise TypeError("'directory' must be a basestring.")
        
        return package, directory
