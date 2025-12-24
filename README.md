# 🦢 SWANSIM

![Python](https://img.shields.io/badge/Python-3.11+-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-v0.105-green) ![Streamlit](https://img.shields.io/badge/Streamlit-v1.25-orange) ![License](https://img.shields.io/badge/License-MIT-lightgrey) ![Status](https://img.shields.io/badge/Status-Alpha-red)

> **Black Swan Civilization Simulator** – A dystopian multi-agent RL simulator for modeling socioeconomic collapse, systemic risks, and macroeconomic instability.

---

## 🔥 Features

### Agents
- **Households:** 4 social classes, neural policy (RL)  
- **Firms:** Startups, SMEs, MNCs (capitalist behavior)  
- **Government:** Macro-policy RL agent  

### Social Network
- Scale-free network for households  
- Unrest diffusion and social influence  

### Shocks
- **Exogenous:** pandemic, financial crash, supply chain collapse, tech failure  
- **Endogenous:** revolutions, market crashes, social unrest spikes  

### Metrics
- GDP Growth  
- Inflation  
- Unemployment  
- Gini Coefficient  
- Average Firm Profit  
- Social Unrest Index  

### RL Integration
- MADDPG for adaptive household & government agents  

### Dashboard
- Streamlit + Plotly interactive real-time visualization  

---

## ⚡ Installation

```bash
git clone https://github.com/yourusername/SWANSIM.git
cd SWANSIM
```
```bash
# Create virtual environment
# Linux/Mac
python -m venv venv && source venv/bin/activate
# Windows
python -m venv venv && venv\Scripts\activate
```
```bash
# Install dependencies
pip install -r requirements.txt
```

🚀 Usage

Frontend
```bash
streamlit run streamlit_app.py
```
Open http://localhost:8501 to view the dashboard.

📁 Folder Structure
```bash
SWANSIM/
├─ backend/
│  ├─ data/
│  │  ├─ imf_client.py
│  │  ├─ rbi_client.py
│  │  └─ data_loader.py
│  ├─ rl/
│  │  ├─ maddpg.py
│  │  ├─ buffers.py
│  │  └─ rewards.py
│  └─ simulation/
│     ├─ env.py
│     ├─ simulator.py
│     ├─ state.py
│     ├─ agents/
│     │  ├─ households.py
│     │  ├─ firms.py
│     │  └─ government.py
│     ├─ economics/
│     │  ├─ markets.py
│     │  └─ inequality.py
│     ├─ networks/
│     │  └─ social_graph.py
│     └─ shocks/
│        ├─ endogenous.py
│        ├─ exogenous.py
│        └─ shock_manager.py
├─ streamlit_app.py
├─ requirements.txt
├─ README.md
├─ verify_backend.py
├─ verify_data.py
├─ verify_graph.py
└─ verify_maddpg.py
```
## 📊 Dashboard Controls

### Start/Stop Simulation

- Inject Shocks: pandemic, financial crash, political coup, supply chain collapse
- Live Metrics: GDP, Inflation, Unemployment, Social Unrest
- Visualization Tabs: Macro-economic trends, Social network

## 📚 References

- Taleb, N. N. The Black Swan: The Impact of the Highly Improbable
- Agent-Based Modeling for Macroeconomic Systems
- Network Theory in Social Contagion

💖 Made with Love & Coffee ☕
