import unittest

from ghini_tree_position import Heap

class HeapTest(unittest.TestCase):
    def test_init(self):
        i = Heap([{'prio':1},{'prio':2},{'prio':3}])
        print(dir(self))
        self.assertEquals(i.priorities(), [3, 1, 2])
        i = Heap([{'prio':1},{'prio':2},{'prio':3},{'prio':4},{'prio':5}])
        self.assertEquals(i.priorities(), [5, 4, 2, 1, 3])
        i = Heap([{'prio':1},{'prio':3},{'prio':2},{'prio':4},{'prio':5}])
        self.assertEquals(i.priorities(), [5, 4, 2, 1, 3])
        i = Heap([{'prio':1},{'prio':2},{'prio':3},{'prio':4},{'prio':5},{'prio':7}])
        self.assertEquals(i.priorities(), [7, 4, 5, 1, 3, 2])

    def test_push(self):

        i = Heap([{'prio':1},{'prio':2},{'prio':3},{'prio':4},{'prio':5},{'prio':7}])
        i.push({'prio': 8})
        self.assertEquals(i.pop(), {'prio': 8})
        i.push({'prio': 6})
        self.assertEquals(i.pop(), {'prio': 7})
        self.assertEquals(i.pop(), {'prio': 6})

    def test_pop(self):

        i = Heap([{'prio':1},{'prio':2},{'prio':3},{'prio':4},{'prio':5},{'prio':7}])
        self.assertEquals(i.pop(), {'prio': 7})
        self.assertEquals(i.pop(), {'prio': 5})
        self.assertEquals(i.pop(), {'prio': 4})
        self.assertEquals(i.pop(), {'prio': 3})
        self.assertEquals(i.pop(), {'prio': 2})
        self.assertEquals(i.pop(), {'prio': 1})
        self.assertEquals(len(i.priorities()), 0)

        a, b, c, d, e, f = ({'prio':1},{'prio':2},{'prio':3},{'prio':4},{'prio':5},{'prio':7})
        i = Heap([f, e, b, c, d, a])
        self.assertEquals(i.priorities(), [7, 5, 2, 3, 4, 1])
        self.assertEquals(i.pop(), {'prio': 7})
        self.assertEquals(i.priorities(), [5, 4, 2, 3, 1])
        self.assertEquals(i.pop(), {'prio': 5})
        self.assertEquals(i.priorities(), [4, 3, 2, 1])

    def test_reprioritize(self):

        a, b, c, d, e, f = ({'prio':1},{'prio':2},{'prio':3},{'prio':4},{'prio':5},{'prio':7})
        i = Heap([a, b, c, d, e, f])

        ## nothing happens if the priority change is zero
        self.assertEquals(i.priorities(), [7, 4, 5, 1, 3, 2])
        i.reprioritize(a, 0)
        self.assertEquals(i.priorities(), [7, 4, 5, 1, 3, 2])

        ## the priority change default value is the positive unit. you specify
        ## the object of which the priority has to be altered.
        a, b, c, d, e, f = ({'prio':1},{'prio':2},{'prio':3},{'prio':4},{'prio':5},{'prio':7})
        i = Heap([a, b, c, d, e, f])
        self.assertEquals(i.priorities(), [7, 4, 5, 1, 3, 2])
        i.reprioritize(a)
        self.assertEquals(i.priorities(), [7, 4, 5, 2, 3, 2])
        i.reprioritize(a)
        self.assertEquals(i.priorities(), [7, 4, 5, 3, 3, 2])
        i.reprioritize(a)
        self.assertEquals(i.priorities(), [7, 4, 5, 4, 3, 2])
        i.reprioritize(a)
        self.assertEquals(i.priorities(), [7, 5, 5, 4, 3, 2])
        self.assertEquals(a, {'heappos': 1, 'prio': 5})

        ## you can give any value for the desired priority change.
        a, b, c, d, e, f = ({'prio':1},{'prio':2},{'prio':3},{'prio':4},{'prio':5},{'prio':7})
        i = Heap([a, b, c, d, e, f])
        self.assertEquals(i.priorities(), [7, 4, 5, 1, 3, 2])
        i.reprioritize(c, 8)
        self.assertEquals(i.priorities(), [11, 7, 5, 1, 4, 2])
        i.reprioritize(e, 15)
        self.assertEquals(i.priorities(), [20, 7, 11, 1, 4, 2])

        ## a negative priority change will sink the object into the heap
        i.reprioritize(e, -20)
        self.assertEquals(i.priorities(), [11, 7, 2, 1, 4, 0])
        i.reprioritize(c, -12)
        self.assertEquals(i.priorities(), [7, 4, 2, 1, -1, 0])

    def test_swap(self):
        i = Heap([{'prio':1},{'prio':2},{'prio':3}])
        self.assertEquals(i.priorities(), [3, 1, 2])
        i._swap(0, 1)
        self.assertEquals(i.priorities(), [1, 3, 2])

        
