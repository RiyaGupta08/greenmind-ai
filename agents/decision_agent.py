import json
from typing import List, Optional
from rich.console import Console
from rich.panel import Panel

from utils.models import AnomalyReport, Decision
import config

console = Console()

_openai_available = bool(config.OPENAI_API_KEY)
if _openai_available:
    try:
        from openai import OpenAI
        _llm_client = OpenAI(api_key=config.OPENAI_API_KEY)
    except ImportError:
        _openai_available = False
        _llm_client = None
else:
    _llm_client = None


class DecisionAgent:

    def run(self, reports: List[AnomalyReport]) -> List[Decision]:

        if _openai_available:
            mode = "[bold green]LLM-Powered Mode (GPT reasoning active)[/bold green]"
        else:
            mode = "[bold yellow]Rule-Based Mode (set OPENAI_API_KEY to enable LLM)[/bold yellow]"

        console.print(Panel(
            f"[bold cyan]Hybrid AI Decision Engine[/bold cyan]\n{mode}",
            border_style="cyan", expand=False
        ))

        decisions: List[Decision] = []
        for report in reports:
            decision = self._decide(report)
            decisions.append(decision)
            self._print_decision(decision)

        console.print()
        return decisions

    def _decide(self, report: AnomalyReport) -> Decision:
        if _openai_available and report.anomaly_type != "none":
            result = self._llm_decide(report)
            if result:
                return result
        return self._rule_decide(report)

    def _llm_decide(self, report: AnomalyReport) -> Optional[Decision]:
        prompt = f"""
You are an expert cloud infrastructure cost optimization AI.

Analyze this server and choose the best action.

SERVER DETAILS:
  Server ID    : {report.server_id}
  CPU Usage    : {report.cpu_usage:.1f}%
  Cost Per Hour: ${report.cost_per_hour:.2f}
  Hours Running: {report.hours_running:.0f} hours
  Anomaly      : {report.anomaly_type}
  Reason       : {report.reason}

AVAILABLE ACTIONS:
  shutdown   = stop server completely (saves 100% cost)
  scale_down = move to smaller instance (saves 50% cost)
  keep       = leave running (no saving)

Respond ONLY in valid JSON with no markdown:
{{
  "action": "shutdown OR scale_down OR keep",
  "reasoning": "2-3 sentences explaining WHY for a business audience",
  "confidence": "high OR medium OR low",
  "risk_level": "none OR low OR medium OR high"
}}
"""
        try:
            resp = _llm_client.chat.completions.create(
                model       = config.LLM_MODEL,
                messages    = [{"role": "user", "content": prompt}],
                max_tokens  = 350,
                temperature = 0.2,
            )
            raw  = resp.choices[0].message.content.strip()
            raw  = raw.replace("```json", "").replace("```", "").strip()
            data = json.loads(raw)

            return Decision(
                server_id    = report.server_id,
                action       = data["action"],
                reasoning    = data["reasoning"],
                confidence   = data.get("confidence", "medium"),
                anomaly_type = report.anomaly_type,
                risk_level   = data.get("risk_level", "low"),
                engine       = "LLM (GPT)",
            )
        except Exception as exc:
            console.print(f"  [yellow]LLM failed ({exc}) -- using rules[/yellow]")
            return None

    def _rule_decide(self, report: AnomalyReport) -> Decision:

        if report.anomaly_type == "idle":
            monthly = report.cost_per_hour * 730
            return Decision(
                server_id    = report.server_id,
                action       = "shutdown",
                reasoning    = (
                    f"CPU usage is only {report.cpu_usage:.1f}% over "
                    f"{report.hours_running:.0f} hours of runtime. "
                    f"At ${report.cost_per_hour:.2f}/hr with zero productive workload, "
                    f"this server wastes ~${monthly:,.0f}/month. "
                    f"Immediate shutdown eliminates 100% of this cost with no service impact."
                ),
                confidence   = "high",
                anomaly_type = report.anomaly_type,
                risk_level   = "low",
                engine       = "Rule Engine",
            )

        if report.anomaly_type == "underutilised":
            monthly = report.cost_per_hour * 0.5 * 730
            return Decision(
                server_id    = report.server_id,
                action       = "scale_down",
                reasoning    = (
                    f"CPU is at {report.cpu_usage:.1f}% on a "
                    f"${report.cost_per_hour:.2f}/hr premium instance. "
                    f"The workload does not justify this tier. "
                    f"Right-sizing saves ~${monthly:,.0f}/month "
                    f"while maintaining full availability."
                ),
                confidence   = "medium",
                anomaly_type = report.anomaly_type,
                risk_level   = "low",
                engine       = "Rule Engine",
            )

        return Decision(
            server_id    = report.server_id,
            action       = "keep",
            reasoning    = (
                f"CPU at {report.cpu_usage:.1f}% -- server is earning its "
                f"cost of ${report.cost_per_hour:.2f}/hr. No action required."
            ),
            confidence   = "high",
            anomaly_type = report.anomaly_type,
            risk_level   = "none",
            engine       = "Rule Engine",
        )

    def _print_decision(self, d: Decision):
        colors = {"shutdown": "red", "scale_down": "yellow", "keep": "green"}
        icons  = {"shutdown": "🔴", "scale_down": "🟡", "keep": "🟢"}
        color  = colors.get(d.action, "white")
        icon   = icons.get(d.action, "o")

        console.print(
            f"\n  {icon} [cyan]{d.server_id}[/cyan]  "
            f"->  [{color}]{d.action.upper()}[/{color}]  "
            f"[dim]({d.confidence} confidence | risk: {d.risk_level} | {d.engine})[/dim]"
        )
        console.print(f"     [dim italic]{d.reasoning}[/dim italic]")