from typing import List
from gadapt.ga_model.genetic_variable import GeneticVariable
class GAOptions():
   
    def __init__(self, ga) -> None:
        super().__init__()           
        self._population_size = ga.population_size
        self._cost_function = ga.cost_function                
        self._immigration_number = ga.immigration_number
        self.set_number_of_mutation_chromosomes(ga)
        self._max_attempt_no = ga.max_attempt_no
        self._requested_cost = ga.requested_cost
        self._logging = ga.logging
        self._genetic_variables = ga._genetic_variables
        self.set_number_of_mutation_genes(ga)
        self._must_mutate_for_same_parents = ga.must_mutate_for_same_parents
        self._timeout = ga.timeout

    def set_number_of_mutation_chromosomes(self, ga):
        if (not ga.number_of_mutation_chromosomes is None) and isinstance(ga.number_of_mutation_chromosomes, int) and ga.number_of_mutation_chromosomes >= 0:                  
            self._number_of_mutation_chromosomes = ga.number_of_mutation_chromosomes
        elif (not ga.percentage_of_mutation_chromosomes is None) and isinstance(ga.percentage_of_mutation_chromosomes, float) and ga.percentage_of_mutation_chromosomes >= 0.0 and ga.percentage_of_mutation_chromosomes <= 100:
            nomc = round(self.population_size * (ga.percentage_of_mutation_chromosomes / 100))
            while nomc >= self.population_size //2 - self.immigration_number:
                nomc -= 1
            if nomc < 0:
                raise Exception("Invalid percentage of mutation chromosomes and immigration number")
            self._number_of_mutation_chromosomes = nomc
        else:
            self._number_of_mutation_chromosomes = ga.number_of_mutation_chromosomes

    def set_number_of_mutation_genes(self, ga):
        if (not ga.number_of_mutation_genes is None) and isinstance(ga.number_of_mutation_genes, int) and ga.number_of_mutation_genes >= 0:
            self._number_of_mutation_genes = ga.number_of_mutation_genes  
        elif (not ga.percentage_of_mutation_genes is None) and isinstance(ga.percentage_of_mutation_genes, float) and ga.percentage_of_mutation_genes >= 0.0 and ga.percentage_of_mutation_genes <= 100:
            self._number_of_mutation_genes = round(float(len(self._genetic_variables)) * (ga.percentage_of_mutation_genes / 100))
        else:
            self._number_of_mutation_genes = ga.number_of_mutation_genes
    
    @property
    def requested_cost(self) -> float:
        return self._requested_cost

    @requested_cost.setter
    def requested_cost(self, value: float):
        self._requested_cost = value
    
    @property
    def max_attempt_no(self) -> int:
        return self._max_attempt_no

    @max_attempt_no.setter
    def max_attempt_no(self, value: int):
        self._max_attempt_no = value
    
    @property
    def immigration_number(self) -> int:
        return self._immigration_number
    
    @immigration_number.setter
    def immigration_number(self, value: int):
        self._immigration_number = value
    
    @property
    def number_of_mutation_chromosomes(self) -> int:
        return self._number_of_mutation_chromosomes
    
    @number_of_mutation_chromosomes.setter
    def number_of_mutation_chromosomes(self, value: int):
        self._number_of_mutation_chromosomes = value
    
    @property
    def number_of_mutation_genes(self) -> int:
        return self._number_of_mutation_genes
    
    @number_of_mutation_genes.setter
    def number_of_mutation_genes(self, value: int):
        self._number_of_mutation_genes = value
    
    @property
    def cost_function(self):
        return self._cost_function
    
    @cost_function.setter
    def cost_function(self, value):
        self._cost_function = value
    
    @property
    def population_size(self) -> int:
        return self._population_size
    
    @population_size.setter
    def population_size(self, value: int):
        self._population_size = value
    
    @property
    def genetic_variables(self) -> List[GeneticVariable]:
        return self._genetic_variables  

    @property
    def abandon_number(self) -> int:
        return self.get_abandon_number()
    
    def get_abandon_number(self) -> int:
        if self.population_size % 2 == 0:
            return self.population_size // 2
        return self.population_size // 2 - 1
    
    @property
    def keep_number(self) -> int:
        return self.population_size - self.abandon_number    

    @property
    def logging(self) -> bool:
        return self._logging
    
    @logging.setter
    def logging(self, value: bool):
        self._logging = value

    @property
    def must_mutate_for_same_parents(self) -> bool:
        return self._must_mutate_for_same_parents
    
    @must_mutate_for_same_parents.setter
    def must_mutate_for_same_parents(self, value: bool):
        self._must_mutate_for_same_parents = value

    @property
    def timeout(self) -> int:
        return self._timeout
    
    @timeout.setter
    def timeout(self, value: int):
        self._timeout = value