from typing import List, Dict
from utils.models import AnomalyReport
import config

USD_TO_INR = 83.0


def predict_future_waste(
    anomalies: List[AnomalyReport],
    days: int = config.PREDICTION_DAYS,
) -> Dict[str, float]:
    predictions: Dict[str, float] = {}
    for a in anomalies:
        if a.anomaly_type == "none":
            continue
        forecast_hours = 24 * days
        waste = a.cost_per_hour * forecast_hours if a.anomaly_type == "idle" \
                else a.cost_per_hour * 0.5 * forecast_hours
        predictions[a.server_id] = round(waste, 2)
    return predictions


def format_predictions(predictions: Dict[str, float]) -> str:
    if not predictions:
        return "  No future waste predicted!"

    total_usd = sum(predictions.values())
    total_inr = total_usd * USD_TO_INR

    lines = ["  30-day waste forecast (if NO action taken):\n"]
    for sid, waste_usd in sorted(predictions.items(), key=lambda x: -x[1]):
        waste_inr = waste_usd * USD_TO_INR
        lines.append(
            f"    {sid:<12}  ${waste_usd:>8,.2f}  "
            f"approx  Rs.{waste_inr:>10,.0f}"
        )
    lines.append(
        f"\n    {'TOTAL':<12}  ${total_usd:>8,.2f}  "
        f"approx  Rs.{total_inr:>10,.0f}"
    )
    return "\n".join(lines)


def format_7day_warning(anomalies: List[AnomalyReport]) -> str:
    waste_7d = sum(predict_future_waste(anomalies, days=7).values())
    if waste_7d == 0:
        return ""
    inr = waste_7d * USD_TO_INR
    return (
        f"  WARNING — Projected waste in 7 days if no action: "
        f"${waste_7d:,.2f}  approx  Rs.{inr:,.0f}"
    )