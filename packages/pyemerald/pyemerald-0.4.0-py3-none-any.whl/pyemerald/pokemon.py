"""
Module implementing all logic related to a Pokemon
e.g. Stats, moves, original trainer etc.
"""
from typing import Type, List, Union, ClassVar, Optional, Dict
from dataclasses import dataclass
import random
import string
from pyemerald.codec import (
    Codec,
    ByteFieldCodec,
    bytes_to_int,
    int_to_bytes,
    Serializable,
    ByteDeltaField,
)
from pyemerald.constants import POKEMON_DATA_SUBSTRUCT_SIZE
from pyemerald.moves import INT_TO_MOVE, MOVE_TO_INT, Move
from pyemerald.items import Item
from pyemerald.pokemon_info import POKE_INFO
from pyemerald.level import Level
from pyemerald.utils import get_bits_by_position
from pyemerald.nature_stats import Stat, Nature


class PCPokemonCodec(Codec):
    def __init__(self, section_class: Type["Serializable"]):
        fields = [
            ByteFieldCodec("personality_value", int, 0, 4),
            ByteFieldCodec("original_trainer_id", int, 4, 4),
            ByteFieldCodec("nickname", str, 8, 10),
            ByteFieldCodec("languague", int, 18, 1),
            ByteFieldCodec("egg_name", int, 19, 1),
            ByteFieldCodec("original_trainer_name", str, 20, 7),
            ByteFieldCodec("markings", int, 27, 1),
            ByteFieldCodec("checksum", int, 28, 2),
            ByteFieldCodec("padding", int, 30, 2),
            ByteFieldCodec("pokemon_data", PokemonData, 32, 48, deserialize_skip=True),
        ]
        self.object_class = section_class
        super().__init__(fields)


class PokemonCodec(Codec):
    def __init__(self, section_class: Type["Serializable"]):
        fields = [
            ByteFieldCodec("personality_value", int, 0, 4),
            ByteFieldCodec("original_trainer_id", int, 4, 4),
            ByteFieldCodec("nickname", str, 8, 10),
            ByteFieldCodec("languague", int, 18, 1),
            ByteFieldCodec("egg_name", int, 19, 1),
            ByteFieldCodec("original_trainer_name", str, 20, 7),
            ByteFieldCodec("markings", int, 27, 1),
            ByteFieldCodec("checksum", int, 28, 2),
            ByteFieldCodec("padding", int, 30, 2),
            ByteFieldCodec("pokemon_data", PokemonData, 32, 48, deserialize_skip=True),
            ByteFieldCodec("status_condition", int, 80, 4),
            ByteFieldCodec("level", int, 84, 1),
            ByteFieldCodec("pokerus", int, 85, 1),
            ByteFieldCodec("current_hp", int, 86, 2),
            ByteFieldCodec("total_hp", int, 88, 2),
            ByteFieldCodec("attack", int, 90, 2),
            ByteFieldCodec("defense", int, 92, 2),
            ByteFieldCodec("speed", int, 94, 2),
            ByteFieldCodec("sp_attack", int, 96, 2),
            ByteFieldCodec("sp_defense", int, 98, 2),
        ]
        self.object_class = section_class
        super().__init__(fields)


class PokemonDataGrowthCodec(Codec):
    def __init__(self, section_class: Type["Serializable"]):
        fields = [
            ByteFieldCodec("species", int, 0, 2),
            ByteFieldCodec("item_held", int, 2, 2),
            ByteFieldCodec("experience", int, 4, 4),
            ByteFieldCodec("pp_bonus", int, 8, 1),
            ByteFieldCodec("friendship", int, 9, 1),
            ByteFieldCodec("unknown", bytes, 10, 2),
        ]
        self.object_class = section_class
        super().__init__(fields)


class PokemonDataAttackCodec(Codec):
    def __init__(self, section_class: Type["Serializable"]):
        fields = [
            ByteFieldCodec(
                "move_1",
                int,
                0,
                2,
                value_map=INT_TO_MOVE,
                reverse_value_map=MOVE_TO_INT,
            ),
            ByteFieldCodec(
                "move_2",
                int,
                2,
                2,
                value_map=INT_TO_MOVE,
                reverse_value_map=MOVE_TO_INT,
            ),
            ByteFieldCodec(
                "move_3",
                int,
                4,
                2,
                value_map=INT_TO_MOVE,
                reverse_value_map=MOVE_TO_INT,
            ),
            ByteFieldCodec(
                "move_4",
                int,
                6,
                2,
                value_map=INT_TO_MOVE,
                reverse_value_map=MOVE_TO_INT,
            ),
            ByteFieldCodec("pp_1", int, 8, 1),
            ByteFieldCodec("pp_2", int, 9, 1),
            ByteFieldCodec("pp_3", int, 10, 1),
            ByteFieldCodec("pp_4", int, 11, 1),
        ]
        self.object_class = section_class
        super().__init__(fields)


