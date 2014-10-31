"""
@todo Add tests for SimpleProperty
"""

import unittest
if __name__ == "__main__":
    from rich_property import *
else:
    from .rich_property import *


class VPropertyTests(unittest.TestCase):
    def setUp(self):
        self.init_val = 'bar'
        self.set_val = 'foo'
         
    def basic_property_tests(self, Klass):
        myobj = Klass()
        #Setter
        myobj.data = self.set_val
        self.assertEquals(myobj._data, self.set_val)
        #Getter
        self.assertEquals(myobj.data, self.set_val)
        #Deleter
        del myobj.data
        self.assertRaises(AttributeError, lambda: myobj.data)
        self.assert_(not hasattr(myobj, 'data'))
        self.assert_(not hasattr(myobj, '_data'))
 
          
    def extended_property_tests(self, Klass):
        myobj = Klass()
        #Validator
        self.assertRaises(AssertionError, lambda: setattr(myobj, 'data', 123))
         
    def test_class_decorator(self):
        class MyClass(object):
            def __init__(self):
                pass
            @VProperty
            class data(object):
                """This is the property 'data' for 'MyClass'."""
                def getter(self):
                    return self._data
                def setter(self, value):
                    self._data = value
                def deleter(self):
                    del self._data
                def validator(self, value):
                    assert(isinstance(value, basestring))
                    return value
        self.basic_property_tests(MyClass)
        self.extended_property_tests(MyClass)
 
    def test_method_decorator(self):
        class MyClass(object):
            def __init__(self):
                pass
            @VProperty
            def data(self):
                return self._data
            @data.setter
            def data(self, value):
                self._data = value
            @data.deleter
            def data(self):
                del self._data
            @data.validator
            def data(self, value):
                assert(isinstance(value, basestring))
                return value
        self.basic_property_tests(MyClass)
        self.extended_property_tests(MyClass)
     
    def test_function_decorator(self):
        def Assertion(val):
            assert(val)
              
        class MyClass(object):
            def __init__(self):
                pass
            data = VProperty(
                lambda self: getattr(self, '_data'),
                lambda self, value: setattr(self, '_data', value),
                lambda self: delattr(self, '_data'),
                lambda self, value: value if isinstance(value, basestring) else Assertion(False),
            )
        self.basic_property_tests(MyClass)
        self.extended_property_tests(MyClass)



class PropertyTests(unittest.TestCase):
    def setUp(self):
        self.set_val = 'foo'
        self.decorator = Property
        
    def basic_property_tests(self, Klass):
        myobj = Klass()
        #Setter
        myobj.data = self.set_val
        self.assertEquals(myobj._data, self.set_val)
        #Getter
        self.assertEquals(myobj.data, self.set_val)
        #Deleter
        del myobj.data
        self.assertRaises(AttributeError, lambda: myobj.data)
        self.assert_(not hasattr(myobj, 'data'))
        self.assert_(not hasattr(myobj, '_data'))
        
    def test_class_decorator(self):
        testroot = self
        class MyClass(object):
            def __init__(self):
                pass
            @testroot.decorator
            class data(object):
                """This is the property 'data' for 'MyClass'."""
                def getter(self):
                    return self._data
                def setter(self, value):
                    self._data = value
                def deleter(self):
                    del self._data
        self.basic_property_tests(MyClass)

    def test_method_decorator(self):
        testroot = self
        class MyClass(object):
            def __init__(self):
                pass
            @testroot.decorator
            def data(self):
                return self._data
            @data.setter
            def data(self, value):
                self._data = value
            @data.deleter
            def data(self):
                del self._data
        self.basic_property_tests(MyClass)
    
    def test_function_decorator(self):
        testroot = self
        def Assertion(val):
            assert(val)
             
        class MyClass(object):
            def __init__(self):
                pass
            data = testroot.decorator(
                lambda self: getattr(self, '_data'),
                lambda self, value: setattr(self, '_data', value),
                lambda self: delattr(self, '_data'),
            )
        self.basic_property_tests(MyClass)



if __name__ == "__main__":
    unittest.main()