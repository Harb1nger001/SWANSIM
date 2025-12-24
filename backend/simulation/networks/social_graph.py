import networkx as nx
import numpy as np


class SocialGraph:
    """
    Social network for households.
    Models unrest diffusion and social amplification.
    """

    def __init__(self, num_agents, config):
        self.config = config

        # Scale-free network (opinion leaders exist)
        self.graph = nx.barabasi_albert_graph(
            num_agents,
            config.get("avg_degree", 3)
        )

        # Diffusion parameters
        self.influence_strength = config.get("influence_strength", 0.3)
        self.decay = config.get("unrest_decay", 0.05)
        self.noise = config.get("social_noise", 0.02)

    # --------------------------------------------------
    # Unrest propagation
    # --------------------------------------------------
    def spread_influence(self, household_states):
        """
        household_states: dict
            {agent_id: {"unrest": float}}

        Returns:
            updated_unrest: dict {agent_id: unrest}
        """

        new_unrest = {}

        for agent_id in self.graph.nodes:
            neighbors = list(self.graph.neighbors(agent_id))

            own_unrest = household_states[agent_id]["unrest"]

            if not neighbors:
                new_unrest[agent_id] = self._clip(own_unrest)
                continue

            # ---- Social influence ----
            neighbor_unrest = np.mean(
                [household_states[n]["unrest"] for n in neighbors]
            )

            # ---- Diffusion equation ----
            propagated = (
                own_unrest
                + self.influence_strength * (neighbor_unrest - own_unrest)
                - self.decay * own_unrest
                + np.random.normal(0, self.noise)
            )

            new_unrest[agent_id] = self._clip(propagated)

        return new_unrest

    # --------------------------------------------------
    # Neighborhood query
    # --------------------------------------------------
    def get_neighbors(self, agent_id):
        return list(self.graph.neighbors(agent_id))

    # --------------------------------------------------
    # Helpers
    # --------------------------------------------------
    @staticmethod
    def _clip(x):
        return float(np.clip(x, 0.0, 1.0))
