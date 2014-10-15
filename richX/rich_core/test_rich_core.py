import unittest
if __name__ == "__main__":
    from rich_core import *
    from assertions_category import *
else:
    from .rich_core import *
    from .assertions_category import *


class TestBasics(unittest.TestCase):
    def test_required(self):
        d = {'a':1,'b':2}

        # If Ok, returns None, else throws Exceptions
        self.assert_(required(d,['a','b']) == None)
        self.assertRaises(KeyError, lambda: required(d,('a','c')))
        
    def test_defaults(self):
        d1 = {'a':1, 'b':2}
        d2 = {'b':3, 'c':4}
        d3 = {'b':5, 'd':6}
        #Left most has priority
        merged = defaults(d1,d2,d3)
        
        self.assertEqual(sorted(merged.keys()), ['a','b','c','d'])
        self.assert_(merged['b'] == 2)
        
    def test_classproperty(self):
        class MyClass(object):
            @ClassProperty
            @classmethod
            def mymethod(cls):
                return 'data'
        self.assertEqual(MyClass.mymethod, 'data')

    def test_NonStringIterable(self):
        #        >>> (.*?)\n        (.*?)\n
        #        self.assertEqual(\1,\2)\n
        self.assertEqual(issubclass(int, NonStringIterable),False)
        self.assertEqual(issubclass(list, NonStringIterable),True)
        self.assertEqual(issubclass(str, NonStringIterable),False)
        self.assertEqual(isinstance(1, NonStringIterable),False)
        self.assertEqual(isinstance(["a"], NonStringIterable),True)
        self.assertEqual(isinstance("a", NonStringIterable),False)
        self.assertEqual(isinstance(unicode('abc'), NonStringIterable),False)
        self.assertEqual(isinstance(iter("a"), NonStringIterable),True)

    def test_NonStringSequence(self):
        self.assertEqual(issubclass(int,NonStringSequence),False)
        self.assertEqual(issubclass(list,NonStringSequence),True)
        self.assertEqual(isinstance(1,NonStringSequence),False)
        self.assertEqual(isinstance(["a"],NonStringSequence),True)
        self.assertEqual(isinstance("a",NonStringSequence),False)
        self.assertEqual(isinstance(unicode('abc'),NonStringSequence),False)
        self.assertEqual(isinstance(iter("a"),NonStringSequence),False)

    def test_Associative(self):
        self.assertEqual(isinstance({},Associative),True)
        self.assertEqual(isinstance([],Associative),True)
        self.assertEqual(isinstance("",Associative),False)
        self.assertEqual(issubclass(int,Associative),False)
        from collections import defaultdict
        self.assertEqual(issubclass(defaultdict,Associative), True)

    def test_pairs(self):
        mylist = ['a','b','c']
        mydict = {'a':0,'b':1,'c':2}
        
        self.assertEqual(pairs(mylist), [(0,'a'), (1,'b'), (2,'c')])
        self.assertEqual(
            sorted(pairs(mydict)), 
            [('a',0), ('b',1), ('c',2)]
        )

    def test_ensure_tuple(self):
        self.assertEqual(ensure_tuple(['a','b']),('a', 'b'))
        self.assertEqual(ensure_tuple('abc'),('abc',))
        self.assertEqual(ensure_tuple(iter(range(4))),(0, 1, 2, 3))
        self.assertEqual(ensure_tuple(None),(None,))
        self.assertEqual(ensure_tuple({'a':1, 'b':2}),({'a': 1, 'b': 2},))
         
