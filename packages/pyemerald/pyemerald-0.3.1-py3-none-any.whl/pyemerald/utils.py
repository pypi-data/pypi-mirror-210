"""Utility functions for testing"""
from pyemerald.codec import Codec


def print_bytes(val: bytes):
    res = ""
    for v in val:
        res += f"\\x{v:02x}"
    print(res)


def compare_bytes_by_codec(data_a: bytes, data_b: bytes, codec: Codec):
    """Compare data_a and data_b by the byte ranges as defined by
    the codec

    Returns
    -------
    List[Tuple[str, bool, Optional[List[int]]]]
        A list of tuples where the first entry is the name of the
        field, second entry whether the bytes from a and b are
        identical and lastly a list of indices where there are
        mismatches if the aren't identical
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
