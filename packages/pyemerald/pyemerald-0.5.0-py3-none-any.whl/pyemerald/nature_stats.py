from dataclasses import dataclass
from typing import Optional
import copy


@dataclass
class Nature:
    name: str
    increase: Optional[str]
    decrease: Optional[str]

    @classmethod
    def from_name(cls, name: str) -> "Nature":
        values = NATURE_NAME_TO_INDEX[name]
        values.pop("idx")
        return cls(**values)

    @classmethod
    def from_personality_value(cls, personality_value: int) -> "Nature":
        idx = personality_value % 25
        values = NATURE_MAP[idx]
        return cls(**values)

    def stat_factor(self, stat: "Stat") -> float:
        """Determine the nature multiplier which should
        be applied when calculating the given stat
        https://bulbapedia.bulbagarden.net/wiki/Stat
        """
        if stat.stat_type == self.increase:
            factor = 1.1
        elif stat.stat_type == self.decrease:
            factor = 0.9
        else:
            factor = 1
        return factor


@dataclass
class Stat:
    stat_type: str
    base: int
    iv: int
    ev: int
    level: int

    def __post_init__(self):
        valid_values = ["hp", "attack", "defense", "speed", "sp_attack", "sp_defense"]
        if self.stat_type not in valid_values:
            raise ValueError(
                f"Value {self.stat_type} is not a value stat type. "
                f"Valid values are {valid_values}"
            )

    def total_stat(self, nature: Nature):
        if self.stat_type == "hp":
            numerator = (2 * self.base + self.iv + int(self.ev / 4)) * self.level
            res = int(numerator / 100) + self.level + 10
        else:
            nature_factor = nature.stat_factor(self)
            numerator = (2 * self.base + self.iv + int(self.ev / 4)) * self.level
            inner = int(numerator / 100) + 5
            res = int(inner * nature_factor)

        return res


NATURE_MAP = {
    0: {"name": "Hardy", "increase": None, "decrease": None},
    1: {"name": "Lonely", "increase": "attack", "decrease": "defense"},
    2: {"name": "Brave", "increase": "attack", "decrease": "speed"},
    3: {"name": "Adamant", "increase": "attack", "decrease": "sp_attack"},
    4: {"name": "Naughty", "increase": "attack", "decrease": "sp_defense"},
    5: {"name": "Bold", "increase": "defense", "decrease": "attack"},
    6: {"name": "Docile", "increase": None, "decrease": None},
    7: {"name": "Relaxed", "increase": "defense", "decrease": "speed"},
    8: {"name": "Impish", "increase": "defense", "decrease": "sp_attack"},
    9: {"name": "Lax", "increase": "defense", "decrease": "sp_defense"},
    10: {"name": "Timid", "increase": "speed", "decrease": "attack"},
    11: {"name": "Hasty", "increase": "speed", "decrease": "defense"},
    12: {"name": "Serious", "increase": None, "decrease": None},
    13: {"name": "Jolly", "increase": "speed", "decrease": "sp_attack"},
    14: {"name": "Naive", "increase": "speed", "decrease": "sp_defense"},
    15: {"name": "Modest", "increase": "sp_attack", "decrease": "attack"},
    16: {"name": "Mild", "increase": "sp_attack", "decrease": "defense"},
    17: {"name": "Quiet", "increase": "sp_attack", "decrease": "speed"},
    18: {"name": "Bashful", "increase": None, "decrease": None},
    19: {"name": "Rash", "increase": "sp_attack", "decrease": "sp_defense"},
    20: {"name": "Calm", "increase": "sp_defense", "decrease": "attack"},
    21: {"name": "Gentle", "increase": "sp_defense", "decrease": "defense"},
    22: {"name": "Sassy", "increase": "sp_defense", "decrease": "speed"},
    23: {"name": "Careful", "increase": "sp_defense", "decrease": "sp_attack"},
    24: {"name": "Quirky", "increase": None, "decrease": None},
}

NATURE_NAME_TO_INDEX = {}
for k, v in NATURE_MAP.items():
    values = {k: v for k, v in v.items() if k != "name"}
    values["idx"] = k
    NATURE_NAME_TO_INDEX[v["name"]] = values
