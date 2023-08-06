# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyemerald']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'pyemerald',
    'version': '0.3.2',
    'description': 'A package to modify save files from Pokemon Emerald',
    'long_description': '# pyemerald\n\nPyemerald is a python package which lets you modify save files from Pokemon Emerald (Sapphire, Ruby, Leaf Green and Fire Red to come). It lets you modify Pokemon in your team and on the PC, and lets you modify items on the PC. It can also be used to inspect a Pokemons attributes like EV\'s (IV\'s to come).\n\nOther and more advanced projects exist e.g. [pkHex](https://projectpokemon.org/home/files/file/1-pkhex/) which inspired this project. However, it annoyed me that I was unable to run pkHex on Linux, and thus pyemerald was created.\n\nPlease make sure to never overwrite your original save file, as this software could accidentially make an invalid save file. You are responsible for using the software correctly.\n## Installation\n\nPyemerald can be installed from pypi with the following command:\n\n```\npip install pyemerald\n```\n\nIt has no dependencies so it should be a simple install.\n\n## Usage\n\nSeveral examples are available in the `examples` folder. But basically it works by loading an `.sav` file using a `Save` object, which can then emit a `Game` object that is modifiable. Once modification is done, the `Game` object is passed back to the `Save` object and saved to a new file (Please always save to a new file, so you don\'t accidentially delete your current save file!).\n\n```python\nfrom pyemerald.save import Save\nfrom pyemerald.pokemon import (\n    PCPokemon,\n    PokemonData,\n    PokemonDataAttack,\n    PokemonDataEV,\n    PokemonDataGrowth,\n    PokemonDataMisc,\n)\n\n# Load save file\nsave = Save.from_file("data/marie_treecko_pokedex_pc.sav")\n\n# Emit Game object for modification\ngame = save.to_game()\n\n# Create a new Pokemon\nninjask = PCPokemon(\n    personality_value=168580405,\n    original_trainer_id=2865336225,\n    nickname="NINJASK",\n    languague=2,\n    egg_name=2,\n    original_trainer_name="BOSS",\n    markings=0,\n    checksum=40646,\n    padding=0,\n    pokemon_data=PokemonData(\n        structs=[\n            PokemonDataEV(\n                hp=85,\n                attack=85,\n                defense=85,\n                speed=85,\n                sp_attack=85,\n                sp_defense=85,\n                coolness=0,\n                beauty=0,\n                cuteness=0,\n                smartness=0,\n                toughness=0,\n                feel=0,\n            ),\n            PokemonDataGrowth(\n                species=302,\n                item_held=0,\n                experience=276458,\n                pp_bonus=0,\n                friendship=58,\n                unknown=b"\\x00\\x00",\n            ),\n            PokemonDataMisc(\n                pokerus=0,\n                met_location=63,\n                origins=4515,\n                ivs_egg=1073741823,\n                ribbons=32768,\n            ),\n            PokemonDataAttack(\n                move_1="False Swipe",\n                move_2="Sleep Powder",\n                move_3="Thunder Wave",\n                move_4="Dig",\n                pp_1=40,\n                pp_2=15,\n                pp_3=20,\n                pp_4=10,\n            ),\n        ],\n        personality_value=168580405,\n        original_trainer_id=2865336225,\n    ),\n)\n\n# Add Pokemon to user PC\ngame.add_pc_pokemon(ninjask)\n\n# Put modification back to the Save Object\nsave.update_from_game(game)\n\n# Write new Save file\nsave.to_file("data/emerald.sav")\n\n```\n',
    'author': 'matkvist',
    'author_email': 'kvistanalytics@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/magnetos_son/pyemerald',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
