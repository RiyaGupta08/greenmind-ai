"""
agents/monitoring_agent.py – Agent 1: Monitoring Agent

Job: Read the CSV file and return a list of ServerRecord objects.
Think of this agent as the "data collector" — it just reads and cleans data.
"""

import pandas as pd
from pathlib import Path
from typing import List
from rich.console import Console

from utils.models import ServerRecord
import config

console = Console()


class MonitoringAgent:

    def __init__(self, csv_path: Path = config.CSV_PATH):
        self.csv_path = csv_path

    def run(self) -> List[ServerRecord]:
        """Main method — called by main.py to start this agent."""
        console.print(f"[bold cyan]🔍 MonitoringAgent:[/bold cyan] Reading data from [dim]{self.csv_path}[/dim]")
        raw_df  = self._load_csv()
        records = self._parse(raw_df)
        console.print(f"  ✅ Loaded [bold]{len(records)}[/bold] server records.\n")
        return records

    def _load_csv(self) -> pd.DataFrame:
        """Load the CSV file. Give a clear error if file is missing."""
        if not self.csv_path.exists():
            raise FileNotFoundError(f"CSV not found at {self.csv_path}")
        return pd.read_csv(self.csv_path)

    def _parse(self, df: pd.DataFrame) -> List[ServerRecord]:
        """Convert each CSV row into a ServerRecord object."""
        required = {"server_id", "cpu_usage", "hours_running", "cost_per_hour"}
        missing  = required - set(df.columns)
        if missing:
            raise ValueError(f"CSV is missing columns: {missing}")

        records = []
        for _, row in df.iterrows():
            try:
                records.append(ServerRecord(
                    server_id     = str(row["server_id"]).strip(),
                    cpu_usage     = float(row["cpu_usage"]),
                    hours_running = float(row["hours_running"]),
                    cost_per_hour = float(row["cost_per_hour"]),
                    region        = str(row.get("region", "unknown")),
                    instance_type = str(row.get("instance_type", "unknown")),
                ))
            except (ValueError, KeyError) as exc:
                console.print(f"  [yellow]⚠ Skipping bad row {_}: {exc}[/yellow]")

        return records