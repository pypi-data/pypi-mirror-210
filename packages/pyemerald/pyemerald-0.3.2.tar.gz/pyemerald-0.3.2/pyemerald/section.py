"""
Module containing implementations of sections which have
their content data deserialized. Thus it is possible to modify
these classes and serialized them back to bytes. This should
be done through the Game class
"""
from dataclasses import dataclass
import copy
from typing import ClassVar, Type, List
from pyemerald.codec import (
    Codec,
    ByteFieldCodec,
    Serializable,
    ByteDelta,
)
from pyemerald.raw_section import RawSection
from pyemerald.constants import (
    BYTES_PER_PARTY_POKEMON,
    BYTES_PER_PC_POKEMON,
    RAW_SECTION_DATA_CONTENT_SIZE,
    PC_ITEM_COUNT,
    ITEM_SIZE,
)
from pyemerald.pokemon import Pokemon, PCPokemon
from pyemerald.items import Item, ITEM_INDEX_TO_NAME

######## Codecs ########
class TrainerInfoCodec(Codec):
    def __init__(self, section_class: Type["Serializable"]):
        fields = [
            ByteFieldCodec("name", str, 0, 7),
            ByteFieldCodec("gender", int, 8, 1),
            ByteFieldCodec("unused", int, 9, 1),
            ByteFieldCodec("trainer_id", int, 10, 4),
            ByteFieldCodec("time_played", int, 14, 5),
            ByteFieldCodec("options", int, 19, 3),
            ByteFieldCodec("security_key", int, 172, 4),
        ]
        self.object_class = section_class
        super().__init__(fields, output_size=RAW_SECTION_DATA_CONTENT_SIZE)


class TeamItemSectionCodec(Codec):
    def __init__(self, section_class: Type["Serializable"]):
        fields = [
            ByteFieldCodec("team_size", int, 564, 4),
            ByteFieldCodec("party", list, 568, 600, deserialize_skip=True),
            ByteFieldCodec("money", int, 1168, 4),
            ByteFieldCodec("coins", int, 1172, 2),
            ByteFieldCodec("pc_items", list, 1176, 200, deserialize_skip=True),
            ByteFieldCodec("item_pocket", int, 1376, 120),
            ByteFieldCodec("key_item_pocket", int, 1496, 120),
            ByteFieldCodec("ball_item_pocket", int, 1616, 64),
            ByteFieldCodec("tm_case", int, 1680, 256),
            ByteFieldCodec("berry_pocket", int, 1936, 184),
        ]
        self.object_class = section_class
        super().__init__(fields, output_size=RAW_SECTION_DATA_CONTENT_SIZE)


class PCBufferInitSectionCodec(Codec):
    def __init__(self, section_class: Type["Serializable"]):
        fields = [
            ByteFieldCodec("current_box", int, 0, 4),
            ByteFieldCodec("pokemon", list, 4, 3920, deserialize_skip=True),
        ]
        self.object_class = section_class
        super().__init__(fields, output_size=RAW_SECTION_DATA_CONTENT_SIZE)


######## Sections ########
class BaseSection(Serializable):
    @classmethod
    def from_raw_section(cls, section: RawSection):
        return cls.from_bytes(section.content_data)

    def to_byte_delta(self) -> ByteDelta:
        return ByteDelta.from_section(self)

    def to_bytes(self) -> bytes:
        raise NotImplementedError(
            "BaseSection need to use to_byte_delta instead of to_bytes!"
        )


@dataclass
class TrainerInfoSection(BaseSection):
    """Class containing information related to the trainer"""

    name: str
    gender: str
    unused: int
    trainer_id: int
    time_played: int
    options: int
    security_key: int
    _codec: ClassVar[Codec] = TrainerInfoCodec


