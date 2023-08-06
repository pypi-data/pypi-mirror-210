from gadapt.ga_model.chromosome import Chromosome
from gadapt.crossover.base_crossover import BaseCrossover
from gadapt.ga_model.gene import Gene
from gadapt.immigration.chromosome_immigration.base_chromosome_immigrator import BaseChromosomeImmigrator
from gadapt.mutation.chromosome_mutation.base_chromosome_mutator import BaseChromosomeMutator
from gadapt.gene_combination.base_gene_combination import BaseGeneCombination

class UniformCrossover(BaseCrossover):
    
    def __init__(self, var_combination: BaseGeneCombination, mutator: BaseChromosomeMutator, immigrator: BaseChromosomeImmigrator):
        super(UniformCrossover, self).__init__(var_combination, mutator, immigrator)
        self.gene_combination = var_combination
    
    def get_mother_father_genes(self, mother: Chromosome, father: Chromosome):
        father_gene = father[self.current_gene_number]
        mother_gene = mother[self.current_gene_number]
        return mother_gene, father_gene
    
    def combine(self, mother_gene: Gene, father_gene: Gene):
        if self.gene_combination is None:
            raise Exception("gene_combination must not be null!")
        return self.gene_combination.combine(mother_gene, father_gene)
    
    
    
    