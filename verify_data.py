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
    
    # Check if config was updated
    raw_config = sim.config.get("raw_config", {})
    init_gdp = raw_config.get("economics", {}).get("initial_gdp", 0)
    print(f"Configured Initial GDP: {init_gdp}")
    
    print("Starting Simulation...")
    sim.start()
    time.sleep(3)
    
    metrics = sim.get_metrics()
    print("Current Metrics:", metrics)
    
    sim.stop()
    
    # Sanity check
    if init_gdp > 1e12:
        print("SUCCESS: Simulation seeded with Real World GDP scale.")
    else:
        print("WARNING: GDP seems low, data loader might have failed.")

except Exception as e:
    print(f"FAILED: {e}")
    import traceback
    traceback.print_exc()

sys.exit(0)
