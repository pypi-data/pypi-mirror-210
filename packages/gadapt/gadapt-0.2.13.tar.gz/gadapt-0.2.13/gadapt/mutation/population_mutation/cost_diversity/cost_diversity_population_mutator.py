from ast import List
import math
from gadapt.ga_model.chromosome import Chromosome
from gadapt.ga_model.ga_options import GAOptions
from gadapt.mutation.population_mutation.base_population_mutator import BasePopulationMutator
import gadapt.utils.ga_utils as ga_utils
import statistics as stat
import gadapt.ga_model.definitions as definitions

class CostDiversityPopulationMutator(BasePopulationMutator):
        
    def __init__(self, options: GAOptions, population_mutator_for_execution: BasePopulationMutator) -> None:
        super().__init__(options)
        self.population_mutator_for_execution = population_mutator_for_execution
        self.first_cost = definitions.FLOAT_NAN
        
    @property
    def first_cost(self) -> float:
        return self._first_cost

    @first_cost.setter
    def first_cost(self, value: float):
        self._first_cost = value       

    def after_first_execution(self, population):
        self.first_cost = population.first_cost 

    @property
    def population_mutator_for_execution(self) -> BasePopulationMutator:
        return self._population_mutator_for_execution

    @population_mutator_for_execution.setter
    def population_mutator_for_execution(self, value: BasePopulationMutator):
        self._population_mutator_for_execution = value 
    
    def get_number_of_mutation_cromosomes(self, allocated_chromosomes, number_of_mutation_chromosomes) -> int:
        def get_mutation_rate() -> float:
            current_costs = []
            current_min_value = min(allocated_chromosomes, key=lambda x: x.cost_value)
            for c in allocated_chromosomes:
                #current_costs.append(c.cost_value - self.first_cost)  
                #current_costs.append(c.cost_value)  
                current_costs.append(c.cost_value - current_min_value.cost_value) 
            stddev = stat.stdev(current_costs)
            avg = abs(ga_utils.average(current_costs))
            if avg == 0:
                rel_stddev = 0
            else:
                rel_stddev = stddev / avg
            if (rel_stddev > 1):
                return 0
            return 1 - rel_stddev
        mutation_rate = get_mutation_rate()
        f_return_value = mutation_rate * float(number_of_mutation_chromosomes)
        return round(f_return_value)
    
    def mutate_population(self, population, number_of_mutation_chromosomes):
        if population is None:
            raise Exception("Population must not be null")
        allocated_chromosomes = [c for c in population if not math.isnan(c.cost_value)]
        current_number_of_mutation_chromosomes = self.get_number_of_mutation_cromosomes(allocated_chromosomes,
            number_of_mutation_chromosomes)
        return self.population_mutator_for_execution.mutate_population(population, current_number_of_mutation_chromosomes)