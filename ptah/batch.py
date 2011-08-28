##############################################################################
#
# Copyright (c) 2003-2007 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Batching Implementation"""


class Batch(object):
    """A Batch represents a sub-list of the full sequence.

    The Batch constructor takes a list (or any list-like object) of elements,
    a starting index and the size of the batch. From this information all
    other values are calculated.
    """

    def __init__(self, sequence, start=0, size=20, batches=None):
        self.sequence = sequence

        length = len(sequence)
        self.update(length, start, size)
        self.updateBatches(batches)

    def update(self, length, start, size):
        self._length = length
        self.start = start
        if length == 0:
            self.start = -1
        elif start >= length:
            raise IndexError('start index key out of range')

        self.size = size
        self._trueSize = size
        if start + size >= length:
            self._trueSize = length - start

        # See interfaces.IBatch
        if length == 0:
            self.end = -1
        else:
            self.end = start + self._trueSize - 1

    def updateBatches(self, batches):
        if batches is None:
            batches = Batches(self)

        self.batches = batches

    @property
    def index(self):
        return self.start / self.size

    @property
    def number(self):
        return self.index + 1

    @property
    def total(self):
        total = self._length / self.size
        if self._length % self.size:
            total += 1
        return total

    @property
    def next(self):
        try:
            return self.batches[self.index + 1]
        except IndexError:
            return None

    @property
    def previous(self):
        idx = self.index - 1
        if idx >= 0:
            return self.batches[idx]
        return None

    @property
    def firstElement(self):
        return self.sequence[self.start]

    @property
    def lastElement(self):
        return self.sequence[self.end]

    def __getitem__(self, key):
        if key >= self._trueSize:
            raise IndexError('batch index out of range')
        return self.sequence[self.start + key]

    def __iter__(self):
        return iter(self.sequence[self.start: self.end + 1])

    def __len__(self):
        return self._trueSize

    def __contains__(self, item):
        for i in self:
            if item == i:
                return True
        else:
            return False

    def __getslice__(self, i, j):
        if j > self.end:
            j = self._trueSize

        return [self[idx] for idx in range(i, j)]

    def __eq__(self, other):
        return ((self.size, self.start, self.sequence) ==
                (other.size, other.start, other.sequence))

    def __ne__(self, other):
        return not self.__eq__(other)

    def __nonzero__(self):
        return self._trueSize != 0

    def __repr__(self):
        return '<%s start=%i, size=%i>' % (
            self.__class__.__name__, self.start, self.size)


class Batches(object):
    """A sequence object representing all the batches. Used by a Batch."""

    def __init__(self, batch):
        self.size = batch.size
        self.total = batch.total
        self.sequence = batch.sequence
        self._batches = {batch.index: batch}

    def __len__(self):
        return self.total

    def __getitem__(self, key):
        if key not in self._batches:
            if key < 0:
                key = self.total + key

            batch = Batch(
                self.sequence, key * self.size, self.size, self)
            self._batches[batch.index] = batch

        try:
            return self._batches[key]
        except KeyError:
            raise IndexError(key)

    def __getslice__(self, i, j):
        j = min(j, self.total)
        return [self[idx] for idx in range(i, j)]


def first_neighbours_last(batches, currentBatchIdx, nb_left, nb_right):
    """Build a sublist from a large batch list.

    This is used to display batch links for a large table.

    arguments:
     * batches: a large sequence (may be a batches as well)
     * currentBatchIdx: index of the current batch or item
     * nb_left: number of neighbours before the current batch
     * nb_right: number of neighbours after the current batch

    The returned list gives:
     * the first batch
     * a None separator if necessary
     * left neighbours of the current batch
     * the current batch
     * right neighbours of the current batch
     * a None separator if necessary
     * the last batch

    Example:

      >>> from batch import first_neighbours_last as f_n_l
      >>> batches = range(100) # it works with real batches as well

    We try to get subsets at different levels:

      >>> for i in range(0,6):
      ...    f_n_l(batches, i, 2, 2)
      [0, 1, 2, None, 99]
      [0, 1, 2, 3, None, 99]
      [0, 1, 2, 3, 4, None, 99]
      [0, 1, 2, 3, 4, 5, None, 99]
      [0, None, 2, 3, 4, 5, 6, None, 99]
      [0, None, 3, 4, 5, 6, 7, None, 99]

      >>> for i in range(93, 99):
      ...    f_n_l(batches, i, 2, 2)
      [0, None, 91, 92, 93, 94, 95, None, 99]
      [0, None, 92, 93, 94, 95, 96, None, 99]
      [0, None, 93, 94, 95, 96, 97, None, 99]
      [0, None, 94, 95, 96, 97, 98, 99]
      [0, None, 95, 96, 97, 98, 99]
      [0, None, 96, 97, 98, 99]

    Try with no previous and no next batch:

      >>> f_n_l(batches, 0, 0, 0)
      [0, None, 99]
      >>> f_n_l(batches, 1, 0, 0)
      [0, 1, None, 99]
      >>> f_n_l(batches, 2, 0, 0)
      [0, None, 2, None, 99]

    Try with only 1 previous and 1 next batch:

      >>> f_n_l(batches, 0, 1, 1)
      [0, 1, None, 99]
      >>> f_n_l(batches, 1, 1, 1)
      [0, 1, 2, None, 99]
      >>> f_n_l(batches, 2, 1, 1)
      [0, 1, 2, 3, None, 99]
      >>> f_n_l(batches, 3, 1, 1)
      [0, None, 2, 3, 4, None, 99]

    Try with incoherent values:

      >>> f_n_l(batches, 0, -4, -10)
      Traceback (most recent call last):
      ...
      AssertionError
      >>> f_n_l(batches, 2000, 3, 3)
      Traceback (most recent call last):
      ...
      AssertionError
    """
    sublist = []
    # setup some batches and indexes
    firstIdx = 0
    lastIdx = len(batches) - 1
    #print currentBatchIdx >= 0,  currentBatchIdx <= lastIdx
    #assert(currentBatchIdx >= 0 and currentBatchIdx <= lastIdx)
    assert(nb_left >= 0 and nb_right >= 0)
    prevIdx = currentBatchIdx - nb_left
    nextIdx = currentBatchIdx + 1
    firstBatch = batches[0]
    lastBatch = batches[len(batches)-1]

    # add first batch
    if firstIdx < currentBatchIdx:
        sublist.append(firstBatch)

    # there must probably be space
    if firstIdx + 1 < prevIdx:
        # we skip batches between first batch and first previous batch
        sublist.append(None)

    # add previous batches
    for i in range(prevIdx, prevIdx + nb_left):
        if firstIdx < i:
            # append previous batches
            sublist.append(batches[i])

    # add current batch
    sublist.append(batches[currentBatchIdx])

    # add next batches
    for i in range(nextIdx, nextIdx + nb_right):
        if i < lastIdx:
            # append previous batch
            sublist.append(batches[i])

    # there must probably be space
    if nextIdx + nb_right < lastIdx:
        # we skip batches between last batch and last next batch
        sublist.append(None)

    # add last batch
    if currentBatchIdx < lastIdx:
        sublist.append(lastBatch)
    return sublist
