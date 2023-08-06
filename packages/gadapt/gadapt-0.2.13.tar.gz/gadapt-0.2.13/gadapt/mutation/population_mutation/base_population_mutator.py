import math
import random
from typing import List
from gadapt.ga_model.chromosome import Chromosome
from gadapt.ga_model.ga_options import GAOptions
import gadapt.ga_model.definitions as definitions
class BasePopulationMutator:
    
    def __init__(self, options: GAOptions) -> None:
        self.options = options

    def before_exit_check(self, population):
        pass

    def after_first_execution(self, population):
        pass
    
    def mutate(self, population):
        number_of_mutated_chromosomes = population.options.number_of_mutation_chromosomes  
        self.mutate_population(population, number_of_mutated_chromosomes)

    def mutate_population(self, population, number_of_mutated_chromosomes):
        raise Exception(definitions.NOT_IMPLEMENTED)
    
    def get_unallocated_chromosomes(self, population, sort_key_function = None) -> List[Chromosome]:
        def unallocated_chromosomes_condition(c: Chromosome) -> bool:
            return math.isnan(c.cost_value) and (not c.is_immigrant) and c.population_generation == population.population_generation and not c.is_mutated
        lst = [c for c in population if (unallocated_chromosomes_condition(c))]
        if not sort_key_function is None:
            lst.sort(key=sort_key_function)
        return lst
    
    def sort_key_random(self, c: Chromosome):
        return random.random()