class PokemonDataEVCodec(Codec):
    def __init__(self, section_class: Type["Serializable"]):
        fields = [
            ByteFieldCodec("hp", int, 0, 1),
            ByteFieldCodec("attack", int, 1, 1),
            ByteFieldCodec("defense", int, 2, 1),
            ByteFieldCodec("speed", int, 3, 1),
            ByteFieldCodec("sp_attack", int, 4, 1),
            ByteFieldCodec("sp_defense", int, 5, 1),
            ByteFieldCodec("coolness", int, 6, 1),
            ByteFieldCodec("beauty", int, 7, 1),
            ByteFieldCodec("cuteness", int, 8, 1),
            ByteFieldCodec("smartness", int, 9, 1),
            ByteFieldCodec("toughness", int, 10, 1),
            ByteFieldCodec("feel", int, 11, 1),
        ]
        self.object_class = section_class
        super().__init__(fields)


class PokemonDataMiscCodec(Codec):
    def __init__(self, section_class: Type["Serializable"]):
        fields = [
            ByteFieldCodec("pokerus", int, 0, 1),
            ByteFieldCodec("met_location", int, 1, 1),
            ByteFieldCodec("origins", int, 2, 2),
            ByteFieldCodec(
                "ivs_egg",
                IVEggContainer,
                4,
                4,
                deserialize_skip=True,
                serialize_skip=True,
            ),
            ByteFieldCodec("ribbons", int, 8, 4),
        ]
        self.object_class = section_class
        super().__init__(fields)


class PokemonDataCodec(Codec):
    def __init__(self, section_class: Type["Serializable"]):
        fields = [
            ByteFieldCodec("structs", list, 0, 48),
        ]
        self.object_class = section_class
        super().__init__(fields)


@dataclass
class BasePokemonData(Serializable):
    @classmethod
    def from_bytes(
        cls, data: bytes, original_trainer_id: int, personality_value: int
    ) -> "BasePokemonData":
        enc = PokemonDataEncryption(original_trainer_id, personality_value)

        # Decrypt data
        decrypted_data = enc.decrypt_data(data)

        # Call the from_bytes on the Serializable
        obj = super(BasePokemonData, cls).from_bytes(decrypted_data)
        obj._encrypter = enc

        return obj

    def to_bytes(self) -> bytes:

        # Convert to bytes using super method Serializable
        byte_data = self.to_bytes_unencrypted()

        # Encrypt data
        encrypted_data = self._encrypter.encrypt_data(byte_data)

        return encrypted_data

    def to_bytes_unencrypted(self) -> bytes:

        # Convert to bytes using super method Serializable
        return super(BasePokemonData, self).to_bytes()

    def __eq__(self, other):

        if not isinstance(other, self.__class__):
            return False

        return self.__dict__ == other.__dict__


@dataclass
class PokemonDataEncryption:
    """
    The four pokemon data subdata structures are encrypted. This class
    holds encryption and decryption of this data
    """

    original_trainer_id: int
    personality_value: int

    @property
    def decryption_key(self):
        return self.original_trainer_id ^ self.personality_value

    def decrypt_data(self, data: bytes, step_size: int = 4) -> bytes:
        key = self.decryption_key
        size = len(data)

        if size % step_size != 0:

            raise ValueError(f"Length issue on data: {size=}, {step_size=}")

        n = int(size / step_size)

        res = bytearray()
        for i in range(n):
            d = data[(step_size * i) : (step_size * (i + 1))]

            # Convert to int in order to xor
            data_int = bytes_to_int(d)

            # XOR
            xor = data_int ^ key

            # Back to bytes
            res += int_to_bytes(xor, step_size)

        return bytes(res)

    def encrypt_data(self, data: bytes, step_size: int = 4) -> bytes:
        return self.decrypt_data(data)


