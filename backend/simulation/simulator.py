import threading
import time
import numpy as np
from simulation.env import BlackSwanEnv
from rl.maddpg import MADDPG
from data.data_loader import DataLoader
import yaml
import os

class Simulator:
    # ... (init code remains similar but with agent init)
    def __init__(self):
        # Load config
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "parameters.yaml")
        with open(config_path, "r") as f:
            yaml_config = yaml.safe_load(f)

        # Load Real Data
        loader = DataLoader()
        real_data = loader.get_initial_state()
        print(f"Seeding Simulation with Real Data: {real_data}")

        # Override YAML/Defaults with Real Data
        if "economics" not in yaml_config:
            yaml_config["economics"] = {}
        
        yaml_config["economics"]["initial_gdp"] = real_data["initial_gdp"]
        yaml_config["economics"]["inflation_target"] = real_data["inflation_target"]
        yaml_config["agents"]["government"]["initial_interest_rate"] = real_data["base_interest_rate"]
        # Note: Unemployment is usually an outcome, but we can perhaps influence initial firm count or labor demand?
        # For now, let's just stick to macro seeding.

        # Flatten/Map config to env expectations
        self.config = {
            "num_households": int(yaml_config["agents"]["households"]["count"] / 1000), # Scale down for performance
            "num_firms": yaml_config["agents"]["firms"]["count"],
            "max_steps": yaml_config["simulation"]["steps"],
            "shock_probs": {
                "pandemic": 0.001,
            },
            "raw_config": yaml_config 
        }
        self.env = BlackSwanEnv(self.config)
        self.obs, _ = self.env.reset()
        
        # Initialize MADDPG Agent
        # Obs dim: [inflation, unemployment, unrest, inequality, gdp] = 5
        # Act dim: [interest, tax, welfare, controls] = 4
        self.agent = MADDPG(5, 4, yaml_config)
        
        self.running = False
        self.thread = None
        self.metrics_history = []
        self.latest_metrics = {}

    # ... (start/stop/metrics remain same)

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run_loop, daemon=True)
            self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)

    def add_shock(self, shock_type, severity):
        self.env.shocks.add_shock(shock_type, severity)

    def get_metrics(self):
        # Convert internal state to serializable dict
        return {
            "gdp_growth": float(self.env.state.economics.gdp_growth) if hasattr(self.env.state.economics, 'gdp_growth') else 0.0,
            "inflation": float(self.env.state.economics.inflation),
            "unemployment": float(self.env.state.economics.unemployment),
            "unrest": float(self.env.state.economics.avg_unrest),
            "history": self.metrics_history[-50:], # Send last 50 points
            "network": self._get_network_data()
        }

    def _run_loop(self):
        step_count = 0
        while self.running:
            # 1. Construct Agent Observation
            # Gov agent act expects: [inflation, unemployment, unrest, inequality, gdp_level]
            # obs from env: [gdp, inflation, unemployment, gini, avg_unrest, top1, rate, tax, welfare, controls]
            
            # Note: We need to normalize GDP for neural net 
            norm_gdp = np.tanh(self.obs[0] / 100000.0) 
            
            gov_state = np.array([
                self.obs[1], # inflation
                self.obs[2], # unemployment
                self.obs[4], # unrest
                self.obs[3], # inequality (gini)
                norm_gdp     # gdp (normalized)
            ])
            
            # 2. Select Action (with noise for exploration)
            action = self.agent.select_action(gov_state, noise=0.1)
            
            # 3. Step Environment
            next_obs, reward, terminated, truncated, info = self.env.step(action)
            
            # 4. Store Experience
            next_norm_gdp = np.tanh(next_obs[0] / 100000.0)
            next_gov_state = np.array([
                next_obs[1], next_obs[2], next_obs[4], next_obs[3], next_norm_gdp
            ])
            
            self.agent.memory.push(gov_state, action, reward, next_gov_state, terminated)
            
            # 5. Train Agent
            if step_count % 10 == 0:
                self.agent.update()
            
            # Update loop variables
            self.obs = next_obs
            step_count += 1
            
            # Record metrics
            step_metrics = {
                "step": self.env.timestep,
                "gdp": float(next_obs[0]),
                "inflation": float(next_obs[1]),
                "unemployment": float(next_obs[2]),
                "unrest": float(next_obs[4])
            }
            self.metrics_history.append(step_metrics)
            
            if terminated or truncated:
                self.obs, _ = self.env.reset()
                
            time.sleep(0.5) # Speed up slightly

    def _get_network_data(self):
        # Format social graph for frontend
        # Use node_link_data for standard compatibility
        G = self.env.social_graph.graph
        # Convert to standard format
        # Filter data to reduce size if needed, but for now send full
        import networkx as nx 
        data = nx.node_link_data(G)
        # Ensure 'links' key is used (default in new nx versions)
        return data
