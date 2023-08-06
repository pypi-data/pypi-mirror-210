# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyemerald']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'pyemerald',
    'version': '0.4.0',
    'description': 'A package to modify save files from Pokemon Emerald',
    'long_description': '# pyemerald\n\nPyemerald is a python package which lets you modify save files from Pokemon Emerald (Sapphire, Ruby, Leaf Green and Fire Red to come). It lets you modify Pokemon in your team and on the PC, and lets you modify items on the PC. It can also be used to inspect a Pokemons attributes like EV\'s (IV\'s to come).\n\nOther and more advanced projects exist e.g. [pkHex](https://projectpokemon.org/home/files/file/1-pkhex/) which inspired this project. However, it annoyed me that I was unable to run pkHex on Linux, and thus pyemerald was created.\n\nPlease make sure to never overwrite your original save file, as this software could accidentially make an invalid save file. You are responsible for using the software correctly.\n## Installation\n\nPyemerald can be installed from pypi with the following command:\n\n```\npip install pyemerald\n```\n\nIt has no dependencies so it should be a simple install.\n\n## Usage\n\nSeveral examples are available in the `examples` folder. But basically it works by loading an `.sav` file using a `Save` object, which can then emit a `Game` object that is modifiable. Once modification is done, the `Game` object is passed back to the `Save` object and saved to a new file (Please always save to a new file, so you don\'t accidentially delete your current save file!).\n\n```python\nfrom pyemerald.save import Save\nfrom pyemerald.pokemon import PCPokemon\nfrom pyemerald.moves import Move\n\nsave = Save.from_file("data/marie_treecko_pokedex_pc.sav")\n\ngame = save.to_game()\n\n# Simple create pokemon\nflygon = PCPokemon.from_name(\n    name="Flygon",\n    level=48,\n    move_1=Move.from_name("Thunder"),\n    move_2=Move.from_name("Thunder Punch"),\n    move_3=Move.from_name("Ice Beam"),\n    move_4=Move.from_name("Fly"),\n)\n\n# Add Pokemon to user PC\ngame.add_pc_pokemon(flygon)\n\n# Put modification back to the Save Object\nsave.update_from_game(game)\n\n# Write new Save file\nsave.to_file("data/emerald.sav")\n\n```\n',
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
