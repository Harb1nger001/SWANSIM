import numpy as np
from rl.rewards import RewardFunctions


class HouseholdAgent:
    """
    Household agent with social learning, consumption, savings,
    and unrest behavior.
    """

    SOCIAL_CLASS_PARAMS = {
        "poor": {"income_mean": 50, "income_std": 10, "propensity_to_protest": 0.5},
        "working": {"income_mean": 100, "income_std": 20, "propensity_to_protest": 0.3},
        "middle": {"income_mean": 300, "income_std": 50, "propensity_to_protest": 0.2},
        "elite": {"income_mean": 1000, "income_std": 200, "propensity_to_protest": 0.05},
    }

    def __init__(self, id, social_class, config):
        self.id = id
        self.social_class = social_class
        self.config = config

        # Initialize wealth
        income_params = self.SOCIAL_CLASS_PARAMS[social_class]
        self.wealth = float(np.random.normal(income_params["income_mean"], income_params["income_std"]))
        self.consumption = 0.0
        self.savings = 0.0
        self.unrest = 0.0

    # --------------------------------------------------
    # Action (Consumption, Savings, Protest)
    # --------------------------------------------------
    def act(self, observation, policy_network=None):
        """
        Observation could include:
        [inflation, unemployment, social_unrest, gdp_growth, personal_wealth]

        Returns: action vector (consumption_pct, savings_pct, protest_pct)
        """

        if policy_network is not None:
            action = policy_network(observation)
        else:
            # Baseline rule: consume % of wealth based on class, save the rest, protest proportional to unrest
            base = self.SOCIAL_CLASS_PARAMS[self.social_class]["propensity_to_protest"]
            consumption_pct = np.clip(0.5 + 0.2 * (1 - base), 0.0, 1.0)
            savings_pct = 1.0 - consumption_pct
            protest_pct = np.clip(base * observation[2], 0.0, 1.0)
            action = np.array([consumption_pct, savings_pct, protest_pct], dtype=np.float32)

        # Update internal states
        self.consumption = self.wealth * action[0]
        self.savings = self.wealth * action[1]
        self.unrest = action[2]

        # Update wealth after consumption (simplified)
        self.wealth = self.savings

        return action

    # --------------------------------------------------
    # Reward Computation
    # --------------------------------------------------
    def compute_reward(self, global_state, local_exposure):
        """
        Computes household reward based on:
        - Consumption utility
        - Inflation
        - Unemployment
        - Social exposure to unrest
        """

        inflation = global_state.economics.inflation
        unemployment = global_state.economics.unemployment

        reward = RewardFunctions.household_reward(
            consumption_utility=RewardFunctions.utility_consumption(self.consumption),
            inflation=inflation,
            unemployment=unemployment,
            unrest_exposure=local_exposure
        )

        return reward

    # --------------------------------------------------
    # Social Exposure Update (optional helper)
    # --------------------------------------------------
    def update_unrest_from_network(self, neighbors):
        """
        neighbors: list of HouseholdAgent
        Simple average unrest of connected agents
        """
        if not neighbors:
            self.unrest_exposure = self.unrest
        else:
            self.unrest_exposure = np.mean([n.unrest for n in neighbors])
        return self.unrest_exposure