@dataclass
class IVEggContainer(Serializable):
    """Contains IV, egg and ability data.
    Doesn't use a codec since it relies on bits
    for each field as opposed to bytes"""

    hp: int
    attack: int
    defense: int
    speed: int
    sp_attack: int
    sp_defense: int
    egg: int
    ability: int
    _codec: ClassVar[Codec] = None

    @classmethod
    def from_bytes(cls, data: bytes):
        # Turn bytes to integer
        number = bytes_to_int(data)

        # Extract values according to
        # https://bulbapedia.bulbagarden.net/wiki/Pok%C3%A9mon_data_substructures_(Generation_III)
        hp = get_bits_by_position(number, 5, 5)
        attack = get_bits_by_position(number, 10, 5)
        defense = get_bits_by_position(number, 15, 5)
        speed = get_bits_by_position(number, 20, 5)
        sp_attack = get_bits_by_position(number, 25, 5)
        sp_defense = get_bits_by_position(number, 30, 5)
        egg = get_bits_by_position(number, 31, 1)
        ability = get_bits_by_position(number, 32, 1)

        return cls(
            hp=hp,
            attack=attack,
            defense=defense,
            speed=speed,
            sp_attack=sp_attack,
            sp_defense=sp_defense,
            egg=egg,
            ability=ability,
        )

    def to_number(self) -> int:

        # Shift all numbers by the amount they were
        # shifted when created from bytes
        number = (
            (self.ability << 31)
            + (self.egg << 30)
            + (self.sp_defense << 25)
            + (self.sp_attack << 20)
            + (self.speed << 15)
            + (self.defense << 10)
            + (self.attack << 5)
            + (self.hp)
        )
        return number

    def to_bytes_unencrypted(self) -> bytes:
        return int_to_bytes(self.to_number(), length=4)


@dataclass
class PokemonDataGrowth(BasePokemonData):
    species: int
    item_held: int
    experience: int
    pp_bonus: int
    friendship: int
    unknown: bytes
    _codec: ClassVar[Codec] = PokemonDataGrowthCodec


@dataclass
class PokemonDataAttack(BasePokemonData):
    move_1: int
    move_2: int
    move_3: int
    move_4: int
    pp_1: int
    pp_2: int
    pp_3: int
    pp_4: int
    _codec: ClassVar[Codec] = PokemonDataAttackCodec


@dataclass
class PokemonDataEV(BasePokemonData):
    hp: int
    attack: int
    defense: int
    speed: int
    sp_attack: int
    sp_defense: int
    coolness: int
    beauty: int
    cuteness: int
    smartness: int
    toughness: int
    feel: int
    _codec: ClassVar[Codec] = PokemonDataEVCodec


@dataclass
class PokemonDataMisc(BasePokemonData):
    pokerus: int
    met_location: int
    origins: int
    ivs_egg: IVEggContainer
    ribbons: int
    _codec: ClassVar[Codec] = PokemonDataMiscCodec

    def to_bytes_unencrypted(self) -> bytes:

        # Create bytes by filling ivs_egg with 0xFF
        data = bytearray(super(BasePokemonData, self).to_bytes())

        # Generate correct byte data
        ivs_egg_bytes = self.ivs_egg.to_bytes_unencrypted()

        # Get codec information for the field
        codec_field = self.codec.get_field_by_name("ivs_egg")
        field_offset = codec_field.offset
        field_size = codec_field.size

        # Add the correct bytes for ivs_egg
        data[field_offset : field_offset + field_size] = ivs_egg_bytes

        return bytes(data)

    @classmethod
    def from_bytes(cls, data: bytes, original_trainer_id: int, personality_value: int):
        misc = super(PokemonDataMisc, cls).from_bytes(
            data, original_trainer_id, personality_value
        )

        # data property is extracted as bytes, call to the PokemonData
        # to create itself from the bytes
        ivs_egg = IVEggContainer.from_bytes(misc.ivs_egg)
        misc.ivs_egg = ivs_egg
        return misc


