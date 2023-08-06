import gadapt.ga_model.definitions as definitions
class BasePreviousCostDiversityPropertyTaker:
    def take_property(self, mutator):
        raise Exception(definitions.NOT_IMPLEMENTED)
    
class MinPreviousCostCostDiversityPropertyTaker:
    def take_property(self, mutator):
        return mutator.previous_min_costs
    
class AvgPreviousCostCostDiversityPropertyTaker:
    def take_property(self, mutator):
        return mutator.previous_avg_costs    