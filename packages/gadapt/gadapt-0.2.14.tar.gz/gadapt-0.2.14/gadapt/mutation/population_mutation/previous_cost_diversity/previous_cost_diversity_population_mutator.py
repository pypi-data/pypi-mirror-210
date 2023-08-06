from ast import List
from gadapt.ga_model.chromosome import Chromosome
from gadapt.ga_model.ga_options import GAOptions
from gadapt.mutation.population_mutation.base_population_mutator import BasePopulationMutator
from gadapt.mutation.population_mutation.previous_cost_diversity.previous_cost_diversity_property_taker import BasePreviousCostDiversityPropertyTaker
import gadapt.utils.ga_utils as ga_utils
import statistics as stat
import gadapt.ga_model.definitions as definitions

class PreviousCostDiversityPopulationMutator(BasePopulationMutator):
        
    def __init__(self, options: GAOptions, population_mutator_for_execution: BasePopulationMutator, property_taker: BasePreviousCostDiversityPropertyTaker) -> None:
        super().__init__(options)
        self.population_mutator_for_execution = population_mutator_for_execution
        self.property_taker = property_taker
        self.first_cost = definitions.FLOAT_NAN
        self.previous_avg_costs: List[float] = []
        self.previous_min_costs: List[float] = []
        self.mutation_rate_sample_number = 10
        
    @property
    def first_cost(self) -> float:
        return self._first_cost

    @first_cost.setter
    def first_cost(self, value: float):
        self._first_cost = value    
    
    def before_exit_check(self, population):
        self.add_previous_costs(population)    

    def after_first_execution(self, population):
        self.first_cost = population.first_cost 

    @property
    def population_mutator_for_execution(self) -> BasePopulationMutator:
        return self._population_mutator_for_execution

    @population_mutator_for_execution.setter
    def population_mutator_for_execution(self, value: BasePopulationMutator):
        self._population_mutator_for_execution = value 
    
    def get_number_of_mutation_cromosomes(self, number_of_mutation_chromosomes) -> int:
        def get_mutation_rate() -> float:
            previous_costs = self.property_taker.take_property(self)
            prev_avg_costs_len = len(previous_costs)
            if prev_avg_costs_len < 2:
                return 0    
            stddev = stat.stdev(previous_costs)
            rel_stddev = stddev / abs(ga_utils.average(previous_costs))
            if (rel_stddev > 1):
                return 0
            return 1 - rel_stddev
        mutation_rate = get_mutation_rate()
        f_return_value = mutation_rate * float(number_of_mutation_chromosomes)
        return round(f_return_value)
    
    def add_previous_costs(self, population):
        min_c = population.min_cost - population.first_cost
        avg_c = population.avg_cost - population.first_cost
        if len(self.previous_avg_costs) < self.mutation_rate_sample_number:
            self.previous_avg_costs.append(avg_c)
            self.previous_min_costs.append(min_c)
            return
        self.reorder_costs(self.previous_avg_costs, avg_c)
        self.reorder_costs(self.previous_min_costs, min_c)        

    def reorder_costs(self, arr, d):
        max_index = len(arr) - 1
        if max_index >= self.mutation_rate_sample_number:
            max_index = self.mutation_rate_sample_number - 1
        for i in range(max_index):
            arr[i] = arr[i + 1]
        arr[max_index] = d
    
    def mutate_population(self, population, number_of_mutation_chromosomes):
        if population is None:
            raise Exception("Population must not be null")
        current_number_of_mutation_chromosomes = self.get_number_of_mutation_cromosomes(
            number_of_mutation_chromosomes)
        return self.population_mutator_for_execution.mutate_population(population, current_number_of_mutation_chromosomes)