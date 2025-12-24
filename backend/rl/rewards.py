import numpy as np


class RewardFunctions:
    """
    Centralized reward definitions for Black Swan.
    All rewards are bounded and shaped for MARL stability.
    """

    # -----------------------------
    # Household Reward
    # -----------------------------
    @staticmethod
    def household_reward(
        consumption: float,
        inflation: float,
        unemployment_risk: float,
        unrest_exposure: float,
        alpha: float = 1.0,
        beta: float = 1.2,
        gamma: float = 1.5
    ) -> float:
        """
        Household objective:
        Maximize survival utility under inflation, job insecurity,
        and social instability.

        R_h = log(consumption)
              - α * inflation
              - β * unemployment_risk
              - γ * unrest_exposure²
        """

        # ---- Safety clipping ----
        consumption = max(consumption, 1e-6)
        inflation = np.clip(inflation, 0.0, 1.0)
        unemployment_risk = np.clip(unemployment_risk, 0.0, 1.0)
        unrest_exposure = np.clip(unrest_exposure, 0.0, 1.0)

        # ---- Utility ----
        utility = np.log(consumption)

        # ---- Penalties ----
        penalty = (
            alpha * inflation +
            beta * unemployment_risk +
            gamma * unrest_exposure ** 2   # unrest escalates nonlinearly
        )

        reward = utility - penalty

        return float(np.clip(reward, -5.0, 5.0))

    # -----------------------------
    # Government Reward
    # -----------------------------
    @staticmethod
    def government_reward(
        gdp_growth: float,
        inflation: float,
        unemployment: float,
        unrest: float,
        inequality: float,
        alpha: float = 0.8,
        beta: float = 1.2,
        gamma: float = 2.0,
        delta: float = 1.0
    ) -> float:
        """
        Government objective:
        Balance growth with systemic stability.

        R_g = + GDP_growth
              - α * inflation
              - β * unemployment
              - γ * unrest²
              - δ * inequality
        """

        # ---- Clip inputs ----
        gdp_growth = np.clip(gdp_growth, -0.25, 0.25)
        inflation = np.clip(inflation, 0.0, 1.0)
        unemployment = np.clip(unemployment, 0.0, 1.0)
        unrest = np.clip(unrest, 0.0, 1.0)
        inequality = np.clip(inequality, 0.0, 1.0)

        reward = (
            gdp_growth
            - alpha * inflation
            - beta * unemployment
            - gamma * unrest ** 2    # revolutions are nonlinear
            - delta * inequality
        )

        # ---- Collapse penalty ----
        if unrest > 0.85 and inequality > 0.6:
            reward -= 2.0

        return float(np.clip(reward, -5.0, 5.0))

    # -----------------------------
    # Utility Function (Explicit)
    # -----------------------------
    @staticmethod
    def utility_consumption(consumption: float) -> float:
        """
        Log utility with numerical safety.
        """
        return float(np.log(max(consumption, 1e-6)))
