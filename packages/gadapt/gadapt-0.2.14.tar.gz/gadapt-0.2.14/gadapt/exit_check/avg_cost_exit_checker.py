from gadapt.exit_check.base_exit_checker import BaseExitChecker

class AvgCostExitChecker(BaseExitChecker):
    def is_exit(self, population):
        if population is None:
            raise Exception("population must not be null")
        return population.avg_cost >= population.previous_avg_cost
        