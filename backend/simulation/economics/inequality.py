import numpy as np


class InequalityMetrics:
    @staticmethod
    def calculate_gini(incomes):
        """
        Calculates Gini coefficient.
        Gini = 0 → perfect equality
        Gini = 1 → maximal inequality
        """

        incomes = np.array(incomes, dtype=np.float64)

        if len(incomes) == 0:
            return 0.0

        if np.all(incomes == 0):
            return 0.0

        incomes = np.sort(incomes)
        n = incomes.shape[0]
        index = np.arange(1, n + 1)

        gini = (
            (2 * index - n - 1) * incomes
        ).sum() / (n * incomes.sum())

        return float(np.clip(gini, 0.0, 1.0))

    @staticmethod
    def calculate_wealth_share(wealths, top_percentile=0.01):
        """
        Calculates the share of total wealth held by the top X percentile.
        Example: top_percentile=0.01 → top 1%
        """

        wealths = np.array(wealths, dtype=np.float64)

        if len(wealths) == 0:
            return 0.0

        total_wealth = wealths.sum()
        if total_wealth <= 0:
            return 0.0

        # Number of agents in top percentile
        k = max(1, int(np.ceil(len(wealths) * top_percentile)))

        # Sort descending
        sorted_wealths = np.sort(wealths)[::-1]

        top_wealth = sorted_wealths[:k].sum()

        share = top_wealth / total_wealth

        return float(np.clip(share, 0.0, 1.0))
