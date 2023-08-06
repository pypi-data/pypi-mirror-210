from gadapt.ga_model.chromosome import Chromosome
from gadapt.ga_model.gene import Gene
from gadapt.immigration.chromosome_immigration.base_chromosome_immigrator import BaseChromosomeImmigrator
from gadapt.mutation.chromosome_mutation.base_chromosome_mutator import BaseChromosomeMutator
from gadapt.gene_combination.base_gene_combination import BaseGeneCombination
import gadapt.utils.ga_utils as ga_utils
import gadapt.ga_model.definitions as definitions

class BaseCrossover:
    
    def __init__(self, gene_combination: BaseGeneCombination, mutator: BaseChromosomeMutator, immigrator: BaseChromosomeImmigrator):
        self._mutation_on_both_sides = True
        self.gene_combination = gene_combination
        self.mutator = mutator
        self.immigrator = immigrator
    
    @property
    def gene_combination(self) -> BaseGeneCombination:
        return self._gene_combination
    
    @gene_combination.setter
    def gene_combination(self, value: BaseGeneCombination):
        self._gene_combination = value

    @property
    def mutator(self) -> BaseChromosomeMutator:
        return self._mutator
    
    @mutator.setter
    def mutator(self, value: BaseChromosomeMutator):
        self._mutator = value

    @property
    def immigrator(self) -> BaseChromosomeImmigrator:
        return self._immigrator
    
    @immigrator.setter
    def immigrator(self, value: BaseChromosomeImmigrator):
        self._immigrator = value

    
    @property
    def mutation_on_both_sides(self) -> bool:
        return self._mutation_on_both_sides
    
    @mutation_on_both_sides.setter
    def mutation_on_both_sides(self, value: bool):
        self._mutation_on_both_sides = value    
    
    def mate(self, mother: Chromosome, father: Chromosome, population_generation: int):
        def get_genetic_diversity(g_m: Gene, g_f: Gene) -> float:
            return abs(g_m.variable_value - g_f.variable_value) / (g_f.genetic_variable.max_value - g_f.genetic_variable.min_value)

        self.mate_init()
        if (len(mother) != len(father)):
            raise Exception("Mother and father must have the same number of genes!")
        offspring1 = Chromosome(self.mutator, self.immigrator, population_generation)
        offspring2 = Chromosome(self.mutator, self.immigrator, population_generation)
        self.number_of_genes = len(father)
        genetic_diversity = []
        for self.current_gene_number in range(self.number_of_genes):
            mother_gene, father_gene = self.get_mother_father_genes(mother, father)
            self.genetic_variable_father = father_gene.genetic_variable
            genetic_variable_mother = mother_gene.genetic_variable
            if (self.genetic_variable_father != genetic_variable_mother):
                genetic_variable_mother = next((item.genetic_variable for item in mother if item.genetic_variable == self.genetic_variable), None)
            if (genetic_variable_mother is None):
                raise Exception("chromosomes in crossover do not have the same structure!")
            genetic_diversity.append(get_genetic_diversity(mother_gene, father_gene))
            var1, var2 = self.combine(mother_gene, father_gene)
            offspring1.add_gene(self.genetic_variable_father, var1)
            offspring2.add_gene(self.genetic_variable_father, var2)
        parrents_diversity = round(ga_utils.average(genetic_diversity), 2)
        offspring1.parents_diversity = parrents_diversity
        offspring2.parents_diversity = parrents_diversity
        offspring1.mutation_on_both_sides = self.mutation_on_both_sides
        offspring2.mutation_on_both_sides = self.mutation_on_both_sides
        offspring1.mother_id = mother.chromosome_id
        offspring2.mother_id = mother.chromosome_id
        offspring1.father_id = father.chromosome_id
        offspring2.father_id = father.chromosome_id
        self.increase_generation(offspring1, offspring2, mother, father)
        return offspring1, offspring2
    
    def mate_init(self):
        pass

    def get_mother_father_genes(self, mother: Chromosome, father: Chromosome):
        raise Exception(definitions.NOT_IMPLEMENTED)

    def combine(self, mother_gene: Gene, father_gene: Gene):
        raise Exception(definitions.NOT_IMPLEMENTED)
    
    def increase_generation(self, offspring1: Chromosome, offspring2: Chromosome, mother: Chromosome, father: Chromosome):
        current_generation = mother.chromosome_generation
        if current_generation == 0 or current_generation < father.chromosome_generation:
            current_generation = father.chromosome_generation
        current_generation += 1
        offspring1.chromosome_generation = current_generation 
        offspring2.chromosome_generation = current_generation

        current_generation = 0
        if mother.first_mutant_generation > 0 or father.first_mutant_generation > 0:
            current_generation = mother.first_mutant_generation
            if current_generation == 0 or father.first_mutant_generation > current_generation:
                current_generation = father.first_mutant_generation
            current_generation +=1
        offspring1.first_mutant_generation = current_generation
        offspring2.first_mutant_generation = current_generation

        current_generation = 0
        if mother.last_mutant_generation > 0 or father.last_mutant_generation > 0:
            current_generation = mother.last_mutant_generation
            if current_generation == 0 or (father.last_mutant_generation > 0 and father.last_mutant_generation < current_generation):
                current_generation = father.last_mutant_generation
            current_generation +=1
        offspring1.last_mutant_generation = current_generation
        offspring2.last_mutant_generation = current_generation

        current_generation = 0
        if mother.first_immigrant_generation > 0 or father.first_immigrant_generation > 0:
            current_generation = mother.first_immigrant_generation
            if current_generation == 0 or father.first_immigrant_generation > current_generation:
                current_generation = father.first_immigrant_generation
            current_generation +=1
        offspring1.first_immigrant_generation = current_generation
        offspring2.first_immigrant_generation = current_generation

        current_generation = 0
        if mother.last_immigrant_generation > 0 or father.last_immigrant_generation > 0:
            current_generation = mother.last_immigrant_generation
            if current_generation == 0 or (father.last_immigrant_generation > 0 and father.last_immigrant_generation < current_generation):
                current_generation = father.last_immigrant_generation
            current_generation +=1
        offspring1.last_immigrant_generation = current_generation
        offspring2.last_immigrant_generation = current_generation