@dataclass
class PokemonData(Serializable):
    """
    Holds the 4 data substructures related to core pokemon stats. These
    are encrypted and thus different from the rest of the pokemon data
    """

    structs: List[
        Union[PokemonDataGrowth, PokemonDataAttack, PokemonDataEV, PokemonDataMisc]
    ]
    personality_value: int
    original_trainer_id: int
    _codec: ClassVar[Codec] = PokemonDataCodec

    def __post_init__(self):
        for struct in self.structs:
            if not hasattr(struct, "_encrypter"):
                enc = PokemonDataEncryption(
                    self.original_trainer_id, self.personality_value
                )
                struct._encrypter = enc

        self.order_structs()

    @property
    def order(self):
        """Return the order the structs should adhere to"""
        return PokemonData._order(self.personality_value)

    @staticmethod
    def _order(personality_value: int):
        mod = personality_value % 24
        return POKEMON_DATA_ORDERING[mod]

    def order_structs(self):
        """Order the structs according to the personality value"""
        res = []
        for _type in self.order:
            for struct in self.structs:
                if isinstance(struct, _type):
                    res.append(struct)

        if len(res) != 4:
            raise ValueError("Missing structs in PokemonData!")

        self.structs = res

    @classmethod
    def from_bytes(cls, data: bytes, personality_value: int, original_trainer_id: int):

        if len(data) != POKEMON_DATA_SUBSTRUCT_SIZE * 4:
            raise ValueError(
                f"Expected {POKEMON_DATA_SUBSTRUCT_SIZE * 4} bytes but got {len(data)}!"
            )

        structs = []
        order = PokemonData._order(personality_value)
        for idx, struct in enumerate(order):
            cur_data = data[
                idx
                * POKEMON_DATA_SUBSTRUCT_SIZE : (idx + 1)
                * POKEMON_DATA_SUBSTRUCT_SIZE
            ]
            structs.append(
                struct.from_bytes(cur_data, personality_value, original_trainer_id)
            )

        obj = cls(structs, personality_value, original_trainer_id)

        return obj

    @staticmethod
    def _to_bytes(byte_structs) -> bytes:

        # Should adhere to the order from self.order (not checked)
        buffer = bytearray()
        for struct in byte_structs:
            buffer += struct

        return bytes(buffer)

    def to_bytes(self) -> bytes:
        return PokemonData._to_bytes([struct.to_bytes() for struct in self.structs])

    def to_bytes_unencrypted(self) -> bytes:
        return PokemonData._to_bytes(
            [struct.to_bytes_unencrypted() for struct in self.structs]
        )

    def to_byte_delta_bespoke(self, offset) -> List[ByteDeltaField]:
        # Copy self in order to modify the pokemon_data property
        # this has to be converted into bytes.
        # Thus not to modify self we use a copy

        data = self.to_bytes()
        field_codec = self.codec.fields[0]
        field_codec.add_offset(offset)

        return [ByteDeltaField(value=data, field_codec=field_codec)]

    def get_struct_by_type(self, _type):
        return [struct for struct in self.structs if isinstance(struct, _type)][0]

    def __eq__(self, other):

        if not isinstance(other, self.__class__):
            return False

        checks = [
            self.personality_value == other.personality_value,
            self.original_trainer_id == other.original_trainer_id,
            self.structs[0] == other.structs[0],
            self.structs[1] == other.structs[1],
            self.structs[2] == other.structs[2],
            self.structs[3] == other.structs[3],
        ]

        return all(checks)


