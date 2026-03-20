# 🌿 GreenMind AI
### Autonomous Cloud Cost Optimization System

A multi-agent AI system that monitors enterprise cloud/resource usage,
detects cost inefficiencies, and takes automated corrective actions
with measurable financial impact.

## 💰 Results
- 11 idle servers detected and actioned
- Total Monthly Savings: $14,782 (approx Rs. 12,26,948)
- 7-day waste if no action: $3,402 (approx Rs. 2,82,366)

## 🤖 How It Works
5 AI agents work together in a pipeline:
1. Monitoring Agent - reads server usage data from CSV
2. Anomaly Detection Agent - finds idle and underutilised servers
3. Hybrid AI Decision Engine - decides actions with full reasoning
4. Action Agent - executes actions and calculates savings
5. Audit Agent - logs every decision with timestamps

## 🛠️ Tech Stack
- Python 3.10+
- Multi-Agent Architecture
- Hybrid AI Decision Engine (LLM + Rules)
- Rich (beautiful terminal UI)
- Pandas (data processing)
- Streamlit (web dashboard)
- Plotly (charts)

## 🚀 How to Run

Install dependencies:
pip install -r requirements.txt

Run in console:
python main.py

Run with human approval mode:
python main.py --approve

Run web dashboard:
streamlit run ui/streamlit_app.py

## 📊 Sample Output
- srv-007 → SHUTDOWN | CPU 1.5% | saving $2,774/month
- srv-014 → SHUTDOWN | CPU 0.8% | saving $2,774/month
- srv-003 → SHUTDOWN | CPU 2.1% | saving $1,752/month
- srv-011 → SHUTDOWN | CPU 3.3% | saving $1,752/month

## 🏗️ Project Structure
greenmind_ai/
├── agents/
│   ├── monitoring_agent.py
│   ├── anomaly_detection_agent.py
│   ├── decision_agent.py
│   ├── action_agent.py
│   └── audit_agent.py
├── utils/
│   ├── models.py
│   ├── helpers.py
│   └── predictor.py
├── data/
│   └── servers.csv
├── ui/
│   └── streamlit_app.py
├── main.py
├── config.py
└── requirements.txt