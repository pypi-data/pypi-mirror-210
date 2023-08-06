from ast import List
import random
from gadapt.ga_model.ga_options import GAOptions
from gadapt.mutation.population_mutation.base_population_mutator import BasePopulationMutator

class ComposedPopulationMutator(BasePopulationMutator):
        
    def __init__(self, options: GAOptions) -> None:
        super().__init__(options)
        self.mutators = []
            
    def append(self, mutator: BasePopulationMutator):
        self.mutators.append(mutator)         
    
    def mutate_population(self, population, number_of_mutation_chromosomes):        
        if population is None:
            raise Exception("Population must not be null")
        if len(self.mutators) == 0:
            raise Exception("at least one mutator must be added")
        random.shuffle(self.mutators)
        nmc = 0
        for m in self.mutators:
            if nmc < number_of_mutation_chromosomes:
                nmc += m.mutate_population(population, number_of_mutation_chromosomes - nmc) 

    def before_exit_check(self, population):
        for m in self.mutators:
            m.before_exit_check(population)

    def after_first_execution(self, population):
        for m in self.mutators:
            m.after_first_execution(population) 