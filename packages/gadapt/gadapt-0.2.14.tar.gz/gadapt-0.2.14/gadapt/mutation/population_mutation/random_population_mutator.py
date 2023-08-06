import random
from gadapt.ga_model.chromosome import Chromosome
from gadapt.ga_model.ga_options import GAOptions
from gadapt.mutation.population_mutation.base_population_mutator import BasePopulationMutator

class RandomPopulationMutator(BasePopulationMutator):
    def __init__(self, options: GAOptions) -> None:
        super().__init__(options)

    def get_number_of_mutation_cromosomes(self) -> int:
        return self.options.number_of_mutation_chromosomes

    def mutate_population(self, population, number_of_mutation_chromosomes):
        if (population is None):
            raise Exception("population must not be None")
        number_of_mutation_genes = self.options.number_of_mutation_genes
        unallocated_chromosomes = self.get_unallocated_chromosomes(
            population, self.sort_key_random)
        chromosomes_for_mutation = unallocated_chromosomes[:number_of_mutation_chromosomes]
        for c in chromosomes_for_mutation:
            c.mutate(number_of_mutation_genes)
        return number_of_mutation_chromosomes