"""
Module implementing a base codec which can be used to 
serialize or deserialize objects into the Pokemon save
file format.
"""
from typing import Union, List, Dict, Optional
from dataclasses import dataclass

BYTE_TO_STR = {
    0x00: " ",
    0xA1: "0",
    0xA2: "1",
    0xA3: "2",
    0xA4: "3",
    0xA5: "4",
    0xA6: "5",
    0xA7: "6",
    0xA8: "7",
    0xA9: "8",
    0xAA: "9",
    0xAB: "!",
    0xAC: "?",
    0xAD: ".",
    0xAE: "-",
    0xB0: "...",
    0xB1: "“",
    0xB2: "”",
    0xB3: "‘",
    0xB4: "’",
    0xB5: "♂",
    0xB6: "♀",
    0xB8: ",",
    0xBA: "/",
    0xBB: "A",
    0xBC: "B",
    0xBD: "C",
    0xBE: "D",
    0xBF: "E",
    0xC0: "F",
    0xC1: "G",
    0xC2: "H",
    0xC3: "I",
    0xC4: "J",
    0xC5: "K",
    0xC6: "L",
    0xC7: "M",
    0xC8: "N",
    0xC9: "O",
    0xCA: "P",
    0xCB: "Q",
    0xCC: "R",
    0xCD: "S",
    0xCE: "T",
    0xCF: "U",
    0xD0: "V",
    0xD1: "W",
    0xD2: "X",
    0xD3: "Y",
    0xD4: "Z",
    0xD5: "a",
    0xD6: "b",
    0xD7: "c",
    0xD8: "d",
    0xD9: "e",
    0xDA: "f",
    0xDB: "g",
    0xDC: "h",
    0xDD: "i",
    0xDE: "j",
    0xDF: "k",
    0xE0: "l",
    0xE1: "m",
    0xE2: "n",
    0xE3: "o",
    0xE4: "p",
    0xE5: "q",
    0xE6: "r",
    0xE7: "s",
    0xE8: "t",
    0xE9: "u",
    0xEA: "v",
    0xEB: "w",
    0xEC: "x",
    0xED: "y",
    0xEE: "z",
    0xFF: "",
}


STR_TO_BYTE = {v: k for k, v in BYTE_TO_STR.items()}


def bytes_to_str(val: bytes) -> str:
    res = ""
    for b in val:
        if b == 255:
            break
        res += BYTE_TO_STR[b]
    return res


def str_to_bytes(val: str) -> bytes:
    return bytes([STR_TO_BYTE[x] for x in val])


def bytes_to_int(val: bytes) -> int:
    return int.from_bytes(val, byteorder="little")


def int_to_bytes(val: int, length: int) -> bytes:
    _bytes = int.to_bytes(val, length, byteorder="little")
    return _bytes


class ByteDeltaField:
    """Class which holds the actual value to be converted
    and the corresponding ByteFieldCodec of that value"""

    def __init__(self, value: Union[str, int, bytes], field_codec: "ByteFieldCodec"):
        self.value = value
        self.field_codec = field_codec

    def to_bytes(self):
        return self.field_codec.to_bytes(self.value)

    def __repr__(self) -> str:
        res = f"{self.__class__.__name__}(value={repr(self.value)}, field_codec={self.field_codec})"
        return res


class ByteDelta:
    """Class which holds the data that should be changed in
    the save file along with information about how to serialize
    it"""

    def __init__(self, delta_fields: List[ByteDeltaField]):
        self.delta_fields = delta_fields

    def to_bytes(self, original_bytes: bytes) -> bytes:
        """Insert relevant bytes at the right offsets into the
        original bytes"""

        # Convert to bytearray
        buffer = bytearray(original_bytes)

        for field in self.delta_fields:

            # Create new bytes
            field_bytes = field.to_bytes()

            if len(field_bytes) < field.field_codec.size:
                field_bytes = field_bytes.ljust(field.field_codec.size, b"\x00")

            # Insert into buffer at correct position
            buffer[
                field.field_codec.offset : field.field_codec.offset
                + field.field_codec.size
            ] = field_bytes

        return bytes(buffer)

    @classmethod
    def from_section(cls, section: "BaseSection") -> "ByteDelta":

        fields = ByteDelta._recurse_create_byte_delta_fields(section, [])
        return ByteDelta(fields)

    @staticmethod
    def _recurse_create_byte_delta_fields(
        _object: "Serializable", field_container: List, offset: int = 0
    ) -> List[ByteDeltaField]:

        for field in _object.codec.fields:

            # Check for simple value
            value = getattr(_object, field.name)

            if isinstance(value, Serializable):
                # Check if object has bespoke logic
                # for creating ByteDelta

                if hasattr(value, "to_byte_delta_bespoke"):
                    field_container.extend(
                        value.to_byte_delta_bespoke(offset + field.offset)
                    )
                else:
                    field_container.extend(
                        ByteDelta._recurse_create_byte_delta_fields(
                            value, [], offset + field.offset
                        )
                    )
            elif isinstance(value, list):
                # If the value is a list create byte delta fields from each element
                loop_offset = 0
                for child in value:
                    field_container.extend(
                        ByteDelta._recurse_create_byte_delta_fields(
                            child, [], offset + field.offset + loop_offset
                        )
                    )
                    loop_offset += child.codec.size
            else:
                # Add offset
                field.add_offset(offset)
                field_container.append(ByteDeltaField(value=value, field_codec=field))

        return field_container

    def __len__(self):
        return len(self.delta_fields)

    def __repr__(self) -> str:
        name = f"{self.__class__.__name__}"
        fields = ",\n".join([repr(x) for x in self.delta_fields])
        res = f"{name}(\ndelta_fields={fields})"
        return res


