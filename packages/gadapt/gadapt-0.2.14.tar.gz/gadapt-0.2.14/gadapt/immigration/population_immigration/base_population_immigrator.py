import gadapt.ga_model.definitions as definitions
class BasePopulationImmigrator:
    def immigrate(self, population):
        raise Exception(definitions.NOT_IMPLEMENTED)