import unittest
#-----
from local_packages.richX.rich_decorator.rich_decorator import *


class OptionalArgumentTests(unittest.TestCase):
    def setUp(self):
        class ExampleOptionalDecorator(OptionalDecorator):
            def __init__(self,pre="before",post="after"):
                self.pre, self.post = (pre,post)
            def wrapper(self,*args,**kwargs):
#                output = []
#                output.append(self.pre)
#                results = self.function(*args,**kwargs)
#                output.append(results)
#                output.append(self.post)
#                return output
                return [self.pre,self.function(*args,**kwargs),self.post]
                
        self.EOD = ExampleOptionalDecorator
        
        @optional_decorator
        class ExampleOptionalDecorator_v2(object):
            def __init__(self,pre="pre",post="post"):
                self.pre, self.post = (pre,post)
            def wrapper(self,*args,**kwargs):
                return [self.pre,self.function(*args,**kwargs),self.post]
        self.EOD2 = ExampleOptionalDecorator_v2
        
    def test_arguments(self):
        @self.EOD
        def no_args(one,two):
            return str((one,two))

        self.assertEqual(
            no_args('#1','#2'),['before', "('#1', '#2')", 'after']
        )
    def test_no_arguments(self):
        @self.EOD('A','B')
        def has_args(one,two):
            return str((one,two))
        
        self.assertEqual(
            has_args('#1','#2'),['A', "('#1', '#2')", 'B']
        )
        
#    def test_deco_arguments(self):
#        @self.EOD2
#        def no_args(one,two):
#            return str((one,two))
#
#        self.assertEqual(
#            no_args('#1','#2'),['pre', "('#1', '#2')", 'post']
#        )
#    def test_deco_no_arguments(self):
#        @self.EOD2('A','B')
#        def has_args(one,two):
#            return str((one,two))
#        
#        self.assertEqual(
#            has_args('#1','#2'),['A', "('#1', '#2')", 'B']
#        )
#        
#        
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


if __name__ == "__main__":
    unittest.main()