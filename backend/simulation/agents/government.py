import numpy as np
from rl.rewards import RewardFunctions


class GovernmentAgent:
    """
    Government controls macro levers and optimizes systemic stability.
    Action space:
    [interest_rate, tax_rate, welfare_spending, capital_controls]
    """

    def __init__(self, config):
        self.config = config

        # ---- Policy bounds ----
        self.min_interest = 0.0
        self.max_interest = 0.2

        self.min_tax = 0.0
        self.max_tax = 0.6

        self.min_welfare = 0.0
        self.max_welfare = 0.5

        self.min_controls = 0.0
        self.max_controls = 1.0

        # ---- GDP history for growth computation ----
        self.prev_gdp = None

    # --------------------------------------------------
    # Policy (Rule-based baseline, RL can replace this)
    # --------------------------------------------------
    def act(self, observation):
        """
        Observation vector (assumed normalized):
        [inflation, unemployment, unrest, inequality, gdp_level]
        """

        inflation, unemployment, unrest, inequality, _ = observation

        # ---- Interest rate: fight inflation, ignore growth pain ----
        interest_rate = np.clip(
            0.02 + 0.15 * inflation,
            self.min_interest,
            self.max_interest
        )

        # ---- Tax rate: redistribute only when unrest is dangerous ----
        tax_rate = np.clip(
            0.15 + 0.4 * inequality * unrest,
            self.min_tax,
            self.max_tax
        )

        # ---- Welfare: pacification mechanism ----
        welfare_spending = np.clip(
            0.1 + 0.5 * unrest,
            self.min_welfare,
            self.max_welfare
        )

        # ---- Capital controls: emergency brake ----
        capital_controls = np.clip(
            unrest ** 2,
            self.min_controls,
            self.max_controls
        )

        return np.array([
            interest_rate,
            tax_rate,
            welfare_spending,
            capital_controls
        ], dtype=np.float32)

    # --------------------------------------------------
    # Reward Computation (No placeholders)
    # --------------------------------------------------
    def compute_reward(self, global_state):
        """
        Uses macro aggregates from global_state.
        """

        # ---- GDP Growth ----
        current_gdp = global_state.economics.gdp
        if self.prev_gdp is None:
            gdp_growth = 0.0
        else:
            gdp_growth = (current_gdp - self.prev_gdp) / max(self.prev_gdp, 1e-6)

        self.prev_gdp = current_gdp

        # ---- Macro indicators ----
        inflation = global_state.economics.inflation
        unemployment = global_state.economics.unemployment
        inequality = global_state.economics.gini_coeff

        # ---- Aggregate unrest (population-weighted) ----
        unrest = self._aggregate_unrest(global_state)

        # ---- Reward ----
        reward = RewardFunctions.government_reward(
            gdp_growth=gdp_growth,
            inflation=inflation,
            unemployment=unemployment,
            unrest=unrest,
            inequality=inequality
        )

        return reward

    # --------------------------------------------------
    # Internal helpers
    # --------------------------------------------------
    def _aggregate_unrest(self, global_state):
        """
        Computes population-weighted unrest from households.
        """

        households = global_state.households

        if len(households) == 0:
            return 0.0

        total_pop = 0.0
        weighted_unrest = 0.0

        for h in households:
            pop = max(h.size, 1.0)
            total_pop += pop
            weighted_unrest += pop * h.unrest_level

        return np.clip(weighted_unrest / total_pop, 0.0, 1.0)
