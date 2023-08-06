from gadapt.ga_model.chromosome import Chromosome
from gadapt.ga_model.gene import Gene
from typing import List
import random
from gadapt.mutation.chromosome_mutation.random_chromosome_mutator import RandomChromosomeMutator
from gadapt.sampling.base_sampling import BaseSampling
import gadapt.utils.ga_utils as ga_utils

class CrossDiversityChromosomeMutator(RandomChromosomeMutator):
                    
    def __init__(self, sampling: BaseSampling) -> None:
        super().__init__()
        self.sampling = sampling
    
    def mutate_chromosome(self, c: Chromosome, number_of_mutation_genes: int):
        if number_of_mutation_genes == 0:
            return
        x_genes = [g for g in c]
        x_genes.sort(key = lambda g: -g.genetic_variable.relative_standard_deviation)   
        if number_of_mutation_genes > len(x_genes):
            number_of_mutation_genes = len(x_genes)
        number_of_mutation_genes = random.randint(1, number_of_mutation_genes)
        genes_for_mutation = self.sampling.get_sample(x_genes, number_of_mutation_genes, lambda g: g.genetic_variable.relative_standard_deviation)        
        for g in genes_for_mutation:
            self.make_mutation(g, c)        
    
    def make_random_value_below(self, g: Gene):
        if g.variable_value == g.genetic_variable.min_value:
            return g.genetic_variable.make_random_value()
        number_of_steps = random.randint(0, round((g.variable_value - g.genetic_variable.min_value) / g.genetic_variable.step))
        return g.genetic_variable.min_value + number_of_steps * g.genetic_variable.step
    
    def make_random_value_above(self, g: Gene):
        if g.variable_value == g.genetic_variable.max_value:
            return g.genetic_variable.make_random_value()
        number_of_steps = random.randint(0, round((g.genetic_variable.max_value - g.variable_value) / g.genetic_variable.step))
        return g.variable_value + number_of_steps * g.genetic_variable.step
    
    def make_random_value_below_or_above(self, g: Gene):
        if (ga_utils.get_rand_bool()):
            return self.make_random_value_above(g)
        return self.make_random_value_below(g)
    
    def set_random_value_below_or_above(self, g: Gene, c: Chromosome):
        g.variable_value = round(self.make_random_value_below_or_above(g), g.genetic_variable.decimal_places)
        self.gene_mutated(g, c)

    def make_mutation(self, g: Gene, c: Chromosome):
        f = self.get_mutate_func(g)
        f(g, c)

    def get_mutate_func(self, g: Gene):
        prob = g.genetic_variable.relative_standard_deviation
        if prob > 1.0:
            prob = 1.0
        should_mutate_random = ga_utils.get_rand_bool_with_probability(prob)
        if should_mutate_random:
            return self.set_random_value
        else:
            return self.set_random_value_below_or_above






