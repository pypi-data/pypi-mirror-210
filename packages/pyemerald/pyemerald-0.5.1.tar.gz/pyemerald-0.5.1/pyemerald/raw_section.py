"""
This module contains the raw section data as described in Bulbapedia.
The content data for each section is stored as raw bytes and can be
used to instantiate actual sections which use the content data"""
from dataclasses import dataclass
from typing import ClassVar
from pyemerald.codec import bytes_to_int, Codec, ByteFieldCodec
from pyemerald.constants import SAVE_INDEX_EMPTY, CHECKSUM_STEP_SIZE


class RawSectionCodec(Codec):
    def __init__(self):
        fields = [
            ByteFieldCodec("content_data", bytes, 0, 3968),
            ByteFieldCodec("section_id", int, 4084, 2),
            ByteFieldCodec("checksum", int, 4086, 2),
            ByteFieldCodec("signature", int, 4088, 4),
            ByteFieldCodec("raw_save_index", int, 4092, 4),
        ]
        self.object_class = RawSection
        super().__init__(fields)


@dataclass
class RawSection:
    """RawSection is the raw data 4096 bytes of a section, content data
    is stored as raw bytes"""

    content_data: bytes
    section_id: int
    signature: int
    raw_save_index: int
    checksum: int
    codec: ClassVar[Codec] = RawSectionCodec

    @property
    def is_empty(self) -> bool:
        raw_save_index = self.raw_save_index
        if raw_save_index == SAVE_INDEX_EMPTY:
            return True
        return False

    @property
    def save_index(self) -> int:

        save_index = self.raw_save_index
        if save_index == SAVE_INDEX_EMPTY:
            save_index = 0

        return save_index

    @staticmethod
    def calc_checksum(data, size, step_size: int = CHECKSUM_STEP_SIZE) -> int:
        chksum = 0
        if size % step_size != 0:
            raise ValueError("Length issue on data")

        n = int(size / step_size)

        for i in range(n):
            d = bytes_to_int(data[(step_size * i) : (step_size * (i + 1))])
            chksum += d

        # Truncate to 32 bit/4 byte (1 byte is two "characters")
        # See link: https://stackoverflow.com/questions/26771792/python-truncating-to-32-bit
        chksum_trunc = chksum & 0xFFFFFFFF

        # Calculating hexadecimal value using function
        # chksum_up_low = int(chksum_trunc[:4], 16) + int(chksum_trunc[-4:], 16)
        chksum_low = chksum_trunc & 0xFFFF
        chksum_high = (
            chksum_trunc >> 16
        )  # Move the top 4 bytes 4 places (1 place = 4 bits) to the right
        chksum_up_low = chksum_high + chksum_low

        # Truncate to 2 bytes
        chksum_res = chksum_up_low & 0xFFFF

        # Convert back to int
        # chksum_res = int(chksum_trunc_2, 16)

        return chksum_res

    @property
    def content_data_size(self) -> int:

        size_map = {
            0: 3884,
            1: 3968,
            2: 3968,
            3: 3968,
            4: 3848,
            5: 3968,
            6: 3968,
            7: 3968,
            8: 3968,
            9: 3968,
            10: 3968,
            11: 3968,
            12: 3968,
            13: 2000,
        }
        return size_map[self.section_id]

    @property
    def checksum(self) -> int:
        return RawSection.calc_checksum(
            self.content_data, self.content_data_size, CHECKSUM_STEP_SIZE
        )

    @checksum.setter
    def checksum(self, value):
        self.raw_checksum = value

    @classmethod
    def from_bytes(cls, data: bytes) -> "RawSection":
        return cls.codec().to_object(data)

    def to_bytes(self) -> "RawSection":
        """Create instance of codec and serizalize
        self to bytes"""
        return self.codec().to_bytes(self)

    def update_from_section(self, section: "BaseSection"):
        """Update the internal byte content data with values from
        a BaseSection. This is done using a delta, instead
        of generating the whole buffer from the BaseSection."""

        byte_delta = section.to_byte_delta()

        new_content_data = byte_delta.to_bytes(self.content_data)
        buffer_size = len(new_content_data)

        if buffer_size != len(self.content_data):
            raise ValueError(
                f"Expected {buffer_size=} got buffer_size={len(self.content_data)}"
            )

        self.content_data = new_content_data

    def __repr__(self):
        rep = (
            f"RawSection(content_data={len(self.content_data)}, "
            f"section_id={self.section_id}, "
            f"signature={self.signature}, "
            f"save_index={self.save_index},"
            f"checksum={self.checksum})"
        )
        return rep
