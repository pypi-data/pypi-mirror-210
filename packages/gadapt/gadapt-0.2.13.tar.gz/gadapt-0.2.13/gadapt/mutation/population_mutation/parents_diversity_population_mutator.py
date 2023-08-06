from ast import List
import random
from gadapt.ga_model.chromosome import Chromosome
from gadapt.ga_model.ga_options import GAOptions
from gadapt.mutation.population_mutation.base_population_mutator import BasePopulationMutator
from gadapt.sampling.base_sampling import BaseSampling

class ParentsDiversityPopulationMutator(BasePopulationMutator):
        
    def __init__(self, sampling: BaseSampling, options: GAOptions) -> None:
        super().__init__(options)
        self.sampling = sampling
            
    def sort_key_parents_diversity_random(self, c: Chromosome):
        return (c.parents_diversity, random.random())      
    
    def mutate_population(self, population, number_of_mutation_chromosomes):
        if population is None:
            raise Exception("Population must not be null")
        unallocated_chromosomes: List[Chromosome] = self.get_unallocated_chromosomes(
            population, self.sort_key_parents_diversity_random)
        chromosomes_for_mutation: List[Chromosome] = []
        if self.options.must_mutate_for_same_parents:
            chromosomes_for_mutation = [
                c for c in unallocated_chromosomes if c.parents_diversity == 0]              
        chromosomes_for_mutation_count = len(chromosomes_for_mutation)
        rest_number = number_of_mutation_chromosomes - chromosomes_for_mutation_count
        if rest_number > 0:
            if self.options.must_mutate_for_same_parents:
                chromosomes_for_mutation = [c for c in unallocated_chromosomes if (not c.parents_diversity == 0)]
            else:
                chromosomes_for_mutation = [c for c in unallocated_chromosomes]
            chromosomes_for_mutation = self.sampling.get_sample(chromosomes_for_mutation, rest_number, lambda c: c.parents_diversity)       
        for c in chromosomes_for_mutation:
            c.mutate(self.options.number_of_mutation_genes)
        return len(chromosomes_for_mutation)