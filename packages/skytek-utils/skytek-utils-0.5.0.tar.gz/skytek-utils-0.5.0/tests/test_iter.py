import pytest

from skytek_utils.iter import chunks


# fmt: off
@pytest.mark.parametrize("input_size, chunk_size, expected_chunks", [
    (30, 10, (10, 10, 10,)),
    (29, 10, (10, 10, 9,)),
    (31, 10, (10, 10, 10, 1,)),
])
# fmt: on
def test_chunks_sizes(input_size, chunk_size, expected_chunks):
    input_generator = range(input_size)
    chunk_sizes = []

    for chunk in chunks(input_generator, chunk_size):
        chunk_sizes.append(len(list(chunk)))

    assert tuple(chunk_sizes) == tuple(expected_chunks)
    assert sum(chunk_sizes) == input_size


# fmt: off
@pytest.mark.parametrize("input_size, chunk_size, expected_chunks", [
    (30, 10, (45, 145, 245,)),
    (29, 10, (45, 145, 216,)),
    (31, 10, (45, 145, 245, 30,)),
])
# fmt: on
def test_chunks_values(input_size, chunk_size, expected_chunks):
    input_generator = range(input_size)
    chunk_sums = []

    for chunk in chunks(input_generator, chunk_size):
        chunk_sums.append(sum(chunk))

    assert tuple(chunk_sums) == tuple(expected_chunks)
    assert sum(chunk_sums) == sum(range(input_size))
