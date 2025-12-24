import numpy as np

class FirmAgent:
    def __init__(self, id, archetype, config):
        self.id = id
        self.archetype = archetype  # 'startup', 'sme', 'mnc'
        self.config = config

        # Initial capital by archetype
        self.capital = (
            1_000.0 if archetype == 'startup'
            else 10_000.0 if archetype == 'sme'
            else 100_000.0
        )

        self.employees = 0
        self.production = 0.0
        self.price = 10.0
        self.alive = True

        # Structural advantages
        self.productivity = {
            'startup': 0.8,
            'sme': 1.0,
            'mnc': 1.3
        }[archetype]

        self.pricing_power = {
            'startup': 0.9,
            'sme': 1.0,
            'mnc': 1.2
        }[archetype]

        self.credit_cost = {
            'startup': 0.10,
            'sme': 0.06,
            'mnc': 0.03
        }[archetype]

    def step(self, market_conditions):
        """
        Decide Price and Desired Labor.
        """
        if not self.alive:
            self.desired_labor = 0
            self.production = 0
            return

        demand = market_conditions['demand']
        wage = market_conditions['wage']
        inflation = market_conditions['inflation']
        shock = market_conditions.get('shock_multiplier', 1.0)

        # 1. Expected demand
        # Ensure a minimum demand signal to prevent death spiral at startup
        effective_demand = max(demand, 100.0) 
        expected_demand = effective_demand * shock * self.productivity

        # 2. Decide labor demand (constrained by capital)
        # We want to produce expected_demand
        labor_required = int(expected_demand / self.productivity)
        
        # Can we afford this labor?
        max_labor_budget = self.capital / max(wage, 1.0)
        self.desired_labor = min(labor_required, int(max_labor_budget))

        # 3. Set price
        self.price *= (1 + inflation * 0.5 * self.pricing_power)
        
        # Reset per-step variables
        self.revenue = 0.0
        self.wage_bill = 0.0

    def produce(self):
        """Called after labor market matches employees."""
        self.production = self.employees * self.productivity

    def post_market_step(self):
        """Called after all markets clear to settle accounts."""
        if not self.alive:
            return

        # Capital costs
        capital_cost = self.capital * self.credit_cost
        
        # Profit
        profit = self.revenue - self.wage_bill - capital_cost
        self.capital += profit
        
        if self.capital < 0:
            self.alive = False
            self.employees = 0
            self.production = 0.0
