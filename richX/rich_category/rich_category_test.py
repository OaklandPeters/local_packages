from rich_category import *

class RichCategoryDocTests(object):
#    def Of(self):
#        """
#        >>> Is(Type(Sequence,of=basestring)([1,2])
#        False
#        >>> Is(Type(Sequence,of=basestring)(['a','b'])
#        True
#        """
        
    def Type(self):
        """
        >>> Is(Type)({},pos=collections.Iterable,neg=basestring)
        True
        >>> nonstringiterable = Type(pos=collections.Iterable,neg=basestring)
        >>> Is(nonstringiterable)({})
        True
        >>> Is(nonstringiterable)("aba")
        False
        
        >>> values = [('a',),['a'],{'a':1},'a',unicode('a'),1,1.0]
        >>> [Is(nonstringiterable)(v) for v in values]
        [True, True, True, False, False, False, False]
        
        
        >>> import types
        >>> type_objs = [v for (k,v) in vars(types).items() if not k.startswith('__')]
        >>> any([Is(Type)(t,Type.nil) for t in type_objs])
        False
        
        >>> all([Is(Type)(t,Type.aleph) for t in type_objs])
        True
        
        """
    def Enum(self):
        """
        >>> values = [('a',),['a'],{'a':1},'aaa',unicode('a'),1,1.0]
        >>> [Is(Enum)(v,Enum.aleph) for v in values]
        [True, True, True, True, True, True, True]
        
        >>> [Is(Enum)(v,Enum.nil) for v in values]
        [False, False, False, False, False, False, False]
        """
    def Attrs(self):
        """
        >>> nonstringsequence = Attrs(
        ...     pos=['__len__','__iter__','__contains__','__getitem__']
        ... )
        >>> Is(nonstringsequence)("alkajlka")
        False
        >>> Is(nonstringsequence)([])
        True
        >>> Is(nonstringsequence)(('a','b'))
        True
        """
    def Subclass(self):
        """
        >>> import types
        >>> type_objs = [v for (k,v) in vars(types).items() if not k.startswith('__')]
        >>> any([Is(Subclass)(t,Subclass.nil) for t in type_objs])
        False
        
        >>> all([Is(Subclass)(t,Subclass.aleph) for t in type_objs])
        True
        """
    def Keys(self):
        """
#        >>> Is(Keys)({'a':1,'b':2},pos=Keys.aleph)
#        True
#        >>> Is(Keys)({},pos=Keys.aleph)
#        True
        """
    def Is(self):
        """
        >>> Is(Keys)({'a':1,'b':2},'a','c')
        True
        >>> mykeys = Keys(pos=('a','b'),neg='c')
        >>> Is(mykeys)({'a':1,'b':2})
        True
        >>> Is(mykeys)({'a':1,'b':2,'c':3})
        False
        
        >>> misstypes = Type(pos=collections.Sequence,neg=str,name='myvar')
        >>> Is(misstypes)(['a','b'])
        True
        >>> Is(misstypes)("aba")
        False
        
        #Test reference to the underlying .__dict__ of misstypes
        >>> misstypes.neg = None
        >>> Is(misstypes)("aba")
        True
        """
    def AssertKeys(self):
        """
        >>> mydict = {'a':1,'b':2}
        >>> AssertKeys(mydict,['b','c'],name='My Dictionary')
        Traceback (most recent call last):
        KeyError: "'My Dictionary' of type 'dict' should have all of ['b', 'c']"
        >>> AssertKeys(mydict,'a')
        {'a': 1, 'b': 2}
        >>> AssertKeys({'a':1},'b')
        Traceback (most recent call last):
        KeyError: "Object of type 'dict' should have all of ['b']"
        """
    def HasKeys(self):
        """
        >>> mydict = {'a':1, 'b':2, 32:3, (2,3,'a'):4}
        >>> HasKeys(mydict,'b')
        True
        >>> HasKeys(mydict,'c')
        False
        >>> HasKeys(mydict,['b',32,31])
        False
        >>> HasKeys(mydict,['b',32,(2,3,'a')])
        True
        >>> HasKeys(mydict,['b',32,31],neg=32)
        False
        >>> HasKeys(['a','b'],[0,1])
        False
        """
    def AssertType(self):
        """
        >>> AssertType({},object)
        {}
        >>> AssertType("aa",pos=collections.Sequence,neg=basestring,name='nameless')
        Traceback (most recent call last):
        TypeError: 'nameless' of type 'str' should be instance of any of ['Sequence'] and not any of ['basestring']
        
        >>> AssertType({},collections.Sequence)
        Traceback (most recent call last):
        TypeError: Object of type 'dict' should be instance of any of ['Sequence']
        >>> AssertType({'a':1},collections.Mapping)
        {'a': 1}
        >>> AssertType([1,2,'a'],list)
        [1, 2, 'a']
        >>> AssertType([1,2,'a'],collections.Sequence)
        [1, 2, 'a']
        >>> AssertType([],(collections.Sequence,list),(type,type(None)))
        []
        >>> AssertType([],pos=(collections.Sequence,list),neg=(type,type(None),object))
        Traceback (most recent call last):
        TypeError: Object of type 'list' should be instance of any of ['Sequence', 'list'] \
and not any of ['type', 'NoneType', 'object']
        """
    def IsType(self):
        """
        IsType(obj,pos=None,neg=None) -> bool
        -----
        @future: use UniversalSet/UniversalClass and EmptySet/Nil
            as default values.
        
        >>> IsType({},dict)
        True
        >>> IsType({},type(None))
        False
        >>> obj = object()
        >>> IsType(obj,pos=object,neg=type(None))
        True
        >>> IsType(None,pos=(object,),neg=type(None))
        False
    
        >>> IsType('mystr',[basestring,type(None)],[int,unicode])
        True
        >>> IsType(None,[type(None),int],neg=(basestring,))
        True
        
        >>> IsType((1,2,3),basestring)
        False
        >>> IsType((1,2,3),(collections.Sequence,type(None)))
        True
        >>> IsType((1,2,3),(collections.Sequence,type(None)),tuple)
        False
        >>> IsType("asda",str)
        True
        >>> IsType(unicode("asda"),basestring,str)
        True
        >>> IsType("asda",basestring,str)
        False
        >>> IsType(['a',1,'b'],rcore.NonStringIterable)
        True
        >>> IsType('a1b',rcore.NonStringIterable)
        False
        
        >>> IsType('aa','akakl')
        Traceback (most recent call last):
        TypeError: isinstance() arg 2 must be a class, type, or tuple of classes and types
        """
    def IsEnum(self):
        """
        Is obj drawn from finite list of possibilities, and not from another.
        >>> IsEnum('string',('string','text',None))
        True
        >>> IsEnum('string',('string','text',None),'string')
        False
        >>> IsEnum(12,('string','text',None))
        False
        >>> IsEnum(123,('string','text',None))
        False
        >>> IsEnum(45,45)
        True
        >>> IsEnum('aa','aa')
        True
        >>> IsEnum('aa',('aa',))
        True
        """
    def AssertEnum(self):
        """
        >>> AssertEnum('string',('string','text',None))
        'string'
        >>> AssertEnum('string',('string','text',None),'string')
        Traceback (most recent call last):
        ValueError: Object of type 'str' should be any of ["('string', 'text', None)"] and not any of ["('string',)"]
        >>> AssertEnum(123,('string','text',None))
        Traceback (most recent call last):
        ValueError: Object of type 'int' should be any of ["('string', 'text', None)"]
        >>> AssertEnum(123,('string','text',None),(123,34))
        Traceback (most recent call last):
        ValueError: Object of type 'int' should be any of ["('string', 'text', None)"] and not any of ['(123, 34)']
        >>> AssertEnum(45,45)
        45
        """
    def IsSubclass(self):
        """       
        >>> IsSubclass(dict,pos=object,neg=type(None))
        True
        >>> IsSubclass(type(None),pos=object,neg=type(None))
        False
        >>> IsSubclass(str,[basestring,type(None)],[int,unicode])
        True
        >>> IsSubclass(type((1,2,3)),basestring)
        False
        >>> IsSubclass(type((1,2,3)),(collections.Sequence,type(None)))
        True
        >>> IsSubclass(type((1,2,3)),(collections.Sequence,type(None)),tuple)
        False
    
        >>> IsSubclass(list,rcore.NonStringIterable)
        True
        >>> IsSubclass(str,rcore.NonStringIterable)
        False
        """
    def AssertSubclass(self):
        """
        >>> AssertSubclass(dict,collections.Sequence)
        Traceback (most recent call last):
        TypeError: Object of type 'type' should be subclass of any of ['Sequence']
        >>> AssertSubclass(dict,(object,type),(collections.Mapping))
        Traceback (most recent call last):
        TypeError: Object of type 'type' should be subclass of any of ['object', 'type'] and not any of ['Mapping']
        >>> AssertSubclass(dict,collections.Mapping)
        <type 'dict'>
        >>> AssertSubclass(list,collections.Sequence)
        <type 'list'>
        >>> AssertSubclass(rcore.NonStringSequence,collections.Iterable)
        <class 'rich_core.NonStringSequence'>
        >>> AssertSubclass(Type,CategoryFunctor)
        <class 'rich_category.Type'>
        """
    def EmptySet(self):
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
    def UniversalSet(self):
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


#values = [('a',),['a'],{'a':1},'a',unicode('a'),1,1.0]
#print([isinstance(v,collections.Iterable) for v in values])


if __name__ == "__main__":
    import doctest
    doctest.testmod()
    
    def doc_check(func):
        """Use to check specific functions, or get more information
        on why they failed the doctest."""
        doctest.run_docstring_examples(func,globals())
        
    import pdb
    pdb.set_trace()
    print('-----')