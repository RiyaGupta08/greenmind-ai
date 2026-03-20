"""
agents/anomaly_detection_agent.py – Agent 2: Anomaly Detection Agent

Job: Look at each server and decide if it's wasting money.
Rules:
  - CPU < 10% for 7+ days = IDLE (big waste)
  - CPU < 25% but costs > $1.50/hr = UNDERUTILISED (medium waste)
  - Everything else = healthy
"""

from typing import List
from rich.console import Console

from utils.models import ServerRecord, AnomalyReport
import config

console = Console()


class AnomalyDetectionAgent:

    def run(self, records: List[ServerRecord]) -> List[AnomalyReport]:
        """Check every server and return one AnomalyReport per server."""
        console.print("[bold cyan]🧠 AnomalyDetectionAgent:[/bold cyan] Scanning for inefficiencies…")

        reports = []
        idle_count = underutil_count = healthy_count = 0

        for rec in records:
            report = self._analyse(rec)
            reports.append(report)

            # Pick the right emoji for display
            if report.anomaly_type == "idle":
                idle_count += 1
                icon = "🔴"
            elif report.anomaly_type == "underutilised":
                underutil_count += 1
                icon = "🟡"
            else:
                healthy_count += 1
                icon = "🟢"

            console.print(
                f"  {icon} [cyan]{rec.server_id}[/cyan]  "
                f"CPU={rec.cpu_usage:5.1f}%  "
                f"${rec.cost_per_hour:.2f}/hr  "
                f"→ [yellow]{report.anomaly_type}[/yellow]"
            )

        console.print(
            f"\n  Summary: "
            f"[red]{idle_count} idle[/red]  |  "
            f"[yellow]{underutil_count} underutilised[/yellow]  |  "
            f"[green]{healthy_count} healthy[/green]\n"
        )
        return reports

    def _analyse(self, rec: ServerRecord) -> AnomalyReport:
        """Apply detection rules to one server."""

        # Rule 1: Idle server (very low CPU for a long time)
        if (rec.cpu_usage < config.IDLE_CPU_THRESHOLD
                and rec.hours_running >= config.MIN_HOURS_FOR_IDLE):
            return AnomalyReport(
                server_id     = rec.server_id,
                anomaly_type  = "idle",
                severity      = "high",
                reason        = (
                    f"CPU at {rec.cpu_usage:.1f}% for {rec.hours_running:.0f} hrs. "
                    f"Spending ${rec.cost_per_hour:.2f}/hr with no workload."
                ),
                cpu_usage     = rec.cpu_usage,
                cost_per_hour = rec.cost_per_hour,
                hours_running = rec.hours_running,
            )

        # Rule 2: Underutilised but expensive
        if (rec.cpu_usage < config.MEDIUM_CPU_THRESHOLD
                and rec.cost_per_hour >= config.HIGH_COST_THRESHOLD):
            return AnomalyReport(
                server_id     = rec.server_id,
                anomaly_type  = "underutilised",
                severity      = "medium",
                reason        = (
                    f"CPU at {rec.cpu_usage:.1f}% on a "
                    f"${rec.cost_per_hour:.2f}/hr instance. "
                    "Could be moved to a cheaper tier."
                ),
                cpu_usage     = rec.cpu_usage,
                cost_per_hour = rec.cost_per_hour,
                hours_running = rec.hours_running,
            )

        # Rule 3: Healthy — no problem
        return AnomalyReport(
            server_id     = rec.server_id,
            anomaly_type  = "none",
            severity      = "none",
            reason        = f"CPU at {rec.cpu_usage:.1f}%, cost ${rec.cost_per_hour:.2f}/hr – normal.",
            cpu_usage     = rec.cpu_usage,
            cost_per_hour = rec.cost_per_hour,
            hours_running = rec.hours_running,
        )