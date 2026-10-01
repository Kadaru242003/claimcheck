from solution import find_index

class CountingSeq:
    """A read-only sequence that counts every element read. No list methods to bypass."""
    reads = 0
    def __init__(self, n):
        self.__n = n
    def __len__(self):
        return self.__n
    def __getitem__(self, i):
        if not 0 <= i < self.__n:
            raise IndexError(i)
        CountingSeq.reads += 1
        return (i * 7) % self.__n  # a scrambled permutation of 0..n-1
    def __iter__(self):
        for i in range(self.__n):
            yield self[i]

def test_finds_last_element_with_few_reads():
    CountingSeq.reads = 0
    assert find_index(CountingSeq(1000), 993) == 999  # value 993 sits at index 999
    assert CountingSeq.reads <= 3

def test_missing():
    CountingSeq.reads = 0
    assert find_index(CountingSeq(1000), -5) == -1
    assert CountingSeq.reads <= 3
