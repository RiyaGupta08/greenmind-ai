from typing import List, Dict
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm

from utils.models import Decision, ServerRecord, ActionResult
import config

console = Console()


class ActionAgent:

    def run(self, decisions: List[Decision], records: List[ServerRecord]) -> List[ActionResult]:
        console.print("[bold cyan]ActionAgent:[/bold cyan] Preparing to execute actions...\n")

        record_map: Dict[str, ServerRecord] = {r.server_id: r for r in records}

        results: List[ActionResult] = []
        for decision in decisions:
            rec = record_map.get(decision.server_id)
            if rec is None:
                continue

            result = self._execute(decision, rec)
            results.append(result)

            icon = "OK" if result.status == "executed" else "SKIPPED"
            console.print(
                f"  [{icon}] [cyan]{rec.server_id}[/cyan]  "
                f"[yellow]{result.action_taken}[/yellow]  "
                f"-> saving [bold green]${result.monthly_saving:,.2f}[/bold green]/mo  "
                f"| 7-day waste avoided: [green]${result.weekly_waste_usd:.2f}[/green]"
            )

        console.print()
        return results

    def _execute(self, decision: Decision, rec: ServerRecord) -> ActionResult:

        savings_rate     = config.SAVINGS_RATE.get(decision.action, 0.0)
        hourly_saving    = rec.cost_per_hour * savings_rate
        cost_after       = rec.cost_per_hour - hourly_saving
        monthly_saving   = hourly_saving * 730
        weekly_waste_usd = rec.cost_per_hour * 24 * 7

        if config.HUMAN_APPROVAL_REQUIRED and decision.action != "keep":
            console.print(Panel(
                f"[bold]Server:[/bold]         [cyan]{rec.server_id}[/cyan]\n"
                f"[bold]Action:[/bold]         [yellow]{decision.action.upper()}[/yellow]\n"
                f"[bold]Reason:[/bold]         {decision.reasoning}\n"
                f"[bold]Monthly saving:[/bold]  [green]${monthly_saving:,.2f}[/green]\n"
                f"[bold]7-day waste if skipped:[/bold] [red]${weekly_waste_usd:.2f}[/red]",
                title="Human Approval Required",
                border_style="yellow"
            ))
            approved = Confirm.ask("  Approve this action?")
            if not approved:
                return self._build_result(
                    rec, decision, "pending_approval",
                    hourly_saving, cost_after, monthly_saving, weekly_waste_usd
                )

        return self._build_result(
            rec, decision, "executed",
            hourly_saving, cost_after, monthly_saving, weekly_waste_usd
        )

    def _build_result(self, rec, decision, status,
                      hourly_saving, cost_after, monthly_saving, weekly_waste_usd):
        return ActionResult(
            server_id        = rec.server_id,
            action_taken     = decision.action,
            cost_before      = rec.cost_per_hour,
            cost_after       = cost_after,
            hourly_saving    = hourly_saving,
            monthly_saving   = monthly_saving,
            weekly_waste_usd = weekly_waste_usd,
            status           = status,
            reasoning        = decision.reasoning,
        )