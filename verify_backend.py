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
    
    print("Starting Simulation...")
    sim.start()
    
    time.sleep(3)
    
    print("Getting Metrics...")
    metrics = sim.get_metrics()
    print("Metrics:", list(metrics.keys()))
    
    print("Stopping Simulation...")
    sim.stop()
    
    print("SUCCESS: Simulation ran for 3 seconds.")

except Exception as e:
    print(f"FAILED: {e}")
    import traceback
    traceback.print_exc()

sys.exit(0)
