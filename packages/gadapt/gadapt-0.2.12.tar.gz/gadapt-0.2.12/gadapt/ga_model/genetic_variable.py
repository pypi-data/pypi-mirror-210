import random
import gadapt.ga_model.definitions as definitions
class GeneticVariable:

    def __init__(self, id: int) -> None:
        self.variable_id = id
        self._standard_deviation = definitions.FLOAT_NAN
    
    def __eq__(self, other):
        if not isinstance(other, GeneticVariable):
            return False
        return self.variable_id == other.variable_id
    
    def __hash__(self) -> int:
        return self.variable_id
    
    @property
    def variable_id(self) -> int:
        return self._variable_id
    
    @variable_id.setter
    def variable_id(self, value: int):
        self._variable_id = value
    
    @property
    def variable_name(self) -> str:
        return self._variable_name
    
    @variable_name.setter
    def variable_name(self, value: str):
        self._variable_name = value

    @property
    def initial_value(self) -> float:
        return self._initial_value
    
    @initial_value.setter
    def initial_value(self, value: float):
        self._initial_value = value

    @property
    def max_value(self) -> float:
        return self._max_value
    
    @max_value.setter
    def max_value(self, value: float):
        self._max_value = value

    @property
    def min_value(self) -> float:
        return self._min_value
    
    @min_value.setter
    def min_value(self, value: float):
        self._min_value = value

    @property
    def step(self) -> float:
        return self._step
    
    @step.setter
    def step(self, value: float):
        self._decimal_places = self.get_decimal_places(value)
        self._step = value

    def get_decimal_places(self, f: float) -> int:
        dp = str(f)[::-1].find('.')
        if dp == -1:
            return 0
        return dp

    @property
    def decimal_places(self) -> int:
        return self._decimal_places

    @property
    def stacked(self) -> bool:
        return self._stacked
    
    @stacked.setter
    def stacked(self, value: bool):
        self._stacked = value

    @property
    def relative_standard_deviation(self) -> float:
        return self._standard_deviation
    
    @relative_standard_deviation.setter
    def relative_standard_deviation(self, value: float):
        self._standard_deviation = value        

    def make_random_value(self):
        number_of_steps = random.randint(0, round((self.max_value - self.min_value) / self.step))
        return self.min_value + number_of_steps * self.step