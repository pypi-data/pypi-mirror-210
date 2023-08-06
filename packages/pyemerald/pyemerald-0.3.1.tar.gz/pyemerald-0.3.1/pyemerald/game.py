"""
Module implementing the Game class which is the main object
to interact with when modifying a save file
"""
from dataclasses import dataclass
from typing import List, Type
from pyemerald.section import BaseSection
from pyemerald.section import TrainerInfoSection, TeamItemSection, PCBufferInitSection
from pyemerald.pokemon import Pokemon, PCPokemon
from pyemerald.items import Item


@dataclass
class Game:
    """Class for modifying a save file once loaded into memory"""

    sections: List[BaseSection]

    @property
    def trainer(self) -> TrainerInfoSection:
        return [
            section
            for section in self.sections
            if isinstance(section, TrainerInfoSection)
        ][0]

    def get_section(self, section_type: Type[BaseSection]) -> BaseSection:
        return [
            section for section in self.sections if isinstance(section, section_type)
        ][0]

    @property
    def party(self) -> List[Pokemon]:
        return self.get_section(TeamItemSection).party

    def get_section_by_id(self, section_id: int) -> BaseSection:
        relevant_section = [
            section for section in self.sections if section.section_id == section_id
        ]

        if len(relevant_section) == 0:
            return None
        elif len(relevant_section) == 1:
            return relevant_section[0]
        else:
            raise ValueError(f"Multiple sections with {section_id=}")

    def add_pc_item(self, item: Item):
        self.get_section(TeamItemSection).add_pc_item(item)

    def add_pc_pokemon(self, pokemon: PCPokemon):
        self.get_section(PCBufferInitSection).add_pc_pokemon(pokemon)