@dataclass
class TeamItemSection(BaseSection):
    """Class containing information related to the current
    party of pokemon, money, bag items and pc items"""

    team_size: int
    party: List["Pokemon"]
    money: int
    coins: int
    pc_items: List[Item]
    item_pocket: List[Item]
    key_item_pocket: List[Item]
    ball_item_pocket: List[Item]
    tm_case: List[Item]
    berry_pocket: List[Item]
    _codec: ClassVar[Codec] = TeamItemSectionCodec

    @classmethod
    def from_bytes(cls, data: bytes):
        team = cls._codec(cls).to_object(data)

        # Each pokemon in a party is 100 bytes, thus
        # we need to create parse 6 * 100 bytes
        party = []
        for i in range(6):
            cur_pokemon_bytes = team.party[
                BYTES_PER_PARTY_POKEMON * i : BYTES_PER_PARTY_POKEMON * (i + 1)
            ]

            if cur_pokemon_bytes != TeamItemSection.null_pokemon:
                party.append(Pokemon.from_bytes(cur_pokemon_bytes))

        team.party = party

        # PC items
        pc_items = []
        for i in range(PC_ITEM_COUNT):
            cur_item_bytes = team.pc_items[ITEM_SIZE * i : ITEM_SIZE * (i + 1)]
            item = Item.from_bytes(cur_item_bytes)
            pc_items.append(item)

        team.pc_items = pc_items

        return team

    def to_bytes(self) -> bytes:

        # Copy self in order to modify the party property
        # this has to be converted into bytes, since the
        # Codec expectes this field to be bytes.
        # Thus not to modify self we use a copy

        cur_obj = copy.copy(self)
        buffer = bytearray()
        for member in cur_obj.party:
            buffer += member.to_bytes()
        cur_obj.party = bytes(buffer)

        return super(TeamItemSection, cur_obj).to_bytes()

    def add_pc_item(self, item: Item):
        cnt_act_items = 0
        next_index = 0
        for idx, cur_item in enumerate(self.pc_items):
            if cur_item.name != ITEM_INDEX_TO_NAME[0]:
                cnt_act_items += 1
            else:
                next_index = idx
                break

        if cnt_act_items >= PC_ITEM_COUNT:
            raise ValueError("Cannot add more PC Items")
        else:
            self.pc_items[next_index] = item

    @staticmethod
    def null_pokemon():
        return BYTES_PER_PARTY_POKEMON * b"\x00"


@dataclass
class PCBufferSection(BaseSection):
    pokemon: List[Pokemon]


@dataclass
class PCBufferInitSection(PCBufferSection):
    """Class containing info about Pokemon stored in the PC.
    This class just represents the first pokemon in the box
    not all of them. The remaining boxes are not implemented."""

    current_box: int
    _codec: ClassVar[Codec] = PCBufferInitSectionCodec

    @classmethod
    def from_bytes(cls, data: bytes):
        pc = cls._codec(cls).to_object(data)

        # Each pokemon in a party is 100 bytes, thus
        # we need to create parse 6 * 100 bytes
        pokemon = []
        for i in range(6):
            cur_pokemon_bytes = pc.pokemon[
                BYTES_PER_PC_POKEMON * i : BYTES_PER_PC_POKEMON * (i + 1)
            ]
            pokemon.append(PCPokemon.from_bytes(cur_pokemon_bytes))

        pc.pokemon = pokemon

        return pc

    def add_pc_pokemon(self, pokemon: PCPokemon):
        self.pokemon.append(pokemon)


# This mapping determines which RawSection's are converted
# to BaseSection implementations
SECTION_ID_TO_TYPE_MAPPING = {
    0: TrainerInfoSection,
    1: TeamItemSection,
    2: None,
    3: None,
    4: None,
    5: PCBufferInitSection,
    6: None,
    7: None,
    8: None,
    9: None,
    10: None,
    11: None,
    12: None,
    13: None,
    65535: None,  # Empty saves has section if \xFF\xFF which is 65535
}

TYPE_TO_SECTION_ID_MAPPING = {
    v: k for k, v in SECTION_ID_TO_TYPE_MAPPING.items() if v is not None
}