# The order of the four sub data structures rotate per pokemon, this is a mapping
# for getting the right order
POKEMON_DATA_ORDERING = {
    0: [PokemonDataGrowth, PokemonDataAttack, PokemonDataEV, PokemonDataMisc],
    1: [PokemonDataGrowth, PokemonDataAttack, PokemonDataMisc, PokemonDataEV],
    2: [PokemonDataGrowth, PokemonDataEV, PokemonDataAttack, PokemonDataMisc],
    3: [PokemonDataGrowth, PokemonDataEV, PokemonDataMisc, PokemonDataAttack],
    4: [PokemonDataGrowth, PokemonDataMisc, PokemonDataAttack, PokemonDataEV],
    5: [PokemonDataGrowth, PokemonDataMisc, PokemonDataEV, PokemonDataAttack],
    6: [PokemonDataAttack, PokemonDataGrowth, PokemonDataEV, PokemonDataMisc],
    7: [PokemonDataAttack, PokemonDataGrowth, PokemonDataMisc, PokemonDataEV],
    8: [PokemonDataAttack, PokemonDataEV, PokemonDataGrowth, PokemonDataMisc],
    9: [PokemonDataAttack, PokemonDataMisc, PokemonDataGrowth, PokemonDataEV],
    10: [PokemonDataAttack, PokemonDataMisc, PokemonDataGrowth, PokemonDataEV],
    11: [PokemonDataAttack, PokemonDataMisc, PokemonDataEV, PokemonDataGrowth],
    12: [PokemonDataEV, PokemonDataGrowth, PokemonDataAttack, PokemonDataMisc],
    13: [PokemonDataEV, PokemonDataGrowth, PokemonDataMisc, PokemonDataAttack],
    14: [PokemonDataEV, PokemonDataAttack, PokemonDataGrowth, PokemonDataMisc],
    15: [PokemonDataEV, PokemonDataAttack, PokemonDataMisc, PokemonDataGrowth],
    16: [PokemonDataEV, PokemonDataMisc, PokemonDataGrowth, PokemonDataAttack],
    17: [PokemonDataEV, PokemonDataMisc, PokemonDataAttack, PokemonDataGrowth],
    18: [PokemonDataMisc, PokemonDataGrowth, PokemonDataAttack, PokemonDataEV],
    19: [PokemonDataMisc, PokemonDataGrowth, PokemonDataEV, PokemonDataAttack],
    20: [PokemonDataMisc, PokemonDataAttack, PokemonDataGrowth, PokemonDataEV],
    21: [PokemonDataMisc, PokemonDataAttack, PokemonDataEV, PokemonDataGrowth],
    22: [PokemonDataMisc, PokemonDataEV, PokemonDataGrowth, PokemonDataAttack],
    23: [PokemonDataMisc, PokemonDataEV, PokemonDataAttack, PokemonDataGrowth],
}


