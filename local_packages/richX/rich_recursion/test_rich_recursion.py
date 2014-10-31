import unittest
if __name__ == "__main__":
    from rich_recursion import *
else:
    from .rich_recursion import *





class TestRecIter(unittest.TestCase):
    def setUp(self):
        self.mapping = {
            'A': {
                'a': {
                    1:'Aa1',
                    2:'Aa2'
                },
                'b': {
                    3:'Ab3',
                    4:'Ab4'
                }
            }
        }
        self.sequence = [
            [
                0,
                1
            ],
            [2,
                [
                    3,
                    4
                ]
            ],
            5
        ]
    def test_getter(self):
        self.assertEqual(getter(self.mapping, ['A', 'a' ,2]), 'Aa2')
        self.assertEqual(getter(self.mapping, ['A', 'b', 3]), 'Ab3')
        
        self.assertRaises(KeyError, lambda: getter(self.mapping, ['A', 'c', 1]))

        self.assertEqual(getter(self.sequence, 0), [0, 1])
        self.assertEqual(getter(self.sequence, [0, 0]), 0)
        self.assertEqual(getter(self.sequence, [2]), 5)
        self.assertEqual(getter(self.sequence, 2), 5)
        self.assertRaises(IndexError, lambda: getter(self.sequence, [0, 2]))
    
    def test_setter(self):
        setter(self.mapping, ['A', 'a', 2], 'XXX')
        self.assertEqual(getter(self.mapping, ['A', 'a', 2]), 'XXX')
        self.assertEqual(self.mapping['A']['a'], {1:'Aa1', 2:'XXX'})
        
        setter(self.mapping, ['A', 'a', 'y'], 'YYY')
        self.assertEqual(getter(self.mapping, ['A', 'a', 'y']), 'YYY')
        self.assertEqual(self.mapping['A']['a'], {1:'Aa1', 2:'XXX', 'y':'YYY'})
    
    def test_rec_iter(self):
        mapping_pairs = list(rec_iter(self.mapping))
        sequence_pairs = list(rec_iter(self.sequence))
        
        mapping_expected = [
            (('A', 'a', 1), 'Aa1'),
            (('A', 'a', 2), 'Aa2'),
            (('A', 'b', 3), 'Ab3'),
            (('A', 'b', 4), 'Ab4')
        ]
        self.assertEqual(mapping_expected, mapping_pairs)
        sequence_expected = [
            ((0, 0), 0),
            ((0, 1), 1),
            ((1, 0), 2),
            ((1, 1, 0), 3),
            ((1, 1, 1), 4),
            ((2,), 5)
        ]
        self.assertEqual(sequence_expected, sequence_pairs)
        
        
    #--------------------------------------------------------------------------
    #    walk_directory() and dirwalk()
    #--------------------------------------------------------------------------
    def directory_tester(self, gen_function):
        curdir = os.path.split(__file__)[0]
        target = os.path.abspath(os.path.join(curdir, '..')) #should be richX
        files = list(gen_function(target, '*.py'))
        
        test_file = os.path.abspath('richX/rich_recursion/test_rich_recursion.py')
        self.assert_(test_file in files)
        rich_rec_pyc = os.path.abspath('richX/rich_recursion/rich_recursion.pyc')
        self.assert_(rich_rec_pyc not in files)
        for name in files:
            self.assertEqual(name[-3:], '.py')
            self.assert_(os.path.isfile(name))
        

    def test_walk_directory(self):
        self.directory_tester(walk_directory)
        
    def test_dirwalk(self):
        self.directory_tester(dirwalk)
        
        # Test if dirwalk, works as operator (class-like function)
        directory, match = dirwalk.validate()
        self.assertEqual(directory, os.getcwd())
        self.assertEqual(match, '*')
    
    

if __name__ == "__main__":
    unittest.main()