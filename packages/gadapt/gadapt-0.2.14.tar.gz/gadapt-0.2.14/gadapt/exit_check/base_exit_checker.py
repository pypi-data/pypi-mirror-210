import logging
from datetime import datetime
import gadapt.ga_model.definitions as definitions

class BaseExitChecker:
    def __init__(self, max_attempt_no: int) -> None:
        self.max_attempt_no = max_attempt_no
        self.attempt_no = 0              
    
    @property
    def attempt_no(self) -> int:
        return self._attempt_no

    @attempt_no.setter
    def attempt_no(self, value: int):
        self._attempt_no = value

    def check(self, population):
        time_diff = (datetime.now() - population.start_time).total_seconds()
        if time_diff >= population.options.timeout:
            population.timeout_expired = True
            return True
        if self.is_exit(population):
            self.attempt_no += 1
        else:
            self.attempt_no = 0
        if self.attempt_no >= self.max_attempt_no:
            logging.info("function exit.")
            return True
        return False
    
    def is_exit(self, population) -> bool:
        raise Exception(definitions.NOT_IMPLEMENTED)
