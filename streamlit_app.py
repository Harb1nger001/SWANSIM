import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx
import time
import sys
import os

# Add backend to path to allow imports
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from simulation.simulator import Simulator

# -----------------------------
# Config
# -----------------------------
st.set_page_config(page_title="Black Swan | Dystopian Sim", layout="wide", page_icon="🦢")

# Custom CSS for Dystopian Theme
st.markdown("""
<style>
    .stApp { background-color: #0a0a0c; color: #e0e0e0; }
    .stButton>button { background-color: #1a1a20; color: #ff3333; border: 1px solid #ff3333; width: 100%; }
    .stButton>button:hover { background-color: #ff3333; color: #0a0a0c; }
    .metric-card { background-color: #111113; padding: 20px; border-radius: 5px; border: 1px solid #333; text-align: center; }
    .metric-value { font-size: 2em; font-weight: bold; color: #0088ff; }
    .metric-label { font-size: 0.8em; text-transform: uppercase; color: #888; }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# State Management
# -----------------------------
if 'sim' not in st.session_state:
    st.session_state['sim'] = Simulator()

sim = st.session_state['sim']

# -----------------------------
# Helper Functions
# -----------------------------
def start_sim():
    try:
        sim.start()
        st.toast("Simulation Started", icon="🚀")
    except Exception as e:
        st.error(f"Error starting simulation: {e}")

def stop_sim():
    try:
        sim.stop()
        st.toast("Simulation Stopped", icon="🛑")
    except Exception as e:
        st.error(f"Error stopping simulation: {e}")

def inject_shock(shock_type, severity):
    try:
        sim.add_shock(shock_type, severity)
        st.toast(f"Shock Injected: {shock_type}", icon="⚡")
    except Exception as e:
        st.error(f"Error injecting shock: {e}")

def fetch_metrics():
    try:
        # Get metrics directly from simulator instance
        return sim.get_metrics()
    except Exception as e:
        # st.error(f"Error fetching metrics: {e}")
        pass
    return {
        "gdp_growth": 0.0,
        "inflation": 0.0,
        "unemployment": 0.0,
        "unrest": 0.0,
        "history": [],
        "network": None
    }

def plot_network(graph_dict):
    try:
        # Correctly parse graph including edge data
        G = nx.node_link_graph(graph_dict)
        pos = nx.spring_layout(G, seed=42)
        
        edge_x, edge_y = [], []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x += [x0, x1, None]
            edge_y += [y0, y1, None]
        
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y, line=dict(width=0.5, color='#888'), hoverinfo='none', mode='lines'
        )
        
        node_x, node_y, node_text = [], [], []
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            # Unrest might be missing if not populated, default to 0
            u_val = G.nodes[node].get('unrest', 0)
            node_text.append(f"Household {node}<br>Unrest: {u_val:.2f}")
        
        node_trace = go.Scatter(
            x=node_x, y=node_y, mode='markers', text=node_text, hoverinfo='text',
            marker=dict(color='#ff3333', size=10)
        )
        
        fig = go.Figure(data=[edge_trace, node_trace])
        fig.update_layout(
            paper_bgcolor="#111113", 
            plot_bgcolor="#111113", 
            showlegend=False,
            margin=dict(l=0, r=0, t=0, b=0),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
        )
        return fig
    except Exception as e:
        print(f"Graph Error: {e}")
        return None

# -----------------------------
# Layout
# -----------------------------
st.title("BLACK SWAN // SYSTEM MONITOR")

col1, col2 = st.columns([1, 4])

# --- Controls ---
with col1:
    st.subheader("CONTROLS")
    if st.button("START SIMULATION"):
        start_sim()
    if st.button("STOP SIMULATION"):
        stop_sim()
    
    st.divider()
    
    st.subheader("INJECT SHOCK")
    shock_type = st.selectbox("Shock Type", ["pandemic", "financial_crash", "political_coup", "supply_chain_collapse", "cyber_attack", "climate_catastrophe"])
    severity = st.slider("Severity", 0.0, 1.0, 0.5)
    if st.button("EXECUTE SHOCK"):
        inject_shock(shock_type, severity)
    
    st.divider()
    if sim.running:
        st.success("System Status: RUNNING")
    else:
        st.info("System Status: IDLE")

# --- Metrics & Charts ---
with col2:
    # Metric placeholders
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    gdp_card = m_col1.empty()
    inflation_card = m_col2.empty()
    unemployment_card = m_col3.empty()
    unrest_card = m_col4.empty()
    
    # Charts tabs
    tab1, tab2 = st.tabs(["MACROECONOMICS", "SOCIAL NETWORK"])
    with tab1:
        macro_chart = st.empty()
    with tab2:
        network_chart = st.empty()
    
    # --- Live update loop ---
    if sim.running:
        while True:
            metrics = fetch_metrics()
            
            # Update metric cards
            gdp_card.markdown(f'<div class="metric-card"><div class="metric-label">GDP Growth</div><div class="metric-value">{metrics["gdp_growth"]:.2%}</div></div>', unsafe_allow_html=True)
            inflation_card.markdown(f'<div class="metric-card"><div class="metric-label">Inflation</div><div class="metric-value">{metrics["inflation"]:.2%}</div></div>', unsafe_allow_html=True)
            unemployment_card.markdown(f'<div class="metric-card"><div class="metric-label">Unemployment</div><div class="metric-value">{metrics["unemployment"]:.2%}</div></div>', unsafe_allow_html=True)
            unrest_card.markdown(f'<div class="metric-card"><div class="metric-label">Social Unrest</div><div class="metric-value">{metrics["unrest"]:.2f}</div></div>', unsafe_allow_html=True)
            
            # Update macro chart
            history = pd.DataFrame(metrics.get("history", []))
            if not history.empty:
                fig = px.line(history, x="step", y=["gdp", "inflation", "unemployment", "unrest"], 
                              title="Economic Trajectory", template="plotly_dark")
                fig.update_layout(paper_bgcolor="#111113", plot_bgcolor="#111113")
                macro_chart.plotly_chart(fig, use_container_width=True)
            
            # Update social network (throttle this, it's heavy)
            if metrics.get("step", 0) % 5 == 0:
                network_dict = metrics.get("network", None)
                if network_dict and len(network_dict.get("nodes", [])) > 0:
                    fig_net = plot_network(network_dict)
                    if fig_net:
                        network_chart.plotly_chart(fig_net, use_container_width=True)
            
            time.sleep(1)
            # Rerun script check? No, local loop. 
            # Streamlit warns about loops. but we are in a 'while True' inside 'if sim.running'. 
            # Ideally we rely on st.rerun() but for smooth animation a loop is often used.
            # We break if simulation stops.
            if not sim.running:
                st.rerun() 
                break
    else:
        # Static view of last known state
        metrics = fetch_metrics()
        gdp_card.markdown(f'<div class="metric-card"><div class="metric-label">GDP Growth</div><div class="metric-value">{metrics["gdp_growth"]:.2%}</div></div>', unsafe_allow_html=True)
        inflation_card.markdown(f'<div class="metric-card"><div class="metric-label">Inflation</div><div class="metric-value">{metrics["inflation"]:.2%}</div></div>', unsafe_allow_html=True)
        unemployment_card.markdown(f'<div class="metric-card"><div class="metric-label">Unemployment</div><div class="metric-value">{metrics["unemployment"]:.2%}</div></div>', unsafe_allow_html=True)
        unrest_card.markdown(f'<div class="metric-card"><div class="metric-label">Social Unrest</div><div class="metric-value">{metrics["unrest"]:.2f}</div></div>', unsafe_allow_html=True)

