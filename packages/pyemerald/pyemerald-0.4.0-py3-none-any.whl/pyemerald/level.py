"""
Module which facilitates calculation of experience points
based on a given level
"""
from pyemerald.pokemon_info import POKE_INFO


class Level:
    def __init__(self, pokemon_name: str):
        self.name = pokemon_name

    def determine_growth_curve(self):
        exp_type_index = POKE_INFO[self.name]["exp_type"]
        return EXP_TYPE_MAP[exp_type_index]

    def calc_exp(self, level: int) -> int:
        """Calculate the experience required for the pokemon
        to reach a certain level"""
        if level > 100:
            raise ValueError("Level cannot be above 100!")

        if level < 1:
            raise ValueError("Level cannot be below 0!")

        growth_func = self.determine_growth_curve()

        return int(growth_func(level))


def level_erratic(level: int) -> int:
    if level < 50:
        return level**3 * (100 - level) / 50
    elif level >= 50 and level < 68:
        return level**3 * (150 - level) / 100
    elif level >= 68 and level < 98:
        return level**3 * int((1911 - 10 * level) / 3) / 500
    elif level >= 98 and level < 100:
        return level**3 * (160 - level) / 100
    return 600_000


def level_fast(level: int) -> int:
    return 4 * level**3 / 5


def level_medium_fast(level: int) -> int:
    return level**3


def level_medium_slow(level: int) -> int:
    return 6 / 5 * level**3 - 15 * level**2 + 100 * level - 140


def level_slow(level: int) -> int:
    return 5 / 4 * level**3


def level_fluctuating(level: int) -> int:
    if level < 15:
        return level**3 * (int((level + 1) / 3) + 24)
    elif level >= 15 and level < 36:
        return level**3 * (level + 14) / 50
    elif level >= 36 and level < 100:
        return level**3 * (int(level / 2) + 32) / 50
    return 1_640_000


EXP_TYPE_MAP = {
    0: level_erratic,
    1: level_fast,
    2: level_medium_fast,
    3: level_medium_slow,
    4: level_slow,
    5: level_fluctuating,
}
