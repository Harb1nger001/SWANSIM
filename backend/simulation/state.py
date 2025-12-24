from dataclasses import dataclass, field
from typing import Dict, List, Any

@dataclass
class EconomicState:
    gdp: float = 0.0
    gdp_last: float = 0.0  # track previous step for growth calculation
    gdp_growth: float = 0.0 # Stored field
    inflation: float = 0.0
    unemployment: float = 0.0
    interest_rate: float = 0.05
    tax_rate: float = 0.2
    gini_coeff: float = 0.0
    wage_index: float = 1.0
    price_index: float = 1.0
    
    # Missing fields
    avg_unrest: float = 0.0
    top1_wealth_share: float = 0.0
    welfare_spending: float = 0.0
    capital_controls: float = 0.0
    regime: str = "stable" # for collapse check

    def update_growth(self):
        """Calculate growth and update history."""
        if self.gdp_last > 0:
            self.gdp_growth = (self.gdp - self.gdp_last) / self.gdp_last
        else:
            self.gdp_growth = 0.0
        
        self.gdp_last = self.gdp

    def apply_policy(self, action):
        """
        Apply government policy actions to the economic state.
        Action: [interest_rate, tax_rate, welfare_spending, capital_controls]
        """
        self.interest_rate = float(action[0])
        self.tax_rate = float(action[1])
        self.welfare_spending = float(action[2])
        self.capital_controls = float(action[3])


@dataclass
class GlobalState:
    step: int = 0
    economics: EconomicState = field(default_factory=EconomicState)
    households: Dict[str, Any] = field(default_factory=dict)
    firms: Dict[str, Any] = field(default_factory=dict)
    government: Dict[str, Any] = field(default_factory=dict)
    network: Any = None  # SocialGraph or other network reference
    shocks: List[Dict] = field(default_factory=list)

    # -----------------------------
    # Economic updates
    # -----------------------------
    def update_economics(self, new_metrics: Dict):
        """Update multiple macroeconomic metrics at once."""
        for k, v in new_metrics.items():
            if hasattr(self.economics, k):
                setattr(self.economics, k, v)

    def update_macros(
        self,
        gdp=None,
        inflation=None,
        unemployment=None,
        interest_rate=None,
        tax_rate=None,
        gini=None,
        wage_index=None,
        price_index=None,
    ):
        """Convenience method to update macro metrics selectively."""
        metrics = {
            "gdp": gdp,
            "inflation": inflation,
            "unemployment": unemployment,
            "interest_rate": interest_rate,
            "tax_rate": tax_rate,
            "gini_coeff": gini,
            "wage_index": wage_index,
            "price_index": price_index,
        }
        self.update_economics({k: v for k, v in metrics.items() if v is not None})

    # -----------------------------
    # Shock helpers
    # -----------------------------
    def add_shock(self, shock_type: str, severity: float, duration: int = None):
        """Add a shock event to the global state."""
        self.shocks.append({
            "type": shock_type,
            "severity": severity,
            "duration": duration
        })

    # -----------------------------
    # Serialization
    # -----------------------------
    def to_dict(self) -> Dict:
        return {
            "step": self.step,
            "economics": self.economics.__dict__,
            "num_households": len(self.households),
            "num_firms": len(self.firms),
            "shocks_active": len(self.shocks)
        }
