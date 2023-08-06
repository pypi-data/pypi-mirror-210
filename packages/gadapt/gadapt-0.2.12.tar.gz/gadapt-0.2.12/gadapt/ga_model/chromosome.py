from typing import List
from gadapt.ga_model.gene import Gene
from gadapt.ga_model.genetic_variable import GeneticVariable
from gadapt.ga_model.ranking_model import RankingModel
from gadapt.immigration.chromosome_immigration.base_chromosome_immigrator import BaseChromosomeImmigrator
from gadapt.mutation.chromosome_mutation.base_chromosome_mutator import BaseChromosomeMutator
import gadapt.ga_model.definitions as definitions
import gadapt.string_operation.ga_strings as ga_strings
class Chromosome (RankingModel):
    
    def __init__(self, mutator: BaseChromosomeMutator, immigrator: BaseChromosomeImmigrator, population_generation: int):
        super().__init__()
        self._mutator = mutator
        self._immigrator = immigrator
        self.cost_value = definitions.FLOAT_NAN
        self._is_immigrant = False
        self.population_generation = population_generation
        self._chromosome_id = None
        self._mutated_variables_id_list = []
        self.first_mutant_generation = 0
        self.first_immigrant_generation = 0
        self.last_mutant_generation = 0
        self.last_immigrant_generation = 0
        self._chromosome_string = None
        self._mother_id = -1
        self.father_id = -1
        self._is_mutated = False
        self._is_immigrant = False
        self.genes = []
        
    def __str__(self):
        return self.get_chromosome_string()
    
    def __getitem__(self, index):
        return self.genes[index]

    def __next__(self):
        return next(self.genes)

    def __len__(self):
        return len(self.genes)

    def get_sorted(self, key: None = None, reverse: bool = False):
        return sorted(self.genes, key=key, reverse=reverse)

    def append(self, g: Gene):
        self.genes.append(g)

    def clear(self):
        self.genes.clear()

    def to_string(self):
        return ga_strings.chromosome_to_string(self)

    def set_chromosome_string(self, value: str):
        if value is None:
           self._chromosome_string  = None 

    def get_chromosome_string(self):
        if self._chromosome_string is None:
            self._chromosome_string = self.to_string()
        return self._chromosome_string

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
    def number_of_mutation_genes(self):
        return self._number_of_mutation_genes
    
    @number_of_mutation_genes.setter
    def number_of_mutation_genes(self, value):
        self._number_of_mutation_genes = value

    @property
    def chromosome_id(self):
        return self._chromosome_id
    
    @chromosome_id.setter
    def chromosome_id(self, value):
        self._chromosome_id = value

    @property
    def cost_value(self):
        return self._cost_value
    
    @cost_value.setter
    def cost_value(self, value):
        self._cost_value = value

    @property
    def is_mutated(self) -> bool:
        return self._is_mutated
    
    @is_mutated.setter
    def is_mutated(self, value: bool):
        self._is_mutated = value

    @property
    def is_immigrant(self) -> bool:
        return self._is_immigrant
    
    @is_immigrant.setter
    def is_immigrant(self, value: bool):
        self._is_immigrant = value

    @property
    def mother_id(self) -> int:
        return self._mother_id
    
    @mother_id.setter
    def mother_id(self, value: int):
        self._mother_id = value

    @property
    def father_id(self) -> int:
        return self._father_id
    
    @father_id.setter
    def father_id(self, value: int):
        self._father_id = value

    def add_gene(self, gen_var: GeneticVariable, gen_var_value: float = definitions.FLOAT_NAN):
        g = Gene(gen_var, gen_var_value)
        self.append(g)

    @property
    def parents_diversity(self) -> float:
        return self._parents_diversity
    
    @parents_diversity.setter
    def parents_diversity(self, value: float):
        self._parents_diversity = value

    @property
    def population_generation(self) -> int:
        return self._population_generation
    
    @population_generation.setter
    def population_generation(self, value: int):
        self._population_generation = value

    @property
    def chromosome_generation(self) -> int:
        return self._chromosome_generation
    
    @chromosome_generation.setter
    def chromosome_generation(self, value: int):
        self._chromosome_generation = value

    @property
    def first_mutant_generation(self) -> int:
        return self._first_mutant_generation
    
    @first_mutant_generation.setter
    def first_mutant_generation(self, value: int):
        self._first_mutant_generation = value    

    @property
    def last_mutant_generation(self) -> int:
        return self._last_mutant_generation
    
    @property
    def first_immigrant_generation(self) -> int:
        return self._first_immigrant_generation
    
    @first_immigrant_generation.setter
    def first_immigrant_generation(self, value: int):
        self._first_immigrant_generation = value

    @property
    def last_immigrant_generation(self) -> int:
        return self._last_immigrant_generation
    
    @last_immigrant_generation.setter
    def last_immigrant_generation(self, value: int):
        self._last_immigrant_generation = value
    
    @last_mutant_generation.setter
    def last_mutant_generation(self, value: int):
        self._last_mutant_generation = value

    @property
    def mutation_on_both_sides(self) -> bool:
        return self._mutation_on_both_sides
    
    @mutation_on_both_sides.setter
    def mutation_on_both_sides(self, value: bool):
        self._mutation_on_both_sides = value

    @property
    def succ(self) -> bool:
        return self._succ
    
    @succ.setter
    def succ(self, value: bool):
        self._succ = value

    def mutate(self, number_of_mutation_genes: int):
        self.mutator.mutate(self, number_of_mutation_genes)

    def immigrate(self):
        self.immigrator.immigrate(self)

    @property
    def mutated_variables_id_list(self) -> List[int]:
        return self._mutated_variables_id_list