class PCPokemon(Serializable):
    """Pokemon class for Pokemon stored in the PC. This is the same as
    the Pokemon class except that the PCPokemon class has fewer attributes.
    This is because some values are not stored in the PC in order to
    conserve space, as they can be recalculated by the game"""

    _codec = PCPokemonCodec

    def __init__(
        self,
        personality_value: int,
        original_trainer_id: int,
        nickname: str,
        original_trainer_name: str,
        pokemon_data: PokemonData,
        languague: int = 2,
        egg_name: int = 2,
        markings: int = 0,
        checksum: int = 0,
        padding: int = 0,
    ):
        self.personality_value = personality_value
        self.original_trainer_id = original_trainer_id
        self.nickname = nickname
        self.languague = languague
        self.egg_name = egg_name
        self.original_trainer_name = original_trainer_name
        self.markings = markings
        self.raw_checksum = checksum
        self.padding = padding
        self.pokemon_data = pokemon_data

    @classmethod
    def from_bytes(cls, data: bytes):
        poke_obj = cls._codec(cls).to_object(data)

        # data property is extracted as bytes, call to the PokemonData
        # to create itself from the bytes
        poke_data = PokemonData.from_bytes(
            poke_obj.pokemon_data,
            poke_obj.personality_value,
            poke_obj.original_trainer_id,
        )
        poke_obj.pokemon_data = poke_data
        return poke_obj

    @staticmethod
    def default_values(
        name: str,
        level: int,
        move_1: Move,
        move_2: Move,
        move_3: Move,
        move_4: Move,
        ev_hp: int = 85,
        ev_attack: int = 85,
        ev_defense: int = 85,
        ev_speed: int = 85,
        ev_sp_attack: int = 85,
        ev_sp_defense: int = 85,
        iv_hp: int = 31,
        iv_attack: int = 31,
        iv_defense: int = 31,
        iv_speed: int = 31,
        iv_sp_attack: int = 31,
        iv_sp_defense: int = 31,
        coolness: int = 0,
        beauty: int = 0,
        cuteness: int = 0,
        smartness: int = 0,
        toughness: int = 0,
        feel: int = 0,
        item_held: Optional[Item] = None,
        friendship: int = 0,
        pp_bonus: int = 0,
        pokerus: int = 0,
        nickname: Optional[str] = None,
        personality_value: Optional[int] = None,
        original_trainer_id: Optional[int] = None,
        original_trainer_name: Optional[str] = None,
    ) -> Dict[str, Union[int, str, PokemonData]]:
        if personality_value is None:
            personality_value = random.randint(100000000, 4_294_967_295)
        if original_trainer_id is None:
            original_trainer_id = random.randint(1000000000, 4_294_967_295)
        if original_trainer_name is None:
            letters = string.ascii_lowercase
            original_trainer_name = "".join(random.choice(letters) for i in range(7))

        if nickname is None:
            nickname = name

        ev = PokemonDataEV(
            hp=ev_hp,
            attack=ev_attack,
            defense=ev_defense,
            speed=ev_speed,
            sp_attack=ev_sp_attack,
            sp_defense=ev_sp_defense,
            coolness=coolness,
            beauty=beauty,
            cuteness=cuteness,
            smartness=smartness,
            toughness=toughness,
            feel=feel,
        )

        level_calc = Level(name)
        experience = level_calc.calc_exp(level)

        growth = PokemonDataGrowth(
            species=POKE_INFO[name]["id"],
            item_held=item_held.index if item_held is not None else 0,
            experience=experience,
            pp_bonus=pp_bonus,
            friendship=friendship,
            unknown=b"\x00\x00",
        )

        misc = PokemonDataMisc(
            pokerus=pokerus,
            met_location=0,
            origins=0,
            ivs_egg=IVEggContainer(
                hp=iv_hp,
                attack=iv_attack,
                defense=iv_defense,
                speed=iv_speed,
                sp_attack=iv_sp_attack,
                sp_defense=iv_sp_defense,
                egg=0,
                ability=0,
            ),
            ribbons=0,
        )

        attack = PokemonDataAttack(
            move_1=move_1.name,
            move_2=move_2.name,
            move_3=move_3.name,
            move_4=move_4.name,
            pp_1=move_1.pp,
            pp_2=move_2.pp,
            pp_3=move_3.pp,
            pp_4=move_4.pp,
        )

        pk_data = PokemonData(
            structs=[ev, growth, misc, attack],
            personality_value=personality_value,
            original_trainer_id=original_trainer_id,
        )

        res = {
            "personality_value": personality_value,
            "original_trainer_id": original_trainer_id,
            "original_trainer_name": original_trainer_name,
            "nickname": nickname,
            "pokemon_data": pk_data,
        }

        return res

    @classmethod
    def from_name(
        cls,
        name: str,
        level: int,
        move_1: Move,
        move_2: Move,
        move_3: Move,
        move_4: Move,
        ev_hp: int = 85,
        ev_attack: int = 85,
        ev_defense: int = 85,
        ev_speed: int = 85,
        ev_sp_attack: int = 85,
        ev_sp_defense: int = 85,
        iv_hp: int = 31,
        iv_attack: int = 31,
        iv_defense: int = 31,
        iv_speed: int = 31,
        iv_sp_attack: int = 31,
        iv_sp_defense: int = 31,
        coolness: int = 0,
        beauty: int = 0,
        cuteness: int = 0,
        smartness: int = 0,
        toughness: int = 0,
        feel: int = 0,
        item_held: Optional[Item] = None,
        friendship: int = 0,
        pp_bonus: int = 0,
        pokerus: int = 0,
        nickname: Optional[str] = None,
        personality_value: Optional[int] = None,
        original_trainer_id: Optional[int] = None,
        original_trainer_name: Optional[str] = None,
    ):
        """
        Create a new PCPokemon

        Parameters
        ----------
        name: str
            Name of the Pokemon e.g. Charizard, Pikachu
        nickname: Optional[str]
            Nickname of Pokemon. If None it is set to name
        personality_value: Optional[int]
            Personality value, if None random number is set
        original_trainer_id: Optional[int]
            ID of original trainer, if None random number is set
        original_trainer_name: Optional[str]
            Name of the original trainer, if None random name is set
        """
        values = PCPokemon.default_values(
            name=name,
            level=level,
            move_1=move_1,
            move_2=move_2,
            move_3=move_3,
            move_4=move_4,
            ev_hp=ev_hp,
            ev_attack=ev_attack,
            ev_defense=ev_defense,
            ev_speed=ev_speed,
            ev_sp_attack=ev_sp_attack,
            ev_sp_defense=ev_sp_defense,
            iv_hp=iv_hp,
            iv_attack=iv_attack,
            iv_defense=iv_defense,
            iv_speed=iv_speed,
            iv_sp_attack=iv_sp_attack,
            iv_sp_defense=iv_sp_defense,
            coolness=coolness,
            beauty=beauty,
            cuteness=cuteness,
            smartness=smartness,
            toughness=toughness,
            feel=feel,
            item_held=item_held,
            friendship=friendship,
            pp_bonus=pp_bonus,
            pokerus=pokerus,
            nickname=nickname,
            personality_value=personality_value,
            original_trainer_id=original_trainer_id,
            original_trainer_name=original_trainer_name,
        )

        return cls(**values)

    @staticmethod
    def calc_checksum(data) -> int:
        chksum = 0
        for i in range(24):
            chksum += bytes_to_int(data[i * 2 : (i + 1) * 2])

        # Truncate to 2 byte
        chksum_res = chksum & 0xFFFF

        return chksum_res

    @property
    def checksum(self) -> int:
        return PCPokemon.calc_checksum(self.pokemon_data.to_bytes_unencrypted())

    @checksum.setter
    def checksum(self, value):
        self.raw_checksum = value

    @property
    def species(self):
        return self.pokemon_data.get_struct_by_type(PokemonDataGrowth).species

    @species.setter
    def species(self, value):
        self.pokemon_data.get_struct_by_type(PokemonDataGrowth).species = value

    @property
    def experience(self):
        return self.pokemon_data.get_struct_by_type(PokemonDataGrowth).species

    @experience.setter
    def experience(self, value):
        self.pokemon_data.get_struct_by_type(PokemonDataGrowth).experience = value

    @property
    def move_1(self):
        return self._get_move(1)

    @property
    def move_2(self):
        return self._get_move(2)

    @property
    def move_3(self):
        return self._get_move(3)

    @property
    def move_4(self):
        return self._get_move(4)

    def _get_move(self, index: int) -> Move:
        if index not in [1, 2, 3, 4]:
            raise ValueError(f"Move index {index} doesn't exist!")
        name = getattr(
            self.pokemon_data.get_struct_by_type(PokemonDataAttack),
            f"move_{index}",
        )
        return Move.from_name(name)

    @move_1.setter
    def move_1(self, move: Move):
        self._set_move(move, 1)

    @move_2.setter
    def move_2(self, move: Move):
        self._set_move(move, 2)

    @move_3.setter
    def move_3(self, move: Move):
        self._set_move(move, 3)

    @move_4.setter
    def move_4(self, move: Move):
        self._set_move(move, 4)

    def _set_move(self, move: Move, index: int):
        if index not in [1, 2, 3, 4]:
            raise ValueError(f"Move index {index} doesn't exist!")
        setattr(
            self.pokemon_data.get_struct_by_type(PokemonDataAttack),
            f"move_{index}",
            move.name,
        )
        setattr(
            self.pokemon_data.get_struct_by_type(PokemonDataAttack),
            f"pp_{index}",
            move.pp,
        )

    @property
    def nature(self):
        nature = Nature.from_personality_value(self.personality_value)
        return nature

    def __repr__(self):
        kws = [f"{key}={value!r}" for key, value in self.__dict__.items()]
        return "{}({})".format(type(self).__name__, ", ".join(kws))

    def __eq__(self, other):

        if not isinstance(other, self.__class__):
            return False

        checks = [
            self.personality_value == other.personality_value,
            self.original_trainer_id == other.original_trainer_id,
            self.nickname == other.nickname,
            self.original_trainer_name == other.original_trainer_name,
            self.pokemon_data == other.pokemon_data,
        ]

        return all(checks)


