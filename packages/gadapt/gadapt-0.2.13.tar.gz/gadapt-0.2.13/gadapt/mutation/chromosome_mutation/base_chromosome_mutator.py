from typing import List
import gadapt.ga_model.definitions as definitions
class BaseChromosomeMutator:    
    
    def mutate(self, c, number_of_mutation_genes: int):
        self.before_mutated(c)
        self.mutate_chromosome(c, number_of_mutation_genes)
        self.chromosome_mutated(c)
    
    def mutate_chromosome(self, c, number_of_mutation_genes: int):
        raise Exception(definitions.NOT_IMPLEMENTED)
    
    def gene_mutated(self, g, c):
        c.mutated_variables_id_list.append(g.genetic_variable.variable_id)        
        
    def chromosome_mutated(self, c):
        c.is_mutated = True
        if c.first_mutant_generation == 0:
            c.first_mutant_generation += 1
        c.last_mutant_generation = 1

    def before_mutated(self, c):
        c.mutated_variables_id_list.clear()

