import unittest
import collections
import types
if __name__ == "__main__":
    from unroll import unroll, accumulate, compose
    from utils import fmap
else:
    from .unroll import unroll, accumulate, compose
    from .utils import fmap


def is_even(n):
    return n % 2 == 0
def even_triples_list(mx):
    return [
        n*3 for n in range(mx)
        if not is_even(n*3) == 0
    ]


class UnrollTests(unittest.TestCase):
    def setUp(self):
        self.input = 5
        self.expected = even_triples_list(self.input)
        
        
    def test_list_decorator(self):
        mx = self.input
        @unroll(list)
        def unrolled():
            for n in range(mx):
                triple = n*3
                if not is_even(triple):
                    continue
                yield triple

        self.assert_(not callable(unrolled))
        output = unrolled
        self.assert_(isinstance(output, collections.MutableSequence))
        self.assert_(isinstance(output, list))
        self.assertEquals(output, self.expected)
        
    def test_dict_decorator(self):
        mx = self.input
        
        @unroll(dict)
        def unrolled():
            for n in range(mx):
                triple = n*3
                if not is_even(triple):
                    continue
                yield n, triple

        self.assertEqual(unrolled, {0: 0, 2: 6, 4: 12})

    def test_list_inline(self):
        mx = self.input
        
        def _unrolled():
            for n in range(mx):
                triple = n*3
                if not is_even(triple):
                    continue
                yield triple
        unrolled = unroll(list)(_unrolled)

        self.assert_(not callable(unrolled))
        output = unrolled
        self.assert_(isinstance(output, collections.MutableSequence))
        self.assert_(isinstance(output, list))
        self.assertEquals(output, self.expected)
        
    def test_exotic_string_concat(self):
        mx = self.input
        @unroll(', '.join)
        def unrolled():
            for n in range(mx):
                triple = n*3
                if not is_even(triple):
                    continue
                yield str(triple)

        self.assertEqual(unrolled, '0, 6, 12')
        
        @unroll(fmap(str), ''.join)
        def unR():
            for n in range(mx):
                triple = n*3
                if not is_even(triple):
                    continue
                yield triple





class AccumulateTests(unittest.TestCase):
    def setUp(self):
        self.input = 5
        self.expected = even_triples_list(self.input)
    def test_list_decorator(self):
        mx = self.input

        @accumulate(list)
        def accumulated():
            for n in range(mx):
                triple = n*3
                if not is_even(triple):
                    continue
                yield triple
        
        
        self.assert_(callable(accumulated))
        output = accumulated()
        self.assert_(isinstance(output, collections.MutableSequence))
        self.assert_(isinstance(output, list))
        self.assertEquals(output, self.expected)


    def test_list_inline(self):
        mx = self.input
        
        def accumulated():
            for n in range(mx):
                triple = n*3
                if not is_even(triple):
                    continue
                yield triple
        accumulated = accumulate(list)(accumulated)

        self.assert_(callable(accumulated))
        output = accumulated()
        self.assert_(isinstance(output, collections.MutableSequence))
        self.assert_(isinstance(output, list))
        self.assertEquals(output, self.expected)


class ComposeTests(unittest.TestCase):
    def test_basic(self):
        def P1(x):
            return x+'1'
        def P2(x):
            return x+'2'
        def P3(x):
            return x+'3'
        self.assertEqual(compose(P1,P2,P3)('Z='), 'Z=123')
        self.assertEqual(compose(P3, P1, P2)(''), '312')



if __name__ == "__main__":
    unittest.main()