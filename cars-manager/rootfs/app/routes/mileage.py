from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
import database as db

mileage_bp = Blueprint("mileage", __name__, url_prefix="/mileage")


@mileage_bp.route("/<int:car_id>")
def mileage_history(car_id):
    car = db.get_car(car_id)
    if not car:
        abort(404)
    logs = db.get_mileage_logs(car_id)
    return render_template("mileage/history.html", car=car, logs=logs)


@mileage_bp.route("/<int:car_id>/add", methods=["GET", "POST"])
def add_mileage(car_id):
    car = db.get_car(car_id)
    if not car:
        abort(404)

    if request.method == "POST":
        mileage_raw = request.form.get("mileage", "").strip()
        if not mileage_raw or not mileage_raw.isdigit():
            flash("Inserisci un chilometraggio valido.", "danger")
            return render_template(
                "mileage/form.html",
                car=car,
                today=date.today().isoformat(),
            )
        mileage = int(mileage_raw)
        log_date = request.form.get("date") or date.today().isoformat()
        notes = request.form.get("notes", "").strip() or None

        latest = db.get_latest_mileage(car_id)
        if mileage < latest:
            flash(
                f"Il chilometraggio inserito ({mileage:,} km) è inferiore all'ultimo rilevamento ({latest:,} km).",
                "warning",
            )

        db.add_mileage_log(car_id, mileage, log_date, notes)
        flash(f"Chilometraggio aggiornato a {mileage:,} km!", "success")
        return redirect(url_for("cars.car_detail", car_id=car_id))

    return render_template(
        "mileage/form.html",
        car=car,
        today=date.today().isoformat(),
    )


@mileage_bp.route("/log/<int:log_id>/delete", methods=["POST"])
def delete_log(log_id):
    car_id = request.form.get("car_id", type=int)
    db.delete_mileage_log(log_id)
    flash("Rilevamento eliminato.", "info")
    if car_id:
        return redirect(url_for("mileage.mileage_history", car_id=car_id))
    return redirect(url_for("cars.list_cars"))
