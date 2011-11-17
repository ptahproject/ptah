import threading
from datetime import timedelta
from ptah import config, form
from pyramid.interfaces import INewRequest

from ptah import token


class ThreadLocalManager(threading.local):

    def __init__(self):
        self.data = {}

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value

    def clear(self):
        self.data = {}

tldata = ThreadLocalManager()


@config.subscriber(INewRequest)
def resetThreadLocalData(ev):
    tldata.clear()


class CSRFService(object):
    """ csrf service for ptah.form """

    TOKEN_TYPE = token.TokenType(
        '1c49d2aacf844557a7aff3dbf09c0740', timedelta(minutes=30))

    def generate(self, data):
        t = token.service.get_bydata(self.TOKEN_TYPE, data)
        if t is not None:
            return t
        return token.service.generate(self.TOKEN_TYPE, data)

    def get(self, t):
        return token.service.get(t)

    def remove(self, t):
        return token.service.remove(t)

form.setCsrfUtility(CSRFService())


class Pagination(object):
    """ simple pagination """

    def __init__(self, page_size, left_neighbours=3, right_neighbours=3):
        self.page_size = page_size
        self.left_neighbours = left_neighbours
        self.right_neighbours = right_neighbours

    def offset(self, current):
        return (current - 1) * self.page_size, self.page_size

    def __call__(self, total, current):
        if not current:
            raise ValueError(current)

        size = int(round(total / float(self.page_size) + 0.4))

        pages = []

        first = 1
        last = size

        prevIdx = current - self.left_neighbours
        nextIdx = current + 1

        if first < current:
            pages.append(first)
        if first + 1 < prevIdx:
            pages.append(None)
        for i in range(prevIdx, prevIdx + self.left_neighbours):
            if first < i:
                pages.append(i)

        pages.append(current)

        for i in range(nextIdx, nextIdx + self.right_neighbours):
            if i < last:
                pages.append(i)
        if nextIdx + self.right_neighbours < last:
            pages.append(None)
        if current < last:
            pages.append(last)

        # prev/next idx
        prevLink = None if current <= 1 else current - 1
        nextLink = None if current >= size else current + 1

        return pages, prevLink, nextLink


@config.cleanup
def cleanup():
    tldata.clear()
