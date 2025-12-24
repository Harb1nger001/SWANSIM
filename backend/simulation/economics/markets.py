import numpy as np


class MarketMechanism:
    """
    Clears labor, goods, and credit markets each timestep.
    """

    def __init__(self, config):
        self.config = config

        # Baseline prices
        self.base_wage = config.get("base_wage", 50.0)
        self.price_adjustment = config.get("price_adjustment", 0.1)
        self.wage_adjustment = config.get("wage_adjustment", 0.1)

        # Credit parameters
        self.base_interest_rate = config.get("base_interest_rate", 0.05)
        self.max_leverage = config.get("max_leverage", 3.0)

    # --------------------------------------------------
    # Labor Market
    # --------------------------------------------------
    def clear_labor_market(self, households, firms):
        """
        Matches household labor supply with firm labor demand.
        Updates wages, employment, and unemployment.
        """

        # ---- Labor supply ----
        labor_supply = len(households)

        # ---- Labor demand ----
        labor_demand = sum(f.desired_labor for f in firms)

        # ---- Wage adjustment ----
        excess_demand = labor_demand - labor_supply
        wage = self.base_wage * (1 + self.wage_adjustment * np.tanh(excess_demand / max(labor_supply, 1)))

        # ---- Employment matching ----
        employed = min(labor_supply, labor_demand)
        unemployment_rate = 1.0 - employed / labor_supply

        # Assign workers randomly
        np.random.shuffle(households)
        employed_households = households[:employed]

        for h in households:
            h.employed = False

        for h in employed_households:
            h.employed = True
            h.wealth += wage

        for f in firms:
            f.employees = int(
                f.desired_labor * employed / max(labor_demand, 1)
            )
            f.wage_bill = f.employees * wage

        return wage, unemployment_rate

    # --------------------------------------------------
    # Goods Market
    # --------------------------------------------------
    def clear_goods_market(self, households, firms):
        """
        Matches household consumption with firm production.
        Adjusts prices based on excess demand.
        """

        # ---- Total demand ----
        total_demand = sum(h.consumption for h in households)

        # ---- Total supply ----
        total_supply = sum(f.production for f in firms)

        # ---- Price adjustment ----
        excess_demand = total_demand - total_supply
        price_multiplier = 1 + self.price_adjustment * np.tanh(excess_demand / max(total_supply, 1))

        for f in firms:
            f.price *= price_multiplier

        # ---- Revenue allocation ----
        if total_supply > 0:
            for f in firms:
                market_share = f.production / total_supply
                f.revenue = market_share * min(total_demand, total_supply) * f.price
        else:
            for f in firms:
                f.revenue = 0.0

        return price_multiplier

    # --------------------------------------------------
    # Credit Market
    # --------------------------------------------------
    def clear_credit_market(self, firms, government):
        """
        Firms borrow from government / central bank.
        Credit rationing under high interest or capital controls.
        """

        interest_rate = government.current_interest_rate

        for f in firms:
            # Desired borrowing based on negative cash flow
            if f.capital < 0:
                desired_credit = abs(f.capital)

                # Capital controls & leverage constraint
                max_credit = self.max_leverage * max(f.capital + desired_credit, 1)
                granted_credit = min(desired_credit, max_credit)

                # Interest burden
                repayment = granted_credit * (1 + interest_rate)

                f.capital += granted_credit
                f.debt += repayment

        return interest_rate
