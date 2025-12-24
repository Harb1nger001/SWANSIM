import numpy as np
from simulation.shocks.exogenous import ExogenousShock

class ShockManager:
    """
    Manages random and targeted shocks to the system.
    """
    def __init__(self, config):
        self.config = config
        self.active_shocks = []
        
        # Probabilities for random shocks (Increased for testing)
        self.shock_probs = config.get("shock_probs", {
            "pandemic": 0.01,
            "financial_crash": 0.02,
            "supply_chain_collapse": 0.05
        })

    def maybe_trigger(self, state, households, firms):
        """
        Check for random shocks or apply active shocks.
        """
        # 1. Random triggers
        for shock_type, prob in self.shock_probs.items():
            if np.random.random() < prob:
                self.add_shock(shock_type, 0.5)

        # 2. Apply active shocks
        # Decay shocks
        alive_shocks = []
        for shock in self.active_shocks:
            self._apply_shock(shock, state, households, firms)
            shock.duration -= 1
            if shock.duration > 0:
                alive_shocks.append(shock)
        
        self.active_shocks = alive_shocks

    def add_shock(self, shock_type, severity):
        """
        Manual or random injection.
        """
        duration = 10 if shock_type != 'permanent' else 1000
        shock = ExogenousShock(
            type=shock_type,
            severity=severity,
            duration=duration,
            start_step=0 
        )
        self.active_shocks.append(shock)

    def _apply_shock(self, shock, state, households, firms):
        """
        Apply effects based on shock type.
        """
        econ = state.economics

        if shock.type == "pandemic":
            # Reduces labor supply and consumption
            econ.unemployment += 5 * shock.severity
            for h in households:
                h.consumption *= (1.0 - 2 * shock.severity)

        elif shock.type == "financial_crash":
            # Destroys capital and wealth
            for f in firms:
                f.capital *= (1.0 - 8 * shock.severity) # Catastrophic capital destruction
            for h in households:
                h.wealth *= (1.0 - 7 * shock.severity) # Massive wealth evaporation
            
            econ.unemployment += 40 * shock.severity # Mass unemployment

        elif shock.type == "political_coup":
            # Increases unrest huge amount
            for h in households:
                h.unrest = np.clip(h.unrest + 20.0 * shock.severity, 0.0, 1.0) # Instant max unrest
            econ.regime_stability = max(0.0, econ.regime_stability - 1.0 * shock.severity) if hasattr(econ, 'regime_stability') else 0

        elif shock.type == "supply_chain_collapse":
            # Increases inflation, reduces production
            econ.inflation += 50 * shock.severity # Hyperinflation risk
            for f in firms:
                f.productivity *= (1.0 - 6 * shock.severity) # Industry halt
        
        elif shock.type == "cyber_attack":
            # Freezes firm capital and increases unrest
            for f in firms:
                f.capital *= (1.0 - 0.1 * shock.severity) # Less destruction, more freeze (simulated by loss)
            for h in households:
                 # Panic
                h.unrest = np.clip(h.unrest + 3 * shock.severity, 0.0, 1.0)
            
        elif shock.type == "climate_catastrophe":
            # Long term production hit and heavy welfare/wealth cost
            econ.inflation += 20 * shock.severity
            econ.unemployment += 10 * shock.severity
            for f in firms:
                f.productivity *= (1.0 - 4 * shock.severity)
            for h in households:
                h.wealth *= (1.0 - 2 * shock.severity) # Property damage
