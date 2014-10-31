import unittest

from local_packages.richX.rich_decorator.nonbindingmethod import *
#from nonbindingmethod import NonBindingMethod

class NonBindingMethodTests(unittest.TestCase):
    def test_basic(self):
        class Dumb(object):
            def __init__(self, base):
                self.base = base
        
        class MyClass(object):
            def __init__(self, base):
                self.base = base
            @NonBindingMethod
            def method(self, value):
                return (self.base, value)
        
        dum = Dumb('dum dum')
        mine = MyClass('smart smart')
        
        self.assertEqual(
            mine.method('kk'),
            ('smart smart', 'kk')
        )
        self.assertEqual(
            MyClass.method(dum, 'kk'),
            ('dum dum', 'kk')
        )
        self.assert_(isinstance(
            mine.method,
            types.MethodType
        ))
        
        self.assert_(isinstance(
            MyClass.method,
            types.FunctionType
        ))

if __name__ == "__main__":
    unittest.main()