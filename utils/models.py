from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class ServerRecord:
    server_id:     str
    cpu_usage:     float
    hours_running: float
    cost_per_hour: float
    region:        str = "unknown"
    instance_type: str = "unknown"

    @property
    def total_cost(self) -> float:
        return self.cost_per_hour * self.hours_running


@dataclass
class AnomalyReport:
    server_id:     str
    anomaly_type:  str
    severity:      str
    reason:        str
    cpu_usage:     float
    cost_per_hour: float
    hours_running: float


@dataclass
class Decision:
    server_id:    str
    action:       str
    reasoning:    str
    confidence:   str
    anomaly_type: str
    risk_level:   str = "low"
    engine:       str = "Rule Engine"


@dataclass
class ActionResult:
    server_id:        str
    action_taken:     str
    cost_before:      float
    cost_after:       float
    hourly_saving:    float
    monthly_saving:   float
    weekly_waste_usd: float
    status:           str
    reasoning:        str = ""
    executed_at:      str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class AuditEntry:
    server_id:     str
    anomaly:       Optional[AnomalyReport]
    decision:      Optional[Decision]
    action_result: Optional[ActionResult]
    timestamp:     str = field(default_factory=lambda: datetime.now().isoformat())