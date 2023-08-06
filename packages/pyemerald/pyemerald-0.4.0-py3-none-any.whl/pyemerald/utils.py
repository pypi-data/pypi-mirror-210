"""Utility functions for testing"""
from pyemerald.codec import Codec


def format_bytes(val: bytes) -> str:
    res = ""
    for v in val:
        res += f"\\x{v:02x}"
    return res


def print_bytes(val: bytes):
    print(format_bytes(val))


def compare_bytes_by_codec(data_a: bytes, data_b: bytes, codec: Codec):
    """Compare data_a and data_b by the byte ranges as defined by
    the codec

    Returns
    -------
    List[Tuple[str, bool, Optional[List[int]]]]
        A list of tuples where the first entry is the name of the
        field, second entry whether the bytes from a and b are
        identical and lastly a list of indices where there are
        mismatches if they aren't identical
    """

    res = []
    for field in codec.fields:
        cur_a = data_a[field.offset : field.offset + field.size]
        cur_b = data_b[field.offset : field.offset + field.size]
        if cur_a == cur_b:
            res.append((field.name, True))
        else:
            miss_idx = []
            for i in range(len(cur_a)):
                if cur_a[i] != cur_b[i]:
                    miss_idx.append(i)
            res.append((field.name, False, miss_idx))
    return res


def are_bytes_equal_by_codec(data_a: bytes, data_b: bytes, codec: Codec):
    res = compare_bytes_by_codec(data_a, data_b, codec)
    return all([x[1] for x in res])


def get_bits_by_position(number, pos, size, total_bits=32) -> int:
    """Function to get a specific bit range in a number
    and return the number it corresponds to.

    Parameters
    ----------
    number: int
        The number which the bits will be extracted from
    pos: int
        The bit position of interest, indexing right to left.
        The position should be 1-indexed, meaning the rightmost
        bit is considered to be index 1.
        E.g it could be the bit at index 4
    size: int
        The number of bits to extract from pos going right.
    total_bits: int
        The bit size of number. Usually 32 bit.

    Examples
    --------
    # Get the the bits in position 4 and 3
    >>> bin(get_bits_by_position(0b10101101, pos=4, size=2, total_bits = 8))
    0b11
    # Get the bits in position 6, 5 and 4
    >>> bin(get_bits_by_position(0b10101101, pos=6, size=3, total_bits = 8))
    0b101

    """
    # Push relevant bits to be the first (Least Significant Bits)
    pushed = number >> (pos - size)

    # Get the first "size" bits counting right to left
    cut = pushed & (2**size - 1)

    return cut
