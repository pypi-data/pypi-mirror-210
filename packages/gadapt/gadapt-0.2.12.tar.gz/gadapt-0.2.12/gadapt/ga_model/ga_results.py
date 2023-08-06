from typing import List
import gadapt.string_operation.ga_strings as ga_strings

class GAResults:
    def __init__(self) -> None:
        self._success = True
        self.result_values = {}
        self._messages = []

    def __str__(self) -> str:
       return ga_strings.results_to_string(self)

    
    @property
    def result_values(self):
        return self._result_values

    @result_values.setter
    def result_values(self, value):
        self._result_values = value

    @property
    def min_cost(self) -> float:
        return self._min_cost

    @min_cost.setter
    def min_cost(self, value: float):
        self._min_cost = value

    @property
    def number_of_iterations(self) -> float:
        return self._number_of_iterations

    @number_of_iterations.setter
    def number_of_iterations(self, value: float):
        self._number_of_iterations = value


    @property
    def success(self) -> bool:
        return self._success

    @success.setter
    def success(self, value: bool):
        self._success = value

    @property
    def messages(self):
        return self._messages

    @messages.setter
    def messages(self, value):
        self._messages = value

    @property
    def message(self) -> str:
        return self._get_message()

    def _get_message(self):
        return ga_strings.get_results_message(self)

    