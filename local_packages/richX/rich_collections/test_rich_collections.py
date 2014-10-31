"""
Tests for BasicSequence, BasicMutableSequence, and BasicMutableMapping
from rich_collections.py.

These do not account for nested structures - which would require recursion.
"""
import unittest
#----
import rich_collections
#from richX.rich_collections import BasicSequence, BasicMutableSequence, BasicMutableMapping


class BasicSequenceTests(unittest.TestCase):
    def setUp(self):
        self.expected_words = ('one', 'two-three', 'jumping.') 
        self.words = rich_collections.BasicSequence(self.expected_words)
        
    def test__getitem__(self):
        self.assertEqual(
            self.words[1], 
            self.expected_words[1], 
            "Bad __getitem__(1)"
        )
    def test_comparison(self):
        self.assertEqual(
            self.words,
            self.expected_words,
            str.format(
                "words ({0}) do not match expected_words ({1}).",
                self.words,
                self.expected_words
            )
        )
    def test_len(self):
        self.assertEqual(
            len(self.words),
            len(self.expected_words),
            "Bad length"
        )


class BasicMutableSequenceTests(unittest.TestCase):
    def setUp(self):
        self.expected_words = ['one', 'two-three', 'jumping.'] 
        self.words = rich_collections.BasicMutableSequence(self.expected_words)
    def test_setitem(self):
        self.words[1] = 'revised'
        self.assertEqual(
            self.words[1],
            'revised',
            'Failed setitem.'
        )
    def test_append(self):
        self.words.append('running and swimming')
        self.assertEqual(
            self.words[3],
            'running and swimming',
            "Failed append"
        )
    def test_delitem(self):
        del self.words[2]
        self.assertEqual(
            len(self.words),
            2,
            "Failed delitem length test."
        )
        self.assertEqual(
            self.words[-1],
            'two-three',
            "Failed delitem get last ([-1]) test"
        )



class BasicMutableMappingTests(unittest.TestCase):
    def setUp(self):
        self.log = rich_collections.BasicMutableMapping({
            'task-1': {
                'file-1': 'foo',
                'file-2': 'bar'
            },
            'task-2': {
                'file-3': 'foo-bar'
            }
        })
    def test_get(self):
        self.assertEqual(self.log['task-1']['file-1'], 'foo')
        self.assertEqual(self.log['task-2'],{'file-3': 'foo-bar'})
    def test_set(self):
        self.log['task-3'] = 'yawn'
        
        self.assertEqual(self.log['task-3'], 'yawn')
        self.assertEqual(self.log['task-2'],{'file-3': 'foo-bar'})



#==============================================================================
#    Local utility functions
#==============================================================================
def iter_compare(first, second):
    for A, B in zip(first, second):
        yield (A == B)
def sequence_compare(first, second):
    return all(iter_compare(first, second))
        

if __name__ == "__main__":
    unittest.main()