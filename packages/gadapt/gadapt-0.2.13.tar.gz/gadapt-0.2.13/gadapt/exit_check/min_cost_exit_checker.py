from gadapt.exit_check.base_exit_checker import BaseExitChecker

class MinCostExitChecker(BaseExitChecker):
    def is_exit(self, population):
        if population is None:
            raise Exception("population must not be null")
        return population.min_cost >= population.previous_min_cost