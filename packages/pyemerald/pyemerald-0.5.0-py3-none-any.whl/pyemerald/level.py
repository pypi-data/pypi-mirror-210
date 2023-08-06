"""
Module which facilitates calculation of experience points
based on a given level
"""
from pyemerald.pokemon_info import POKE_INFO


class Level:
    def __init__(self, pokemon_name: str):
        self.name = pokemon_name

    @property
    def exp_type_index(self) -> int:
        return POKE_INFO[self.name]["exp_type"]

    def determine_growth_curve(self):
        return EXP_TYPE_MAP[self.exp_type_index]

    def calc_exp(self, level: int) -> int:
        """Calculate the experience required for the pokemon
        to reach a certain level"""
        if level > 100:
            raise ValueError("Level cannot be above 100!")

        if level < 1:
            raise ValueError("Level cannot be below 0!")

        growth_func = self.determine_growth_curve()

        return int(growth_func(level))

    def get_level_from_exp(self, exp: int) -> int:
        """Calculate the level based on experience points"""
        for row in EXP_TO_LEVEL[self.exp_type_index]:
            low = row[0]
            high = row[1]
            level = row[2]
            if exp >= low and exp <= high:
                return level

            if level == 99:
                # If the function didn't return in the above
                # if clause exp will be larger than the bounds
                # for 99, thus level has to be 100
                return 100


def level_erratic(level: int) -> int:
    if level == 1:
        return 0
    elif level < 50:
        res = level**3 * (100 - level) / 50
    elif level >= 50 and level < 68:
        res = level**3 * (150 - level) / 100
    elif level >= 68 and level < 98:
        res = level**3 * int((1911 - 10 * level) / 3) / 500
    elif level >= 98 and level < 100:
        res = level**3 * (160 - level) / 100
    else:
        res = 600_000
    return int(res)


def level_fast(level: int) -> int:
    if level == 1:
        return 0
    return int(4 * level**3 / 5)


def level_medium_fast(level: int) -> int:
    if level == 1:
        return 0
    return int(level**3)


def level_medium_slow(level: int) -> int:
    if level == 1:
        return 0
    return int(6 / 5 * level**3 - 15 * level**2 + 100 * level - 140)


def level_slow(level: int) -> int:
    if level == 1:
        return 0
    return int(5 / 4 * level**3)


def level_fluctuating(level: int) -> int:
    if level == 1:
        return 0
    elif level < 15:
        res = level**3 * (int((level + 1) / 3) + 24) / 50
    elif level >= 15 and level < 36:
        res = level**3 * (level + 14) / 50
    elif level >= 36 and level < 100:
        res = level**3 * (int(level / 2) + 32) / 50
    else:
        res = 1_640_000
    return int(res)


EXP_TYPE_MAP = {
    0: level_erratic,
    1: level_fast,
    2: level_medium_fast,
    3: level_medium_slow,
    4: level_slow,
    5: level_fluctuating,
}

# Calculate table for reverse lookup exp -> level
EXP_TO_LEVEL = {
    idx: [
        (level_func(level), level_func(level + 1) - 1, level) for level in range(1, 100)
    ]
    for idx, level_func in EXP_TYPE_MAP.items()
}
