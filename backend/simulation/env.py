import gymnasium as gym
from gymnasium import spaces
import numpy as np

from simulation.state import GlobalState
from simulation.agents.government import GovernmentAgent
from simulation.agents.households import HouseholdAgent
from simulation.agents.firms import FirmAgent
from simulation.economics.markets import MarketMechanism
from simulation.networks.social_graph import SocialGraph
from simulation.economics.inequality import InequalityMetrics
from simulation.shocks.shock_manager import ShockManager


class BlackSwanEnv(gym.Env):
    """
    Single-environment macro-socioeconomic simulator.
    Government is the learning agent.
    """

    metadata = {"render_modes": ["human"]}

    def __init__(self, config: dict):
        super().__init__()

        self.config = config
        self.max_steps = config.get("max_steps", 500)

        # -----------------------------
        # Core state
        # -----------------------------
        self.state = GlobalState()
        self.timestep = 0

        # -----------------------------
        # Agents
        # -----------------------------
        self.government = GovernmentAgent(config)

        self.households = [
            HouseholdAgent(
                id=i,
                social_class=np.random.choice(
                    ["poor", "working", "middle", "elite"],
                    p=[0.35, 0.35, 0.2, 0.1]
                ),
                config=config
            )
            for i in range(config.get("num_households", 200))
        ]

        self.firms = [
            FirmAgent(
                id=i,
                archetype=np.random.choice(
                    ["startup", "sme", "mnc"],
                    p=[0.5, 0.35, 0.15]
                ),
                config=config
            )
            for i in range(config.get("num_firms", 50))
        ]

        # -----------------------------
        # Systems
        # -----------------------------
        self.market = MarketMechanism(config)
        self.social_graph = SocialGraph(len(self.households), config)
        self.shocks = ShockManager(config)

        # -----------------------------
        # Spaces (government control)
        # -----------------------------
        # Observation:
        # [GDP, inflation, unemployment, gini, avg_unrest,
        #  top1_wealth_share, interest_rate, tax_rate, welfare, capital_controls]
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(10,), dtype=np.float32
        )

        # Action:
        # [interest_rate, tax_rate, welfare_spending, capital_controls]
        self.action_space = spaces.Box(
            low=0.0, high=1.0, shape=(4,), dtype=np.float32
        )

    # --------------------------------------------------
    # Reset
    # --------------------------------------------------
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        self.state = GlobalState()
        self.timestep = 0

        # Reset government memory
        self.government.prev_gdp = 10000.0
        
        # Kickstart economy
        self.state.economics.gdp = 10000.0
        self.state.economics.gdp_last = 10000.0
        self.state.economics.wage_index = 1.0
        self.state.economics.price_index = 1.0

        return self._get_obs(), {}

    # --------------------------------------------------
    # Step
    # --------------------------------------------------
    def step(self, action):
        self.timestep += 1

        # -----------------------------
        # 1. Apply shocks
        # -----------------------------
        self.shocks.maybe_trigger(self.state, self.households, self.firms)

        # -----------------------------
        # 2. Government action
        # -----------------------------
        self.state.economics.apply_policy(action)
        self.government.current_interest_rate = self.state.economics.interest_rate

        # -----------------------------
        # 3. Firms decide production & labor
        # -----------------------------
        market_conditions = {
            "demand": self.state.economics.gdp,
            "wage": self.market.base_wage * self.state.economics.wage_index,
            "inflation": self.state.economics.inflation,
            "interest_rate": self.state.economics.interest_rate
        }
        for f in self.firms:
            f.step(market_conditions)

        # -----------------------------
        # 4. Households act
        # -----------------------------
        household_states = {}
        for h in self.households:
            obs = self._household_obs(h)
            h.act(obs)
            household_states[h.id] = {"unrest": h.unrest}

        # -----------------------------
        # 5. Social unrest diffusion
        # -----------------------------
        updated_unrest = self.social_graph.spread_influence(household_states)
        for h in self.households:
            h.unrest = updated_unrest[h.id]

        # -----------------------------
        # 6. Market clearing
        # -----------------------------
        wage, unemployment = self.market.clear_labor_market(self.households, self.firms)
        
        # Firms produce with hired labor
        for f in self.firms:
            f.produce()
            
        price_multiplier = self.market.clear_goods_market(self.households, self.firms)
        self.market.clear_credit_market(self.firms, self.government)
        
        # Firms settle accounts
        for f in self.firms:
            f.post_market_step()

        # -----------------------------
        # 7. Update macro metrics
        # -----------------------------
        self._update_macros(unemployment)

        # -----------------------------
        # 8. Reward
        # -----------------------------
        reward = self.government.compute_reward(self.state)

        # -----------------------------
        # 9. Termination conditions
        # -----------------------------
        terminated = self._check_collapse()
        truncated = self.timestep >= self.max_steps

        return self._get_obs(), reward, terminated, truncated, {}

    # --------------------------------------------------
    # Observations
    # --------------------------------------------------
    def _get_obs(self):
        econ = self.state.economics

        return np.array([
            econ.gdp,
            econ.inflation,
            econ.unemployment,
            econ.gini_coeff,
            econ.avg_unrest,
            econ.top1_wealth_share,
            econ.interest_rate,
            econ.tax_rate,
            econ.welfare_spending,
            econ.capital_controls
        ], dtype=np.float32)

    def _household_obs(self, h):
        econ = self.state.economics
        return np.array([
            econ.inflation,
            econ.unemployment,
            econ.avg_unrest,
            econ.gdp_growth,
            h.wealth
        ], dtype=np.float32)

    # --------------------------------------------------
    # Macro updates
    # --------------------------------------------------
    def _update_macros(self, unemployment):
        econ = self.state.economics

        # GDP
        econ.gdp = sum(f.revenue for f in self.firms)

        # Inflation (price pressure proxy)
        econ.inflation = np.clip(
            econ.inflation + 0.01 * np.random.randn(),
            0.0, 1.0
        )

        # Unemployment
        econ.unemployment = unemployment

        # Inequality
        wealths = [h.wealth for h in self.households]
        econ.gini_coeff = InequalityMetrics.calculate_gini(wealths)
        econ.top1_wealth_share = InequalityMetrics.calculate_wealth_share(wealths)

        # Unrest
        econ.avg_unrest = np.mean([h.unrest for h in self.households])

        # GDP growth
        econ.update_growth()

    # --------------------------------------------------
    # Collapse logic
    # --------------------------------------------------
    def _check_collapse(self):
        econ = self.state.economics

        # Endogenous revolution
        if econ.avg_unrest > 0.7 and econ.unemployment > 0.15:
            econ.regime = "collapsed"
            return True

        # Economic death
        if econ.gdp < 1e-3:
            econ.regime = "collapsed"
            return True

        return False
