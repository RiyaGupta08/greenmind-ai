"""
config.py – Central configuration for GreenMind AI
All thresholds, paths, and settings live here so you only change one file.
"""

import os
from pathlib import Path

# ── Project Paths ─────────────────────────────────────────────
BASE_DIR   = Path(__file__).parent
DATA_DIR   = BASE_DIR / "data"
LOGS_DIR   = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

CSV_PATH       = DATA_DIR / "servers.csv"
AUDIT_LOG_PATH = LOGS_DIR / "audit_trail.json"
SUMMARY_PATH   = LOGS_DIR / "summary_report.txt"

# ── LLM Settings ──────────────────────────────────────────────
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
LLM_MODEL      = "gpt-4o-mini"

# ── Detection Thresholds ──────────────────────────────────────
IDLE_CPU_THRESHOLD      = 10.0   # % cpu below this = idle
HIGH_COST_THRESHOLD     = 1.50   # $/hr above this = expensive
MIN_HOURS_FOR_IDLE      = 168    # must run 1 week to be flagged
MEDIUM_CPU_THRESHOLD    = 25.0   # below this + high cost = underutilised

# ── Action Savings Map ────────────────────────────────────────
SAVINGS_RATE = {
    "shutdown":   1.00,   # 100% cost eliminated
    "scale_down": 0.50,   # 50% cost saved
    "keep":       0.00,   # no saving
}

# ── Human-Approval Mode ───────────────────────────────────────
HUMAN_APPROVAL_REQUIRED = False

# ── Future Waste Prediction ───────────────────────────────────
PREDICTION_DAYS = 30