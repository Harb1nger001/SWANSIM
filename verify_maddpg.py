import sys
import os
import time

# Add root directory to python path
sys.path.append(os.path.abspath("d:/Black Swan/backend"))

try:
    print("Importing Simulator...")
    from simulation.simulator import Simulator
    
    print("Initializing Simulator...")
    sim = Simulator()
    
    print("Config Loaded:", sim.config['num_households'], "households (from yaml/scale)")
    print("Agent Initialized:", sim.agent)
    
    print("Starting Simulation...")
    sim.start()
    
    time.sleep(5)
    
    print("Metrics History Length:", len(sim.metrics_history))
    if len(sim.metrics_history) > 0:
        print("Latest Metric:", sim.metrics_history[-1])
        
    print("Stopping Simulation...")
    sim.stop()
    
    print("SUCCESS: Simulation ran with MADDPG agent.")

except Exception as e:
    print(f"FAILED: {e}")
    import traceback
    traceback.print_exc()

sys.exit(0)