class TestAsserterCategory(unittest.TestCase):
    #        >>> (.*?)\n        (.*?)\n
    #        self.assertEqual(\1,\2)\n
    def test_IsType(self):
        self.assertEqual(IsType({},dict),True)
        self.assertEqual(IsType({},type(None)),False)
        
        obj_not_none = lambda elm: IsType(elm, pos=object,neg=type(None))
        self.assertEqual(obj_not_none(object()), True)
        self.assertEqual(obj_not_none(None), False)
    
        self.assertEqual(IsType('mystr',[basestring,type(None)],[int,unicode]),True)
        self.assertEqual(IsType(None,[type(None),int],neg=(basestring,)),True)
    
        self.assertEqual(IsType((1,2,3),basestring),False)
        self.assertEqual(IsType((1,2,3),(collections.Sequence,type(None))),True)
        self.assertEqual(IsType((1,2,3),(collections.Sequence,type(None)),tuple),False)
        self.assertEqual(IsType("asda",str),True)
        self.assertEqual(IsType(unicode("asda"),basestring,str),True)
        self.assertEqual(IsType("asda",basestring,str),False)
        self.assertEqual(IsType(['a',1,'b'],NonStringIterable),True)
        self.assertEqual(IsType('a1b',NonStringIterable),False)
    
        self.assertRaises(TypeError, lambda: IsType('aa','akakl'))

    def test_AssertType(self):
        self.assertRaises(
            TypeError,
            lambda: AssertType("aa",pos=collections.Sequence,neg=basestring,name='nameless')
        )
        self.assertRaises(
            TypeError,
            lambda: AssertType({},collections.Sequence)
        )
        self.assertRaises(TypeError, lambda: AssertType('aa','aa'))
        self.assertRaises(
            TypeError,
            lambda: AssertType([],pos=(collections.Sequence,list),neg=(type,type(None),object))
        )
        
        self.assertEqual(AssertType({},object), {})
        self.assertEqual(AssertType({'a':1},collections.Mapping), {'a': 1})
        self.assertEqual(AssertType([1,2,'a'],list), [1, 2, 'a'])
        self.assertEqual(AssertType([1,2,'a'],collections.Sequence), [1, 2, 'a'])
        self.assertEqual(AssertType([],(collections.Sequence,list),(type,type(None))), [])
        
    def test_HasAttrs(self):
        self.assertEqual(HasAttrs({},("__contains__","values")),True)
        self.assertEqual(HasAttrs([],("__contains__","values")),False)
        class MyParent(object):
            def user(self): return 'baz'
        class MyClass(MyParent):
            def budget(self): return 'foo'
            def record(self): return 'bar'
        self.assertEqual(HasAttrs(MyClass,'budget'),True)
        self.assertEqual(HasAttrs(MyClass,'payroll'),False)
        self.assertEqual(HasAttrs(MyClass,('payroll','user')),False)
        self.assertEqual(HasAttrs(MyClass,('budget','user')),True)
        self.assertEqual(HasAttrs(MyClass,'budget','user'),False)
        self.assertEqual(HasAttrs(MyClass,pos='budget',neg='user'),False)
        self.assertEqual(HasAttrs(MyClass,neg='user',pos='budget'),False)
        self.assertEqual(HasAttrs(MyClass,neg='identifier',pos='budget'),True)
        self.assertEqual(HasAttrs(MyClass,('user','record'),('identifier','company')),True)
        self.assertEqual(HasAttrs(MyClass,('user','record'),('identifier','budget')),False)
        self.assertEqual(HasAttrs(MyClass,('identifier','company'),('user','record')),False)
    def test_AssertAttrs(self):
        self.assertEqual(AssertAttrs({},("__contains__","values")),{})
        self.assertRaises(AttributeError,
            lambda: AssertAttrs([],("__contains__","values"))
        )
        class MyClass(object):
            def budget(self): return 'foo'
            def record(self): return 'bar'
        self.assertEqual(AssertAttrs(MyClass,'budget'),MyClass)
        self.assertRaises(AttributeError,
            lambda: AssertAttrs(MyClass,'payroll')
        )
        self.assertRaises(AttributeError,
            lambda: AssertAttrs(MyClass,'payroll',('user','record'))
        )
    def test_IsEnum(self):
    
        self.assertEqual(IsEnum('string',('string','text',None),'string'),False)
        self.assertEqual(IsEnum(12,('string','text',None)),False)
        self.assertEqual(IsEnum(123,('string','text',None)),False)
        self.assertEqual(IsEnum(45,45),True)
        self.assertEqual(IsEnum('aa','aa'),True)
        self.assertEqual(IsEnum('aa',('aa',)),True)
    def test_AssertEnum(self):
        self.assertEqual(AssertEnum('string',('string','text',None)),'string')
        self.assertRaises(ValueError,
            lambda: AssertEnum('string',('string','text',None),'string')
        )
        self.assertRaises(ValueError,
            lambda: AssertEnum(123,('string','text',None))
        )
        self.assertRaises(ValueError,
            lambda: AssertEnum(123,('string','text',None),(123,34))
        )
        self.assertEqual(AssertEnum(45,45),45)
    def test_IsSubclass(self):
        self.assertEqual(IsSubclass(dict,pos=object,neg=type(None)),True)
        self.assertEqual(IsSubclass(type(None),pos=object,neg=type(None)),False)
        self.assertEqual(IsSubclass(str,[basestring,type(None)],[int,unicode]),True)
        self.assertEqual(IsSubclass(type((1,2,3)),basestring),False)
        self.assertEqual(IsSubclass(type((1,2,3)),(collections.Sequence,type(None))),True)
        self.assertEqual(IsSubclass(type((1,2,3)),(collections.Sequence,type(None)),tuple),False)
    
        self.assertEqual(IsSubclass(list,NonStringIterable),True)
        self.assertEqual(IsSubclass(str,NonStringIterable),False)
    def test_AssertSubclass(self):
        self.assertRaises(ValueError,
            lambda: AssertSubclass(dict,collections.Sequence)
        )
        self.assertRaises(ValueError,
            lambda: AssertSubclass(dict,(object,type),(collections.Mapping))
        )
        self.assertEqual(AssertSubclass(dict,collections.Mapping),dict)
        self.assertEqual(AssertSubclass(list,collections.Sequence),list)
        self.assertEqual(AssertSubclass(NonStringSequence,collections.Iterable),NonStringSequence)
        self.assertEqual(AssertSubclass(IsType,PredicateFunctor),IsType)
    def test_HasKeys(self):
        mydict = {'a':1, 'b':2, 32:3, (2,3,'a'):4}
        self.assertEqual(HasKeys(mydict,'b'),True)
        self.assertEqual(HasKeys(mydict,'c'),False)
        self.assertEqual(HasKeys(mydict,['b',32,31]),False)
        self.assertEqual(HasKeys(mydict,['b',32,(2,3,'a')]),True)
        self.assertEqual(HasKeys(mydict,['b',32,31],neg=32),False)
        self.assertEqual(HasKeys(['a','b'],[0,1]),False)
    def test_AssertKeys(self):
        mydict = {'a':1,'b':2}
        self.assertRaises(KeyError,
            lambda: AssertKeys(mydict,['b','c'],name='My Dictionary')
        )
        self.assertEqual(AssertKeys(mydict,'a'),{'a': 1, 'b': 2})
        self.assertRaises(KeyError,
            lambda: AssertKeys({'a':1},'b')
        )
    
    
if __name__ == "__main__":
    unittest.main()