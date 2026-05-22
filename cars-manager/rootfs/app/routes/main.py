from flask import Blueprint, render_template
import database as db

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    db.refresh_overdue_status()
    stats = db.get_dashboard_stats()
    upcoming = db.get_upcoming_maintenance(days=60)
    open_faults = db.get_malfunctions(status="open")
    cars = db.get_all_cars()
    return render_template(
        "index.html",
        stats=stats,
        upcoming=upcoming,
        open_faults=open_faults[:5],
        cars=cars,
    )
