import unittest
from multimaps import SetMultimap,ListMultimap

class TestMultimaps(unittest.TestCase):
    #def setUp(self):
    def test_SetMultimap(self):
        factory = SetMultimap
        
        #[] Test Shared Traits - includes insertion via _populate
        self._shared(factory)

        #[] Rebuild
        mmap = self._populate(factory)
        
        #[] Test Basic Inclusion - differs Set-vs-List
        assert(mmap['a'] == set([1,2,4,8,16]))
        assert(mmap['b'] == set(['a','b','c']))
        assert(mmap['c'] == set([(2,3,1),(1,2,3),(3,3,2,4)]))
        
        #[] Test removal - - differs Set-vs-List
        mmap.remove('a',1)
        mmap.remove('a',2)
        mmap.remove('a',8)
        assert('a' in mmap)
        assert(2 not in mmap['a'])
        assert(mmap['a'] == set([4,16]))
        
        #[] Rebuild - to erase previous changes (simplicity)
        mmap = self._populate(factory)
        
        #[] Test MutableMap Mixin Methods - .keys(),.values(),.items()
        assert(set(mmap.keys()) == set(['a','b','c']))
        assert(set(['a','b','c']) in mmap.values())
        assert(('a',set([1,2,4,8,16])) in mmap.items())
        
        #[] Test MutableMap Mixin Methods - get/get(default)/setdefault 
        #assert(mmap.get('c') == [2,3,1])
        assert(mmap.get('c') == set([(2,3,1),(1,2,3),(3,3,2,4)]))    
        assert(not mmap.get('d'))       #mmap.get('d') --> Exception, which comes back as 'False' in assertions
        assert(mmap.get('d',[]) == [])
        assert(mmap.setdefault('e','matta') == set(['matta']))
        assert(mmap['e'] == set(['matta']))
        assert(mmap.setdefault('b',set(['c','c'])) == set(['a','b','c']))
        assert(mmap['b'] == set(['a','b','c']))

        #[] Test MutableMap Mixin Methods - clear,update,pop,popitem
        mmap.clear()
        assert(len(mmap) == 0)
        mmap.insert('f',[1,2,3,4,4,3,2])
        assert(mmap['f'] == set([1,2,3,4]))
        mmap.update({'a':set([1,2,2,3]),'b':set(['a','c','a','d'])})
        
        assert(mmap['a'] == set([1,2,3]))
        assert(mmap['b'] == set(['a','d','c']))
        assert(mmap.pop('b') == set(['a','d','c']))
        assert('b' not in mmap)
        assert(mmap.popitem() == ('a',set([1,2,3])))        #Remove a random item
        
        #[] Test Internal Objects - Set functions
        mmap = self._populate(factory)
        assert(all(elm in [1,2,4,8,16] for elm in mmap['a']))      #iteration on set
        assert(len(mmap['b']) == 3)
        
        assert(mmap['b'] < set(['a','b','c','d']))      #strict subset
        assert(mmap['b'] <= set(['a','b','c','d']))     #subset - is every element of mmap['b'] in set X
        assert(mmap['c'] > set([(2,3,1),(1,2,3)]))      #strict superset
        assert(mmap['a'] | mmap['b'] == set([1,2,4,8,16,'a','b','c']))
        assert(mmap['a'] & set([1,2,3,'q']) == set([1,2]))
        assert(mmap['b'] - set(['b','c']) == set(['a']))
        assert(mmap['b'] ^ set(['b','e']) == set(['a','c','e']))      #xor (^): all elements in exactly one of the two sets
                
        assert(mmap['a'].isdisjoint(set([32,64])))          #.isdisjoint() ~ A and B == set()
        superset = mmap['c']; superset.add((1,4))
        assert(not mmap['c'].isdisjoint(superset))
        
        
    def test_ListMultimap(self):
        factory = ListMultimap
        #[] Execute tests shared between multimap types
        self._shared(factory)
        
        
    def _shared(self,factory):
        mmap = self._populate(factory)
        #[] Test Basic Inclusion - shared
        assert('b' in mmap)
        assert('d' not in mmap)
        assert(2 in mmap['a'])
        assert(1 in mmap['a'])
        assert(3 not in mmap['a'])
        assert((2,3,1) in mmap['c'])
        assert(mmap['a'] != mmap['b'])
        assert(mmap == self._populate(factory))
        
        #[] Test removal - shared
        del mmap['b']
        assert('b' not in mmap)
        mmap.remove('a',1)
        assert(1 not in mmap['a'])
        
        #[] Test basic insertion
        
    def _populate(self,factory):
        mmap = factory()
        mmap['a'] = 1
        mmap['a'] = 2
        mmap['a'] = 4
        mmap['a'] = 4
        mmap['a'] = 8
        mmap['a'] = 8
        mmap['a'] = 8
        mmap['a'] = 16
        mmap['a'] = 16
        mmap['a'] = 16
        mmap['a'] = 16
        mmap['b'] = 'a'
        mmap['b'] = 'b'
        mmap['b'] = 'a'
        mmap['b'] = 'c'
        mmap['b'] = 'b'
        mmap['c'] = (2,3,1)
        mmap['c'] = (1,2,3)
        mmap['c'] = (3,3,2,4)
        return mmap



if __name__ == "__main__":
    
    suite= unittest.TestSuite()
    suite.addTest(TestMultimaps('test_SetMultimap'))
    suite.addTest(TestMultimaps('test_ListMultimap'))
    
    runner = unittest.TextTestRunner()
    runner.run(suite)