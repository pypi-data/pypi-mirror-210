# pyemerald

Pyemerald is a python package which lets you modify save files from Pokemon Emerald (Sapphire, Ruby, Leaf Green and Fire Red to come). It lets you modify Pokemon in your team and on the PC, and lets you modify items on the PC. It can also be used to inspect a Pokemons attributes like EV's (IV's to come).

Other and more advanced projects exist e.g. [pkHex](https://projectpokemon.org/home/files/file/1-pkhex/) which inspired this project. However, it annoyed me that I was unable to run pkHex on Linux, and thus pyemerald was created.

Please make sure to never overwrite your original save file, as this software could accidentially make an invalid save file. You are responsible for using the software correctly.
## Installation

Pyemerald can be installed from pypi with the following command:

```
pip install pyemerald
```

It has no dependencies so it should be a simple install.

## Usage

Several examples are available in the `examples` folder. But basically it works by loading an `.sav` file using a `Save` object, which can then emit a `Game` object that is modifiable. Once modification is done, the `Game` object is passed back to the `Save` object and saved to a new file (Please always save to a new file, so you don't accidentially delete your current save file!).

```python
from pyemerald.save import Save
from pyemerald.pokemon import (
    PCPokemon,
    PokemonData,
    PokemonDataAttack,
    PokemonDataEV,
    PokemonDataGrowth,
    PokemonDataMisc,
)

# Load save file
save = Save.from_file("data/marie_treecko_pokedex_pc.sav")

# Emit Game object for modification
game = save.to_game()

# Create a new Pokemon
ninjask = PCPokemon(
    personality_value=168580405,
    original_trainer_id=2865336225,
    nickname="NINJASK",
    languague=2,
    egg_name=2,
    original_trainer_name="BOSS",
    markings=0,
    checksum=40646,
    padding=0,
    pokemon_data=PokemonData(
        structs=[
            PokemonDataEV(
                hp=85,
                attack=85,
                defense=85,
                speed=85,
                sp_attack=85,
                sp_defense=85,
                coolness=0,
                beauty=0,
                cuteness=0,
                smartness=0,
                toughness=0,
                feel=0,
            ),
            PokemonDataGrowth(
                species=302,
                item_held=0,
                experience=276458,
                pp_bonus=0,
                friendship=58,
                unknown=b"\x00\x00",
            ),
            PokemonDataMisc(
                pokerus=0,
                met_location=63,
                origins=4515,
                ivs_egg=1073741823,
                ribbons=32768,
            ),
            PokemonDataAttack(
                move_1="False Swipe",
                move_2="Sleep Powder",
                move_3="Thunder Wave",
                move_4="Dig",
                pp_1=40,
                pp_2=15,
                pp_3=20,
                pp_4=10,
            ),
        ],
        personality_value=168580405,
        original_trainer_id=2865336225,
    ),
)

# Add Pokemon to user PC
game.add_pc_pokemon(ninjask)

# Put modification back to the Save Object
save.update_from_game(game)

# Write new Save file
save.to_file("data/emerald.sav")

```