class ByteFieldCodec:
    """Class which defines the the location and size of a
    value to be extracted and the corresponding type. Is
    also used when deserializing a value back to bytes."""

    def __init__(
        self,
        name: str,
        data_type: Union[str, int, bytes],
        offset: int,
        size: int,
        value_map: Optional[Dict[int, str]] = None,
        reverse_value_map: Optional[Dict[int, str]] = None,
        deserialize_skip: bool = False,
    ):
        """deserialize_skip if this is True when creating object from bytes it will
        just set the raw bytes on the given attribute. If False (which is default)
        it will deserialize as specified"""
        self.name = name
        self.data_type = data_type
        self.offset = offset
        self.size = size
        self.value_map = value_map
        self.reverse_value_map = reverse_value_map
        self.deserialize_skip = deserialize_skip

        if (self.value_map is not None and self.reverse_value_map is None) or (
            self.value_map is None and self.reverse_value_map is not None
        ):
            raise ValueError(
                "Both value_map and reverse_value_map must be set on ByteFieldCode"
            )

    def to_value(self, data: bytes) -> Union[str, int, bytes]:
        """Convert bytes to a typed python value"""

        blob = data[self.offset : self.offset + self.size]

        if self.deserialize_skip:
            return blob
        else:

            if self.data_type is int:
                value = bytes_to_int(blob)
            elif self.data_type is str:
                value = bytes_to_str(blob)
            elif self.data_type is bytes:
                value = blob
            elif isinstance(self.data_type, type(Serializable)):
                # Let the object itself deserialize the bytes to a value
                value = self.data_type.from_bytes(data)
            else:
                raise ValueError(f"Invalid type {self.data_type=}")

            if self.value_map is not None:
                return self.value_map[value]
            else:
                return value

    def to_bytes(self, value: Union[str, int]) -> bytes:
        """Convert a value to bytes"""
        if self.value_map is not None:
            value = self.reverse_value_map[value]

        if self.data_type is int:
            return int_to_bytes(value, self.size)
        elif self.data_type is str:
            raw_bytes = str_to_bytes(value)

            # Pad to size
            _bytes = raw_bytes.ljust(self.size, b"\xff")
            return _bytes
        elif self.data_type is bytes:
            return value
        elif self.data_type is list:
            # Assumes data has been converted into bytes already!
            if isinstance(value, bytes):
                return value
            else:
                raise ValueError(
                    "Can't turn list into bytes! Please convert value to bytes manually!"
                )
        else:
            raise ValueError(f"Type {self.data_type} is not supported!")

    def add_offset(self, offset):
        self.offset += offset

    def __repr__(self) -> str:
        value_map_size = None if self.value_map is None else len(self.value_map)
        reverse_value_map_size = (
            None if self.reverse_value_map is None else len(self.reverse_value_map)
        )
        res = (
            f"{self.__class__.__name__}("
            f"name={self.name}, "
            f"data_type={self.data_type}, "
            f"offset={self.offset}, "
            f"size={self.size}, "
            f"value_map={value_map_size}, "
            f"reverse_value_map={reverse_value_map_size}, "
            f"deserialize_skip={self.deserialize_skip})"
        )
        return res


class Codec:
    """The main class controlling how values are serialized and deserialized
    to/from the pokemon save format"""

    def __init__(self, fields: List[ByteFieldCodec], output_size: Optional[int] = None):
        """fields are the ByteFieldCodec object to use for the codec,
        output size is used when serializing to bytes, in order to
        determine the total length of the output bytes. This will add
        padding if the data doesnt fill the entire size.
        """
        self.fields = fields
        self.output_size = output_size

    def to_values(self, data: bytes) -> Dict[str, Union[str, int]]:
        """Convert data to dict of values using the ByteFieldCodec
        fields defined in the codec"""
        res = {}
        for field in self.fields:
            res[field.name] = field.to_value(data)

        return res

    def to_object(self, data: bytes) -> "Object":
        """Create instance of a object based on the bytes data"""
        values = self.to_values(data)
        object_class = self.object_class

        return object_class(**values)

    def to_bytes(self, _object: object) -> bytes:
        """Take an object and serialize it using the codec.
        It has to have attribute values corresponding to
        ByteFieldCodec values"""

        # Order by offset
        sorted_fields = sorted(self.fields, key=lambda x: x.offset)

        buffer = bytearray()

        for field in sorted_fields:

            # Pad buffer up to the current offset
            buffer = buffer.ljust(field.offset, b"\x00")

            # Get value from _object
            value = getattr(_object, field.name)
            field_bytes = field.to_bytes(value)

            if len(field_bytes) < field.size:
                field_bytes = field_bytes.ljust(field.size, b"\x00")

            buffer += field_bytes

        if self.output_size is not None:
            buffer = buffer.ljust(self.output_size, b"\x00")

        return bytes(buffer)

    @property
    def size(self) -> int:
        """Return the number of bytes taken up when using the
        codec to convert data to bytes"""
        sort_fields = sorted(self.fields, key=lambda x: x.offset)
        res = sort_fields[-1].offset + sort_fields[-1].size
        return res

    def __repr__(self):
        res = f"{self.__class__.__name__}({repr(self.fields)})"
        return res

    def get_field_by_name(self, name: str) -> ByteFieldCodec:
        return [field for field in self.fields if field.name == name][0]


@dataclass
class Serializable:
    """Class which can be inherited from in order to
    get convenience methods for working with the codec"""

    @property
    def codec(self) -> Codec:
        return self._codec(type(self))

    @classmethod
    def from_bytes(cls, data: bytes):
        return cls._codec(cls).to_object(data)

    def to_bytes(self) -> bytes:
        return self.codec.to_bytes(self)
