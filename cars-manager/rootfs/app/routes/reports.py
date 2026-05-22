from datetime import datetime
from flask import Blueprint, render_template, request
import database as db

reports_bp = Blueprint("reports", __name__, url_prefix="/reports")


@reports_bp.route("/")
def dashboard():
    car_id = request.args.get("car_id", type=int)
    year = request.args.get("year", type=int) or datetime.now().year

    cars = db.get_all_cars()
    maintenance_costs = db.get_maintenance_costs_by_type(car_id=car_id)
    malfunction_severity = db.get_malfunction_by_severity(car_id=car_id)
    malfunction_stats = db.get_malfunction_stats(car_id=car_id)
    monthly_costs = db.get_monthly_costs(year=year, car_id=car_id)

    # Build full 12-month cost array (fill missing months with 0)
    cost_by_month = {r["month"]: r["total_cost"] for r in monthly_costs}
    monthly_chart_data = [round(cost_by_month.get(f"{m:02d}", 0), 2) for m in range(1, 13)]

    # Maintenance costs chart data
    maint_labels = [r["type"] for r in maintenance_costs]
    maint_values = [round(r["total_cost"], 2) for r in maintenance_costs]

    # Severity chart data
    severity_order = ["low", "medium", "high", "critical"]
    severity_map = {r["severity"]: r["count"] for r in malfunction_severity}
    severity_values = [severity_map.get(s, 0) for s in severity_order]

    years_range = list(range(datetime.now().year, datetime.now().year - 6, -1))

    return render_template(
        "reports/dashboard.html",
        cars=cars,
        selected_car=car_id,
        selected_year=year,
        years_range=years_range,
        malfunction_stats=malfunction_stats,
        maintenance_costs=maintenance_costs,
        monthly_chart_data=monthly_chart_data,
        maint_labels=maint_labels,
        maint_values=maint_values,
        severity_values=severity_values,
    )
