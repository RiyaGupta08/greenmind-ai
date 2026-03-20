from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from typing import List
from utils.models import ActionResult, AuditEntry

console = Console()
USD_TO_INR = 83.0


def print_banner():
    console.print(Panel(
        "[bold green]GreenMind AI[/bold green]\n"
        "[dim]Autonomous Cloud Cost Optimization System\n"
        "Powered by Hybrid AI Decision Engine (LLM + Rules)[/dim]",
        border_style="green", expand=False
    ))


def print_section(title: str):
    console.rule(f"[bold cyan]{title}[/bold cyan]")


def print_savings_table(results: List[ActionResult]):
    table = Table(
        title="Cost Optimization Summary",
        box=box.ROUNDED,
        header_style="bold magenta",
        show_lines=True,
    )
    table.add_column("Server",          style="cyan",       no_wrap=True)
    table.add_column("Action",          style="yellow")
    table.add_column("$/hr Before",     style="red",        justify="right")
    table.add_column("$/hr After",      style="green",      justify="right")
    table.add_column("Monthly Saving",  style="bold green", justify="right")
    table.add_column("7-day Waste",     style="red",        justify="right")
    table.add_column("Status",          style="white")
    table.add_column("AI Reason",       style="dim",        max_width=45)

    total_hourly  = 0.0
    total_monthly = 0.0

    for r in results:
        color = {
            "shutdown":   "red",
            "scale_down": "yellow",
            "keep":       "dim",
        }.get(r.action_taken, "white")

        reason_short = (r.reasoning[:80] + "...") if len(r.reasoning) > 80 else r.reasoning

        table.add_row(
            r.server_id,
            f"[{color}]{r.action_taken}[/{color}]",
            f"${r.cost_before:.2f}",
            f"${r.cost_after:.2f}",
            f"${r.monthly_saving:,.2f}",
            f"${r.weekly_waste_usd:.2f}",
            r.status,
            reason_short,
        )
        total_hourly  += r.hourly_saving
        total_monthly += r.monthly_saving

    console.print(table)

    total_inr = total_monthly * USD_TO_INR
    console.print(Panel(
        f"[bold]Total Hourly Saving :[/bold]  [green]${total_hourly:.2f}/hr[/green]\n"
        f"[bold]Total Monthly Saving:[/bold]  [bold green]${total_monthly:,.2f}[/bold green]"
        f"  approx  [bold green]Rs.{total_inr:,.0f}[/bold green]",
        title="Grand Total", border_style="green"
    ))


def print_audit_summary(entries: List[AuditEntry]):
    print_section("Audit Trail")
    for e in entries:
        if not e.action_result:
            continue
        ar    = e.action_result
        color = {
            "shutdown":   "red",
            "scale_down": "yellow",
            "keep":       "green",
        }.get(ar.action_taken, "white")
        console.print(
            f"  [cyan]{e.server_id}[/cyan]  "
            f"[{color}]{ar.action_taken:<12}[/{color}]  "
            f"saving [green]${ar.monthly_saving:,.2f}/mo[/green]  "
            f"[dim]{e.timestamp[:19]}[/dim]"
        )
        if ar.reasoning:
            short = (ar.reasoning[:90] + "...") if len(ar.reasoning) > 90 else ar.reasoning
            console.print(f"    [dim italic]-- {short}[/dim italic]")