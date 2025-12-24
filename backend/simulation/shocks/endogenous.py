class EndogenousShocks:
    def __init__(self, config):
        self.config = config
        
    def check_triggers(self, global_state):
        # Check for revolutions, coups, state failure
        triggers = []
        if global_state.economics.unemployment > 0.3:
            triggers.append("mass_unrest")
        if global_state.economics.gini_coeff > 0.6:
            triggers.append("revolution_risk")
        return triggers
