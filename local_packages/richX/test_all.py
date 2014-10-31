"""
Run this via:
python -m richX/test_all
"""
import unittest
 
def test_module(module):
    print("Testing module: '{0}'\n".format(module.__name__))
    try:
        unittest.main(module)
    except Exception as exc:
        #Exception other than standard unit-test failure
        print("Error in attempting to run unittest for module: "+str(module))
        print(exc)
        print("\n\n")
    except SystemExit as exc:
        #Normal completion of unittests
        pass
 
if __name__ == "__main__":


    from richX.rich_collections import test_rich_collections
    from richX.rich_property import test_rich_property
    from richX.rich_core import test_rich_core
    from richX.rich_recursion import test_rich_recursion
    from richX.rich_operator import test_rich_operator
    from richX.rich_decorator import test_rich_decorator

    modules = [
        test_rich_collections,
        test_rich_property,
        test_rich_core,
        test_rich_recursion,
        test_rich_operator,
        test_rich_decorator
    ]
    
    for module in modules:
        test_module(module)