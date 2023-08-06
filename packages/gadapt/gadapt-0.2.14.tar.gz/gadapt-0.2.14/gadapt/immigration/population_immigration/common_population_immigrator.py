from typing import List
from gadapt.ga_model.chromosome import Chromosome
from gadapt.immigration.population_immigration.base_population_immigrator import BasePopulationImmigrator

class CommonPopulationImmigrator(BasePopulationImmigrator):

    def immigrate(self, population):
        if population.options.immigration_number < 1:
            return
        keep_number = population.options.keep_number
        chromosome_list: List[Chromosome] = list(population.get_sorted(
            key=lambda c: c.cost_value))[:keep_number]
        chromosome_list = sorted(chromosome_list,
            key=lambda c: (-c.cost_value, -c.chromosome_id))[:population.options.immigration_number]
        for c in chromosome_list:
            c.immigrate()
            c.population_generation = population.population_generation
