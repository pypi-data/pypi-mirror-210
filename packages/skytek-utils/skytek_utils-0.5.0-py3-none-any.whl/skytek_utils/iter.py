from itertools import chain, islice


def chunks(iterable, chunk_size):
    iterator = iter(iterable)
    for first in iterator:
        yield chain([first], islice(iterator, chunk_size - 1))
