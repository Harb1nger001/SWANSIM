import sys
import os
import networkx as nx

# Add root directory to python path
sys.path.append(os.path.abspath("d:/Black Swan/backend"))

try:
    print("Importing Simulator...")
    from simulation.simulator import Simulator
    
    print("Initializing Simulator...")
    sim = Simulator()
    
    print("Getting Network Data...")
    net_data = sim._get_network_data()
    print(f"Network Data Keys: {net_data.keys()}")
    
    print("Reconstructing Graph...")
    G = nx.node_link_graph(net_data)
    print(f"Reconstructed Graph: {len(G.nodes)} nodes, {len(G.edges)} edges")
    
    if len(G.nodes) > 0:
        print("SUCCESS: Social Graph logic is valid.")
    else:
        print("FAILURE: Graph is empty.")

except Exception as e:
    print(f"FAILED: {e}")
    import traceback
    traceback.print_exc()

sys.exit(0)
