"""
agents/audit_agent.py – Agent 5: Audit / Logging Agent

Job: Collect outputs from all other agents and save them to disk.
Creates two files:
  - logs/audit_trail.json    (machine-readable log of every decision)
  - logs/summary_report.txt  (human-readable summary)
"""

import json
import dataclasses
from datetime import datetime
from typing import List, Dict
from rich.console import Console

from utils.models import AnomalyReport, Decision, ActionResult, AuditEntry
import config

console = Console()


def _to_dict(obj) -> dict:
    """Convert a dataclass object to a plain dictionary for JSON saving."""
    if obj is None:
        return {}
    if dataclasses.is_dataclass(obj):
        return {k: _to_dict(v) for k, v in dataclasses.asdict(obj).items()}
    return obj


class AuditAgent:

    def run(
        self,
        anomalies: List[AnomalyReport],
        decisions: List[Decision],
        actions:   List[ActionResult],
    ) -> List[AuditEntry]:
        """Combine all agent outputs into audit entries and save to disk."""
        console.print("[bold cyan]📋 AuditAgent:[/bold cyan] Recording audit trail…")

        # Build lookup dictionaries keyed by server_id
        anomaly_map  = {a.server_id: a for a in anomalies}
        decision_map = {d.server_id: d for d in decisions}
        action_map   = {a.server_id: a for a in actions}

        # Get all server IDs across all agents
        all_ids = sorted(set(anomaly_map) | set(decision_map) | set(action_map))

        entries = []
        for sid in all_ids:
            entry = AuditEntry(
                server_id     = sid,
                anomaly       = anomaly_map.get(sid),
                decision      = decision_map.get(sid),
                action_result = action_map.get(sid),
            )
            entries.append(entry)

        self._write_json(entries)
        self._write_summary(entries)

        actioned = sum(1 for e in entries if e.action_result and e.action_result.action_taken != "keep")
        console.print(
            f"  ✅ Audit log saved  → [dim]{config.AUDIT_LOG_PATH}[/dim]\n"
            f"  📄 Summary saved    → [dim]{config.SUMMARY_PATH}[/dim]\n"
            f"  {actioned} servers actioned.\n"
        )
        return entries

    def _write_json(self, entries: List[AuditEntry]) -> None:
        """Save each entry as one line of JSON (NDJSON format)."""
        config.AUDIT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with config.AUDIT_LOG_PATH.open("a", encoding="utf-8") as fh:
            for entry in entries:
                fh.write(json.dumps(_to_dict(entry)) + "\n")

    def _write_summary(self, entries: List[AuditEntry]) -> None:
        """Save a plain text summary report."""
        total_monthly = sum(
            e.action_result.monthly_saving
            for e in entries if e.action_result
        )

        lines = [
            "=" * 60,
            "  GreenMind AI – Cost Optimization Summary",
            f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 60, "",
        ]

        for e in entries:
            ar     = e.action_result
            action = ar.action_taken if ar else "N/A"
            saving = f"${ar.monthly_saving:,.2f}/mo" if ar else "-"
            lines.append(f"  {e.server_id:<12} action={action:<12} saving={saving}")

        lines += [
            "", "-" * 60,
            f"  TOTAL PROJECTED MONTHLY SAVINGS: ${total_monthly:,.2f}",
            "=" * 60,
        ]

        config.SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
        config.SUMMARY_PATH.write_text("\n".join(lines), encoding="utf-8")