from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
import database as db

maintenance_bp = Blueprint("maintenance", __name__, url_prefix="/maintenance")

EVENT_TYPES = [
    ("maintenance", "Manutenzione"),
    ("revision", "Revisione"),
    ("bollo", "Bollo Auto"),
    ("insurance", "Assicurazione"),
    ("other", "Altro"),
]


@maintenance_bp.route("/")
def list_maintenance():
    db.refresh_overdue_status()
    car_id = request.args.get("car_id", type=int)
    status = request.args.get("status")
    event_type = request.args.get("type")
    events = db.get_maintenance_events(car_id=car_id, status=status, event_type=event_type)
    cars = db.get_all_cars()
    return render_template(
        "maintenance/list.html",
        events=events,
        cars=cars,
        event_types=EVENT_TYPES,
        selected_car=car_id,
        selected_status=status,
        selected_type=event_type,
    )


@maintenance_bp.route("/new", methods=["GET", "POST"])
def new_event():
    cars = db.get_all_cars()
    preselect_car = request.args.get("car_id", type=int)

    if request.method == "POST":
        car_id = request.form.get("car_id", type=int)
        title = request.form.get("title", "").strip()
        if not car_id or not title:
            flash("Auto e titolo sono obbligatori.", "danger")
            return render_template(
                "maintenance/form.html",
                event=request.form,
                cars=cars,
                event_types=EVENT_TYPES,
            )

        cost_raw = request.form.get("cost", "").strip()
        db.create_maintenance_event(
            car_id=car_id,
            event_type=request.form.get("type", "maintenance"),
            title=title,
            due_date=request.form.get("due_date") or None,
            notes=request.form.get("notes", "").strip() or None,
            reminder_days=int(request.form.get("reminder_days", 30)),
            recurrence_months=int(request.form.get("recurrence_months", 0)),
            cost=float(cost_raw) if cost_raw else None,
        )
        flash("Scadenza aggiunta con successo!", "success")
        return redirect(url_for("maintenance.list_maintenance"))

    return render_template(
        "maintenance/form.html",
        event={"car_id": preselect_car},
        cars=cars,
        event_types=EVENT_TYPES,
    )


@maintenance_bp.route("/<int:event_id>/edit", methods=["GET", "POST"])
def edit_event(event_id):
    event = db.get_maintenance_event(event_id)
    if not event:
        abort(404)
    cars = db.get_all_cars()

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        if not title:
            flash("Il titolo è obbligatorio.", "danger")
            return render_template(
                "maintenance/form.html",
                event=request.form,
                cars=cars,
                event_types=EVENT_TYPES,
            )
        cost_raw = request.form.get("cost", "").strip()
        db.update_maintenance_event(
            event_id=event_id,
            event_type=request.form.get("type", "maintenance"),
            title=title,
            due_date=request.form.get("due_date") or None,
            notes=request.form.get("notes", "").strip() or None,
            reminder_days=int(request.form.get("reminder_days", 30)),
            recurrence_months=int(request.form.get("recurrence_months", 0)),
            cost=float(cost_raw) if cost_raw else None,
        )
        flash("Scadenza aggiornata!", "success")
        return redirect(url_for("maintenance.list_maintenance"))

    return render_template(
        "maintenance/form.html",
        event=event,
        cars=cars,
        event_types=EVENT_TYPES,
    )


@maintenance_bp.route("/<int:event_id>/complete", methods=["POST"])
def complete_event(event_id):
    event = db.get_maintenance_event(event_id)
    if not event:
        abort(404)
    completed_date = request.form.get("completed_date") or __import__("datetime").date.today().isoformat()
    cost_raw = request.form.get("cost", "").strip()
    cost = float(cost_raw) if cost_raw else None
    notes = request.form.get("notes", "").strip() or None
    db.complete_maintenance_event(event_id, completed_date, cost, notes)
    flash("Scadenza contrassegnata come completata!", "success")
    return redirect(url_for("maintenance.list_maintenance"))


@maintenance_bp.route("/<int:event_id>/delete", methods=["POST"])
def delete_event(event_id):
    event = db.get_maintenance_event(event_id)
    if not event:
        abort(404)
    db.delete_maintenance_event(event_id)
    flash("Scadenza eliminata.", "info")
    return redirect(url_for("maintenance.list_maintenance"))
