from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
import database as db

cars_bp = Blueprint("cars", __name__, url_prefix="/cars")

FUEL_TYPES = ["Benzina", "Diesel", "GPL", "Metano", "Ibrido", "Elettrico", "Plug-in Hybrid"]


@cars_bp.route("/")
def list_cars():
    cars = db.get_all_cars()
    return render_template("cars/list.html", cars=cars)


@cars_bp.route("/new", methods=["GET", "POST"])
def new_car():
    if request.method == "POST":
        make = request.form.get("make", "").strip()
        model = request.form.get("model", "").strip()
        if not make or not model:
            flash("Marca e modello sono obbligatori.", "danger")
            return render_template("cars/form.html", car=request.form, fuel_types=FUEL_TYPES)

        car_id = db.create_car(
            make=make,
            model=model,
            year=request.form.get("year") or None,
            license_plate=request.form.get("license_plate", "").strip() or None,
            color=request.form.get("color", "").strip() or None,
            vin=request.form.get("vin", "").strip() or None,
            fuel_type=request.form.get("fuel_type", "").strip() or None,
            purchase_date=request.form.get("purchase_date") or None,
            notes=request.form.get("notes", "").strip() or None,
        )
        flash(f"Auto {make} {model} aggiunta con successo!", "success")
        return redirect(url_for("cars.car_detail", car_id=car_id))

    return render_template("cars/form.html", car={}, fuel_types=FUEL_TYPES)


@cars_bp.route("/<int:car_id>")
def car_detail(car_id):
    car = db.get_car(car_id)
    if not car:
        abort(404)
    mileage_logs = db.get_mileage_logs(car_id)
    current_mileage = mileage_logs[0]["mileage"] if mileage_logs else 0
    maintenance = db.get_maintenance_events(car_id=car_id)
    documents = db.get_documents(car_id=car_id)
    malfunctions = db.get_malfunctions(car_id=car_id)
    return render_template(
        "cars/detail.html",
        car=car,
        current_mileage=current_mileage,
        mileage_logs=mileage_logs[:5],
        maintenance=maintenance,
        documents=documents,
        malfunctions=malfunctions,
    )


@cars_bp.route("/<int:car_id>/edit", methods=["GET", "POST"])
def edit_car(car_id):
    car = db.get_car(car_id)
    if not car:
        abort(404)

    if request.method == "POST":
        make = request.form.get("make", "").strip()
        model = request.form.get("model", "").strip()
        if not make or not model:
            flash("Marca e modello sono obbligatori.", "danger")
            return render_template("cars/form.html", car=request.form, fuel_types=FUEL_TYPES)

        db.update_car(
            car_id=car_id,
            make=make,
            model=model,
            year=request.form.get("year") or None,
            license_plate=request.form.get("license_plate", "").strip() or None,
            color=request.form.get("color", "").strip() or None,
            vin=request.form.get("vin", "").strip() or None,
            fuel_type=request.form.get("fuel_type", "").strip() or None,
            purchase_date=request.form.get("purchase_date") or None,
            notes=request.form.get("notes", "").strip() or None,
        )
        flash("Auto aggiornata con successo!", "success")
        return redirect(url_for("cars.car_detail", car_id=car_id))

    return render_template("cars/form.html", car=car, fuel_types=FUEL_TYPES)


@cars_bp.route("/<int:car_id>/delete", methods=["POST"])
def delete_car(car_id):
    car = db.get_car(car_id)
    if not car:
        abort(404)
    db.delete_car(car_id)
    flash(f"Auto {car['make']} {car['model']} eliminata.", "info")
    return redirect(url_for("cars.list_cars"))