class Pokemon(PCPokemon):
    """Pokemon class for Pokemon in the party"""

    _codec = PokemonCodec

    def __init__(
        self,
        personality_value: int,
        original_trainer_id: int,
        nickname: str,
        original_trainer_name: str,
        pokemon_data: PokemonData,
        status_condition: int,
        level: int,
        pokerus: int,
        current_hp: int,
        total_hp: int,
        attack: int,
        defense: int,
        speed: int,
        sp_attack: int,
        sp_defense: int,
        languague: int = 2,
        egg_name: int = 2,
        markings: int = 0,
        checksum: int = 0,
        padding: int = 0,
    ):
        super().__init__(
            personality_value=personality_value,
            original_trainer_id=original_trainer_id,
            nickname=nickname,
            languague=languague,
            egg_name=egg_name,
            original_trainer_name=original_trainer_name,
            markings=markings,
            checksum=checksum,
            padding=padding,
            pokemon_data=pokemon_data,
        )

        self.status_condition = status_condition
        self.level = level
        self.pokerus = pokerus
        self.current_hp = current_hp
        self.total_hp = total_hp
        self.attack = attack
        self.defense = defense
        self.speed = speed
        self.sp_attack = sp_attack
        self.sp_defense = sp_defense

    @classmethod
    def from_name(
        cls,
        name: str,
        level: int,
        move_1: Move,
        move_2: Move,
        move_3: Move,
        move_4: Move,
        ev_hp: int = 85,
        ev_attack: int = 85,
        ev_defense: int = 85,
        ev_speed: int = 85,
        ev_sp_attack: int = 85,
        ev_sp_defense: int = 85,
        iv_hp: int = 31,
        iv_attack: int = 31,
        iv_defense: int = 31,
        iv_speed: int = 31,
        iv_sp_attack: int = 31,
        iv_sp_defense: int = 31,
        coolness: int = 0,
        beauty: int = 0,
        cuteness: int = 0,
        smartness: int = 0,
        toughness: int = 0,
        feel: int = 0,
        item_held: Optional[Item] = None,
        friendship: int = 0,
        pp_bonus: int = 0,
        pokerus: int = 0,
        nickname: Optional[str] = None,
        personality_value: Optional[int] = None,
        original_trainer_id: Optional[int] = None,
        original_trainer_name: Optional[str] = None,
    ):
        """
        Create a new PCPokemon

        Parameters
        ----------
        name: str
            Name of the Pokemon e.g. Charizard, Pikachu
        nickname: Optional[str]
            Nickname of Pokemon. If None it is set to name
        personality_value: Optional[int]
            Personality value, if None random number is set
        original_trainer_id: Optional[int]
            ID of original trainer, if None random number is set
        original_trainer_name: Optional[str]
            Name of the original trainer, if None random name is set
        """
        values = PCPokemon.default_values(
            name=name,
            level=level,
            move_1=move_1,
            move_2=move_2,
            move_3=move_3,
            move_4=move_4,
            ev_hp=ev_hp,
            ev_attack=ev_attack,
            ev_defense=ev_defense,
            ev_speed=ev_speed,
            ev_sp_attack=ev_sp_attack,
            ev_sp_defense=ev_sp_defense,
            iv_hp=iv_hp,
            iv_attack=iv_attack,
            iv_defense=iv_defense,
            iv_speed=iv_speed,
            iv_sp_attack=iv_sp_attack,
            iv_sp_defense=iv_sp_defense,
            coolness=coolness,
            beauty=beauty,
            cuteness=cuteness,
            smartness=smartness,
            toughness=toughness,
            feel=feel,
            item_held=item_held,
            friendship=friendship,
            pp_bonus=pp_bonus,
            pokerus=pokerus,
            nickname=nickname,
            personality_value=personality_value,
            original_trainer_id=original_trainer_id,
            original_trainer_name=original_trainer_name,
        )

        # Add values specific for this class
        values["status_condition"] = 0

        # Nature
        nature = Nature.from_personality_value(values["personality_value"])

        # Calc stats
        poke_info = POKE_INFO[name]
        hp_stat = Stat("hp", poke_info["hp"], iv_hp, ev_hp, level)
        attack_stat = Stat("attack", poke_info["attack"], iv_attack, ev_attack, level)
        defense_stat = Stat(
            "defense", poke_info["defense"], iv_defense, ev_defense, level
        )
        speed_stat = Stat("speed", poke_info["speed"], iv_speed, ev_speed, level)
        sp_attack_stat = Stat(
            "sp_attack", poke_info["sp_attack"], iv_sp_attack, ev_sp_attack, level
        )
        sp_defense_stat = Stat(
            "sp_defense", poke_info["sp_defense"], iv_sp_defense, ev_sp_defense, level
        )

        values["level"] = level
        values["pokerus"] = 255
        values["current_hp"] = hp_stat.total_stat(nature=nature)
        values["total_hp"] = hp_stat.total_stat(nature=nature)
        values["attack"] = attack_stat.total_stat(nature=nature)
        values["defense"] = defense_stat.total_stat(nature=nature)
        values["speed"] = speed_stat.total_stat(nature=nature)
        values["sp_attack"] = sp_attack_stat.total_stat(nature=nature)
        values["sp_defense"] = sp_defense_stat.total_stat(nature=nature)

        return cls(**values)
