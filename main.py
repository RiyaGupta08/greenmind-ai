import argparse
import sys
from pathlib import Path
from rich.console import Console

from agents.monitoring_agent        import MonitoringAgent
from agents.anomaly_detection_agent import AnomalyDetectionAgent
from agents.decision_agent          import DecisionAgent
from agents.action_agent            import ActionAgent
from agents.audit_agent             import AuditAgent

from utils.helpers   import print_banner, print_section, print_savings_table, print_audit_summary
from utils.predictor import predict_future_waste, format_predictions, format_7day_warning
import config

console = Console()


def parse_args():
    p = argparse.ArgumentParser(description="GreenMind AI")
    p.add_argument("--csv",     type=Path, default=config.CSV_PATH)
    p.add_argument("--approve", action="store_true",
                   help="Require human approval before each action")
    return p.parse_args()


def run_pipeline(csv_path: Path, require_approval: bool = False):
    config.HUMAN_APPROVAL_REQUIRED = require_approval

    print_banner()

    # Step 1 — Monitoring
    print_section("Step 1 - Monitoring Agent")
    records = MonitoringAgent(csv_path=csv_path).run()
    if not records:
        console.print("[red]No records loaded. Exiting.[/red]")
        sys.exit(1)

    # Step 2 — Anomaly Detection
    print_section("Step 2 - Anomaly Detection Agent")
    anomaly_reports = AnomalyDetectionAgent().run(records)

    # 7-day proactive warning
    warning = format_7day_warning(anomaly_reports)
    if warning:
        console.print()
        console.print(warning)
        console.print()

    # 30-day forecast
    print_section("Forecast - Projected Waste If No Action Taken")
    predictions = predict_future_waste(anomaly_reports)
    console.print(format_predictions(predictions))
    console.print()

    # Step 3 — Decisions
    print_section("Step 3 - Hybrid AI Decision Engine")
    decisions = DecisionAgent().run(anomaly_reports)

    # Step 4 — Actions
    print_section("Step 4 - Action Agent")
    action_results = ActionAgent().run(decisions, records)

    # Step 5 — Audit
    print_section("Step 5 - Audit Agent")
    audit_entries = AuditAgent().run(anomaly_reports, decisions, action_results)

    # Final results
    print_section("Results - Cost Optimization Report")
    print_savings_table(action_results)
    console.print()
    print_audit_summary(audit_entries)

    return audit_entries


if __name__ == "__main__":
    args = parse_args()
    run_pipeline(csv_path=args.csv, require_approval=args.approve)