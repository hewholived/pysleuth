
class Set(set):
    def get(self):
        '''Non-destructively retrieve an item from the set.'''
        # This is a bit ugly, but it's all we have to work with!
        item = self.pop()
        self.add(item)
        return item

    def __add__(self, other_set):
        '''Convenience operator for getting the union of sets.'''
        assert isinstance(other_set, set), other_set
        return self.union(other_set)

    def __subtract__(self, other_set):
        '''Convenience operator for getting the difference of sets.'''
        assert isinstance(other_set, set), other_set
        return self.difference(other_set)
