import gadapt.ga_model.definitions as definitions
class RankingModel:
    def __init__(self):
        self._rank = -1
        self._cummulative_probability = definitions.FLOAT_NAN
    
    @property
    def rank(self):
        return self._rank
    
    @rank.setter
    def rank(self, value):
        self._rank = value
    
    @property
    def cummulative_probability(self):
        return self._cummulative_probability
    
    @cummulative_probability.setter
    def cummulative_probability(self, value):
        self._cummulative_probability = value

    def replace_rank(self, rank):
        self.rank = rank
        return self

    def reset_for_sampling(self):
        self._rank = -1
        self._cummulative_probability = definitions.FLOAT_NAN