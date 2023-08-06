import logging
import math
from typing import List
from gadapt.cost_finding.base_cost_finder import BaseCostFinder
from gadapt.ga_model.chromosome import Chromosome
from gadapt.ga_model.population import Population
import gadapt.utils.ga_utils as ga_utils

class CommonCostFinder(BaseCostFinder):
    def find_costs_for_chromosome(self, population: Population):
        if (population is None):
            raise Exception("population must not be null!")
        chromosomes_for_execution: List[Chromosome] = [
            c for c in population if (math.isnan(c.cost_value)) or (c.is_immigrant and c.population_generation == population.population_generation)]
        for c in chromosomes_for_execution:
            self.execute_function(population.options.cost_function, c)        
        better_chromosomes: List[Chromosome] = population.get_sorted(key=lambda x: x.cost_value)[:
            population.options.keep_number]        
        population.best_individual = better_chromosomes[0]       
        population.min_cost = (min(
            better_chromosomes, key=lambda x: x.cost_value)).cost_value
        better_chromosomes_without_immigrants = better_chromosomes[:population.options.keep_number - population.options.immigration_number]
        population.avg_cost = sum(
            [c.cost_value for c in better_chromosomes_without_immigrants]) / len(better_chromosomes_without_immigrants)
        self.log_population(population)
        population.clear_and_add_chromosomes(better_chromosomes)
        population.update_variables()
        self.cost_found_first_time(population, better_chromosomes)
        
    def cost_found_first_time(self, population: Population, better_chromosomes: List[Chromosome] ):
        if math.isnan(population.first_cost):
            population.first_cost = ga_utils.average([c.cost_value for c in better_chromosomes])
            population.population_mutator.after_first_execution(population)

    def log_population(self, population: Population):
        if population.options.logging:
            logging.info(str(population))