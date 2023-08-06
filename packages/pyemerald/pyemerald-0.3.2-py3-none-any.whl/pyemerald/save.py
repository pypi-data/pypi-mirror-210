"""
Module defining the a crude representation of the save file.
It handles reading and writing of the file
"""
from dataclasses import dataclass
from typing import List
from pyemerald.section import RawSection
from pyemerald.constants import (
    SLOT_SIZE,
    N_SECTIONS,
    SECTION_SIZE,
    HALL_OF_FAME_SIZE,
    MYSTERY_GIFT_SIZE,
    RECORDED_BATTLE_SIZE,
    HALL_OF_FAME_OFFSET,
    MYSTERY_GIFT_OFFSET,
    RECORDED_BATTLE_OFFSET,
)
from pyemerald.game import Game
from pyemerald.section import (
    BaseSection,
    SECTION_ID_TO_TYPE_MAPPING,
    TYPE_TO_SECTION_ID_MAPPING,
)


@dataclass
class Slot:
    """Class which corresponds to the bytes creating when saving
    a game. A save file contains two slots
    """

    sections: List[RawSection]
    save_index: int
    is_empty: bool

    @classmethod
    def from_bytes(cls, data: bytes) -> "Slot":
        """Instantiate a Slot from raw bytes"""

        sections = []
        for section in range(N_SECTIONS):
            section_offset = section * SECTION_SIZE

            raw_section = RawSection.from_bytes(
                data[section_offset : (section_offset + SECTION_SIZE)],
            )

            sections.append(raw_section)

        # Get save index from last section
        save_index = sections[-1].save_index

        is_empty = any([section.is_empty for section in sections])

        return cls(sections=sections, save_index=save_index, is_empty=is_empty)

    def to_bytes(self):
        """Convert slot to bytes"""

        if self.is_empty:
            return b"\xff".ljust(SLOT_SIZE, b"\xff")

        buffer = bytearray()

        for section in self.sections:

            buffer += section.to_bytes()

        return bytes(buffer)

    def to_game(self) -> Game:
        """Create Game object from the Slot"""
        relevant_sections = []
        for section in self.sections:
            in_mem_class = SECTION_ID_TO_TYPE_MAPPING[section.section_id]
            if in_mem_class is not None:
                relevant_sections.append(in_mem_class.from_raw_section(section))

        return Game(relevant_sections)

    def update_from_section(self, section: "BaseSection", section_id: int):
        """Update the content data of a RawSection based on a
        BaseSection"""

        relevant_sections = [s for s in self.sections if s.section_id == section_id]

        if len(relevant_sections) == 0:
            raise ValueError(f"Couldn't find section with {section_id=}")
        elif len(relevant_sections) == 1:
            relevant_sections[0].update_from_section(section)
        else:
            raise ValueError(f"Multiple RawSection's in Slot with {section_id=}")

    def __repr__(self):
        if self.is_empty:
            return "Slot()"
        else:
            rep = ", \n\t".join([f"\t{repr(s)}" for s in self.sections])
            rep = f"Slot(\n\t{rep})"
            return rep

    def get_section_by_id(self, section_id: int) -> RawSection:
        """Get the RawSection with a certain section id"""
        relevant_section = [
            section for section in self.sections if section.section_id == section_id
        ]

        if len(relevant_section) == 0:
            return None
        elif len(relevant_section) == 1:
            return relevant_section[0]
        else:
            raise ValueError(f"Multiple sections with {section_id=}")


@dataclass
class Save:
    """In memory representation of a save file"""

    slots: List[Slot]
    hall_of_fame: bytes
    mystery_gift: bytes
    recorded_battle: bytes
    updated: bool = False

    def __post_init__(self):
        if len(self.slots) > 2:
            raise ValueError("No more than two slots!")

    @classmethod
    def from_file(cls, path: str) -> "Save":
        with open(path, "rb") as f:
            data = f.read()

        slot0 = Slot.from_bytes(data[:SLOT_SIZE])
        slot1 = Slot.from_bytes(data[SLOT_SIZE : SLOT_SIZE * 2])

        hall_of_fame = data[
            HALL_OF_FAME_OFFSET : HALL_OF_FAME_OFFSET + HALL_OF_FAME_SIZE
        ]
        mystery_gift = data[
            MYSTERY_GIFT_OFFSET : MYSTERY_GIFT_OFFSET + MYSTERY_GIFT_SIZE
        ]
        recorded_battle = data[
            RECORDED_BATTLE_OFFSET : RECORDED_BATTLE_OFFSET + RECORDED_BATTLE_SIZE
        ]

        return Save(
            slots=[slot0, slot1],
            hall_of_fame=hall_of_fame,
            mystery_gift=mystery_gift,
            recorded_battle=recorded_battle,
        )

    def to_bytes(self) -> bytes:

        buffer = b""
        for slot in self.slots:
            buffer += slot.to_bytes()

        buffer += self.hall_of_fame
        buffer += self.mystery_gift
        buffer += self.recorded_battle

        return buffer

    def to_file(self, path: str):

        data = self.to_bytes()
        with open(path, "wb") as f:
            f.write(data)

    @property
    def most_recent_slot_index(self) -> int:
        save_index_0 = self.slots[0].save_index
        save_index_1 = self.slots[1].save_index

        if save_index_0 > save_index_1:
            return 0
        return 1

    @property
    def next_save_slot_index(self) -> int:
        most_recent = self.most_recent_slot_index
        if most_recent == 1:
            return 0
        return 1

    @property
    def next_save_slot(self) -> int:
        next_index = self.next_save_slot_index
        return self.slots[next_index]

    @property
    def current_slot(self) -> Slot:
        return self.slots[self.most_recent_slot_index]

    def update_from_game(self, game: Game):

        if self.updated:
            raise ValueError("Can only call 'update_from_game' once before saving!")

        slot = self.current_slot

        for section in game.sections:
            # Get ID corresponding to child of BaseSection
            section_id = TYPE_TO_SECTION_ID_MAPPING[type(section)]

            slot.update_from_section(section=section, section_id=section_id)

        # Increment slot save index. NB: This means update_from_game can only be called once!
        # slot.save_index += 2
        self.updated = True

    def to_game(self) -> Game:
        return self.current_slot.to_game()

    def __repr__(self):
        rep = f"Save(\n\tslot0={repr(self.slots[0])},\n\tslot1={repr(self.slots[1])}\n)"

        return rep
