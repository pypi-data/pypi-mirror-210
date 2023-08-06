import sys
from gadapt.execution.ga_executor import GAExecutor
from gadapt.factory.ga_factory import GAFactory
from gadapt.ga_model.genetic_variable import GeneticVariable
from gadapt.ga_model.ga_options import GAOptions
from gadapt.ga_model.ga_results import GAResults
from gadapt.ga_model.population import Population
import gadapt.utils.ga_utils as ga_utils
import gadapt.ga_model.definitions as definitions

class GA:
    def __init__(self,
                 cost_function = None,
                 population_size = 64, 
                 exit_check = definitions.AVG_COST,
                 requested_cost = sys.float_info.max,
                 max_attempt_no = 10,
                 parent_selection = definitions.ROULETTE_WHEEL,
                 population_mutation = definitions.COST_DIVERSITY, 
                 number_of_mutation_chromosomes = 1,    
                 parent_diversity_mutation_chromosome_selection = definitions.ROULETTE_WHEEL, 
                 must_mutate_for_same_parents = True,
                 chromosome_mutation = definitions.CROSS_DIVERSITY,                                        
                 number_of_mutation_genes = 1,                     
                 cross_diversity_mutation_gene_selection = definitions.ROULETTE_WHEEL,
                 immigration_number = 0,                                                                                   
                 logging = False,                                                              
                 timeout = 120
                 ) -> None:                     
        self.cost_function = cost_function
        self.population_size = population_size
        self.exit_check = exit_check 
        self.requested_cost = requested_cost 
        self.max_attempt_no = max_attempt_no
        self.parent_selection = parent_selection
        self.population_mutation = population_mutation
        self.must_mutate_for_same_parents = must_mutate_for_same_parents
        self._number_of_mutation_chromosomes = -1
        self.number_of_mutation_chromosomes = number_of_mutation_chromosomes
        self._number_of_mutation_chromosomes_changed = False
        self.number_of_mutation_genes = number_of_mutation_genes
        self.chromosome_mutation = chromosome_mutation        
        self.immigration_number = immigration_number                                              
        self.logging = logging
        self._genetic_variables = []        
        self.cross_diversity_mutation_gene_selection = cross_diversity_mutation_gene_selection
        self.parent_diversity_mutation_chromosome_selection = parent_diversity_mutation_chromosome_selection        
        self.timeout = timeout 
        self._current_gv_id = 0               

    def execute(self) -> GAResults:        
        return GAExecutor(GAOptions(self) , GAFactory(self)).execute()
        
    @property
    def population_size(self) -> int:
        return self._population_size
    
    @population_size.setter
    def population_size(self, value: int):
        self._population_size = ga_utils.try_get_int(value)

    def add(self, min_value: float, max_value:float, step: float=0.01):    
        if (not isinstance(min_value, float) and not isinstance(min_value, int)) or (not isinstance(max_value, float) and not isinstance(max_value, int)):
            raise Exception("min value, max value and step must be numerical values!")
        genetic_variable = GeneticVariable(self._current_gv_id)
        genetic_variable.min_value = min_value
        genetic_variable.max_value = max_value
        genetic_variable.step = step
        self._genetic_variables.append(genetic_variable)
        self._current_gv_id += 1

    @property
    def cost_function(self):
        return self._cost_function
    
    @cost_function.setter
    def cost_function(self, value):
        self._cost_function = value

    @property
    def number_of_mutation_genes(self) -> int:
        return self._number_of_mutation_genes
    
    @number_of_mutation_genes.setter
    def number_of_mutation_genes(self, value: int):
        self._number_of_mutation_genes = ga_utils.try_get_int(value)

    @property
    def number_of_mutation_chromosomes(self) -> int:
        return self._number_of_mutation_chromosomes
    
    @number_of_mutation_chromosomes.setter
    def number_of_mutation_chromosomes(self, value: int):
        first_time = self._number_of_mutation_chromosomes == -1
        self._number_of_mutation_chromosomes = ga_utils.try_get_int(value)
        if not first_time:
            self._number_of_mutation_chromosomes_changed = True

    @property
    def immigration_number(self) -> int:
        return self._immigration_number
    
    @immigration_number.setter
    def immigration_number(self, value: int):
        self._immigration_number = ga_utils.try_get_int(value)
    
    @property
    def population_mutation(self) -> str:
        return self._population_mutation

    @population_mutation.setter
    def population_mutation(self, value: str):
        self._population_mutation = ga_utils.prepare_string(value)

    @property
    def parent_diversity_mutation_chromosome_selection(self) -> str:
        return self._parent_diversity_mutation_chromosome_selection

    @parent_diversity_mutation_chromosome_selection.setter
    def parent_diversity_mutation_chromosome_selection(self, value: str):
        self._parent_diversity_mutation_chromosome_selection = ga_utils.prepare_string(value)

    @property
    def chromosome_mutation(self) -> str:
        return self._chromosome_mutation

    @chromosome_mutation.setter
    def chromosome_mutation(self, value: str):
        self._chromosome_mutation = ga_utils.prepare_string(value)

    @property
    def cross_diversity_mutation_gene_selection(self) -> str:
        return self._cross_diversity_mutation_gene_selection

    @cross_diversity_mutation_gene_selection.setter
    def cross_diversity_mutation_gene_selection(self, value: str):
        self._cross_diversity_mutation_gene_selection = ga_utils.prepare_string(value)

    @property
    def max_attempt_no(self) -> int:
        return self._max_attempt_no

    @max_attempt_no.setter
    def max_attempt_no(self, value: int):
        self._max_attempt_no = ga_utils.try_get_int(value)

    @property
    def exit_check(self) -> str:
        return self._exit_check

    @exit_check.setter
    def exit_check(self, value: str):
        self._exit_check = ga_utils.prepare_string(value)

    @property
    def parent_selection(self) -> str:
        return self._parent_selection

    @parent_selection.setter
    def parent_selection(self, value: str):
        self._parent_selection = ga_utils.prepare_string(value)

    @property
    def requested_cost(self) -> float:
        return self._requested_cost

    @requested_cost.setter
    def requested_cost(self, value: float):
        self._requested_cost = ga_utils.try_get_float(value)

    @property
    def logging(self) -> bool:
        return self._logging
    
    @logging.setter
    def logging(self, value: bool):
        self._logging = ga_utils.try_get_bool(value)

    @property
    def must_mutate_for_same_parents(self) -> bool:
        return self._must_mutate_for_same_parents
    
    @must_mutate_for_same_parents.setter
    def must_mutate_for_same_parents(self, value: bool):
        self._must_mutate_for_same_parents = ga_utils.try_get_bool(value)
    
    @property
    def timeout(self) -> int:
        return self._timeout
    
    @timeout.setter
    def timeout(self, value: int):
        self._timeout = ga_utils.try_get_int(value)
    
