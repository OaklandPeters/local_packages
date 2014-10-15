import unittest
import types
import abc

from local_packages.richX.rich_operator.rich_operator import *

class TestMyProcessing(unittest.TestCase):
    class MyProcessing(object):
        __metaclass__ = OperatorMeta
        def __call__(self, *args, **kwargs):
            return 1234
        def foo(self, bang):
            return 'foo'+repr(bang)
        @classmethod
        def already_classmethod(cls, shebang):
            return 'already '+str(shebang)
             
     
    def test_basic(self):
        result = self.MyProcessing('a')
        self.assertEqual(result, 1234)
        self.assertEqual(self.MyProcessing.foo(5), "foo5")
        self.assertEqual(self.MyProcessing.already_classmethod(3), 'already 3')
         
     
    def test_abstract_method_requirement(self):
        def make_erroring():
            class MyErroring(object):
                __metaclass__ = OperatorMeta
                def caller(self, *args, **kwargs):
                    print("Insufficient - Should have errored")
            return MyErroring
     
        self.assertRaises(TypeError,make_erroring)
 
    def test_classmethods(self):        
        _get = lambda name: self.MyProcessing.__dict__[name]
        self.assert_(isinstance(_get('__call__'), classmethod))
        self.assert_(isinstance(_get('foo'), classmethod))
        self.assert_(isinstance(_get('already_classmethod'), classmethod))
 
        self.MyProcessing.new_method = lambda x: x
        self.assert_(not isinstance(_get('new_method'), classmethod))


class TestInheritance(unittest.TestCase):
    def test_three_generations(self):
        class AsserterInterface(object):
            __metaclass__ = OperatorMeta
            message = abc.abstractmethod(lambda *args, **kwargs: NotImplemented)
            meets = abc.abstractmethod(lambda *args, **kwargs: NotImplemented)
            exception = abc.abstractproperty()
            get_return = abc.abstractmethod(lambda *args, **kwargs: NotImplemented)
            #-------- Mixins
            def __call__(self, *args, **kwargs):
                if not self.meets(*args, **kwargs):
                    self.raise_exception(*args, **kwargs)
                return self.get_return(*args, **kwargs)
            def raise_exception(self, *args, **kwargs):
                raise self.exception(self.message(*args, **kwargs))

        def make_error():
            class FileAsserterInterface(AsserterInterface):
                """Parent interface for all File-related assertions."""
                
                def get_return(self, path):
                    return path
                meets = abc.abstractproperty()
                message = abc.abstractproperty()
                exception = abc.abstractproperty()
            return FileAsserterInterface
        
        self.assertRaises(TypeError, make_error)

    def test_approach_two(self):
        class GrandParent(object):
            __metaclass__ = OperatorMeta
            message = abc.abstractmethod(lambda *args, **kwargs: NotImplemented)
            meets = abc.abstractmethod(lambda *args, **kwargs: NotImplemented)
            exception = abc.abstractproperty()
            get_return = abc.abstractmethod(lambda *args, **kwargs: NotImplemented)
            #-------- Mixins
            def __call__(self, *args, **kwargs):
                if not self.meets(*args, **kwargs):
                    self.raise_exception(*args, **kwargs)
                return self.get_return(*args, **kwargs)
            def raise_exception(self, *args, **kwargs):
                raise self.exception(self.message(*args, **kwargs))
        class Parent(GrandParent):
            """
            defines one abstract --> non-abstract
            preserves three abstracts --> abstract
            """ 
            def get_return(self, path):
                return path
            meets = abc.abstractproperty()
            message = abc.abstractproperty()
            exception = abc.abstractproperty()
        
        def should_be_correct():
            class Child(Parent):
                """Implements remaining abstracts."""
                def meets(self):    return False
                def message(self):  return "My message"
                exception = RuntimeError
            return Child
        
        def should_be_error_1():
            #Error because abstract 'message' is neither:
            #    (1) defined as non-abstract
            #    (2) re-defined as abstract in Child
            class Child(Parent):
                def meets(self):    return False
                exception = RuntimeError
            return Child
        
        def should_be_correct_2():
            #Correct, because:
            #    (1) meets, exception redefined as non-abstract
            #    (2) message redefined as abstract
            class Child(Parent):
                def meets(self):    return False
                message = abc.abstractmethod(lambda *args, **kwargs: NotImplemented)
                exception = RuntimeError
            return Child
        
        

        Child1 = should_be_correct()
        Child2 = should_be_correct_2()

        # Child version 1
        self.assert_(
            issubclass(Child1, Parent)
        )
        # Child version 2
        self.assert_(
            issubclass(Child2, Parent)
        )
        
        

        
        
        
        self.assert_(
            'message' in Child2.__abstractmethods__
        )
        
        self.assertRaises(TypeError, should_be_error_1)
        self.assertRaises(TypeError, should_be_error_2)
        
if __name__ == "__main__":
    unittest.main()