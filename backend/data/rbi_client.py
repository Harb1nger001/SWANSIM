import pandas as pd
import numpy as np

class RBIClient:
    """
    Client for Reserve Bank of India (RBI) Data.
    Since RBI does not have a public JSON API for historical time-series in the same format,
    this client provides:
    1. Historical priors (hardcoded/local CSV based on 2010-2024 data).
    2. Simulated forward-looking monetary policy response function.
    """
    
    def __init__(self):
        # Historical Indian Policy Rates (Repo Rate) approx
        self.historical_repo_rates = {
            2010: 5.25, 2011: 8.50, 2012: 8.00, 2013: 7.75, 2014: 8.00,
            2015: 6.75, 2016: 6.25, 2017: 6.00, 2018: 6.50, 2019: 5.15,
            2020: 4.00, 2021: 4.00, 2022: 6.25, 2023: 6.50, 2024: 6.50
        }
    
    def get_historical_rates(self):
        """Returns historical repo rates."""
        return self.historical_repo_rates

    def get_current_policy_rate(self):
        """Returns the current simulated policy rate (Repo Rate)."""
        # Default starting point (2024)
        return 6.50

    def simulate_mpc_decision(self, inflation, gdp_gap):
        """
        Simulates the Monetary Policy Committee (MPC) decision using a Taylor Rule for India.
        
        Target Inflation: 4% (+/- 2%)
        Neutral Rate: ~1-1.5% real rate -> ~5.5% nominal
        """
        target_inflation = 4.0
        neutral_rate = 5.5
        
        # Taylor rule coefficients for emerging market
        alpha = 1.5 # Reaction to inflation
        beta = 0.5  # Reaction to output gap
        
        inflation_gap = inflation - target_inflation
        
        # Nominal Rate = Neutral + alpha * (Inf - Target) + beta * OutputGap
        policy_rate = neutral_rate + (alpha * inflation_gap) + (beta * gdp_gap)
        
        return max(3.0, min(10.0, policy_rate)) # Bounds for realism

if __name__ == "__main__":
    client = RBIClient()
    print("Historical Rates:", client.get_historical_rates())
    print("Simulated Rate (Inf=6%, Gap=-1%):", client.simulate_mpc_decision(6.0, -1.0))
