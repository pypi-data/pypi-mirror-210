import gadapt.ga_model.definitions as definitions
class BaseChromosomeImmigrator:
    def immigrate(self, c):
        self.immigrate_chromosome(c)
        self.chromosome_immigrated(c)

    def immigrate_chromosome(self, c):
        raise Exception(definitions.NOT_IMPLEMENTED)

    def chromosome_immigrated(self, c):
        c.is_immigrant = True
        if c.first_immigrant_generation == 0:
            c.first_immigrant_generation += 1
        c.last_immigrant_generation = 1
        c.first_mutant_generation = 0
        c.last_mutant_generation = 0
        c.set_chromosome_string(None)
