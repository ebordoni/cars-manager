from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
import database as db
from email_utils import send_quote_email

malfunctions_bp = Blueprint("malfunctions", __name__, url_prefix="/malfunctions")

SEVERITY_LABELS = {
    "low": "Bassa",
    "medium": "Media",
    "high": "Alta",
    "critical": "Critica",
}


@malfunctions_bp.route("/")
def list_malfunctions():
    car_id = request.args.get("car_id", type=int)
    status = request.args.get("status")
    items = db.get_malfunctions(car_id=car_id, status=status)
    cars = db.get_all_cars()
    return render_template(
        "malfunctions/list.html",
        items=items,
        cars=cars,
        severity_labels=SEVERITY_LABELS,
        selected_car=car_id,
        selected_status=status,
    )


@malfunctions_bp.route("/<int:malfunction_id>")
def malfunction_detail(malfunction_id):
    item = db.get_malfunction(malfunction_id)
    if not item:
        abort(404)
    contacts = db.get_contacts()
    return render_template(
        "malfunctions/detail.html",
        item=item,
        contacts=contacts,
        severity_labels=SEVERITY_LABELS,
    )


@malfunctions_bp.route("/new", methods=["GET", "POST"])
def new_malfunction():
    cars = db.get_all_cars()
    preselect_car = request.args.get("car_id", type=int)

    if request.method == "POST":
        car_id = request.form.get("car_id", type=int)
        title = request.form.get("title", "").strip()
        if not car_id or not title:
            flash("Auto e titolo sono obbligatori.", "danger")
            return render_template(
                "malfunctions/form.html",
                item=request.form,
                cars=cars,
                severity_labels=SEVERITY_LABELS,
            )
        db.create_malfunction(
            car_id=car_id,
            title=title,
            description=request.form.get("description", "").strip() or None,
            severity=request.form.get("severity", "medium"),
            date_reported=request.form.get("date_reported") or date.today().isoformat(),
        )
        flash("Guasto segnalato con successo!", "success")
        return redirect(url_for("malfunctions.list_malfunctions"))

    return render_template(
        "malfunctions/form.html",
        item={"car_id": preselect_car, "date_reported": date.today().isoformat()},
        cars=cars,
        severity_labels=SEVERITY_LABELS,
    )


@malfunctions_bp.route("/<int:malfunction_id>/edit", methods=["GET", "POST"])
def edit_malfunction(malfunction_id):
    item = db.get_malfunction(malfunction_id)
    if not item:
        abort(404)
    cars = db.get_all_cars()

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        if not title:
            flash("Il titolo è obbligatorio.", "danger")
            return render_template(
                "malfunctions/form.html",
                item=request.form,
                cars=cars,
                severity_labels=SEVERITY_LABELS,
            )
        db.update_malfunction(
            malfunction_id=malfunction_id,
            title=title,
            description=request.form.get("description", "").strip() or None,
            severity=request.form.get("severity", "medium"),
            date_reported=request.form.get("date_reported") or item["date_reported"],
        )
        flash("Guasto aggiornato!", "success")
        return redirect(url_for("malfunctions.malfunction_detail", malfunction_id=malfunction_id))

    return render_template(
        "malfunctions/form.html",
        item=item,
        cars=cars,
        severity_labels=SEVERITY_LABELS,
    )


@malfunctions_bp.route("/<int:malfunction_id>/resolve", methods=["POST"])
def resolve_malfunction(malfunction_id):
    item = db.get_malfunction(malfunction_id)
    if not item:
        abort(404)
    resolved_date = request.form.get("resolved_date") or date.today().isoformat()
    cost_raw = request.form.get("cost", "").strip()
    cost = float(cost_raw) if cost_raw else None
    resolution_notes = request.form.get("resolution_notes", "").strip() or None
    db.resolve_malfunction(malfunction_id, resolved_date, resolution_notes, cost)
    flash("Guasto contrassegnato come risolto!", "success")
    return redirect(url_for("malfunctions.malfunction_detail", malfunction_id=malfunction_id))


@malfunctions_bp.route("/<int:malfunction_id>/delete", methods=["POST"])
def delete_malfunction(malfunction_id):
    item = db.get_malfunction(malfunction_id)
    if not item:
        abort(404)
    db.delete_malfunction(malfunction_id)
    flash("Segnalazione eliminata.", "info")
    return redirect(url_for("malfunctions.list_malfunctions"))


@malfunctions_bp.route("/<int:malfunction_id>/email", methods=["GET", "POST"])
def send_email(malfunction_id):
    item = db.get_malfunction(malfunction_id)
    if not item:
        abort(404)
    contacts = [c for c in db.get_contacts() if c.get("email")]

    if request.method == "POST":
        contact_id = request.form.get("contact_id", type=int)
        subject = request.form.get("subject", "").strip()
        body = request.form.get("body", "").strip()

        if not contact_id or not subject or not body:
            flash("Seleziona un contatto e compila oggetto e messaggio.", "danger")
            return render_template(
                "malfunctions/email.html",
                item=item,
                contacts=contacts,
                form=request.form,
            )

        contact = db.get_contact(contact_id)
        if not contact or not contact.get("email"):
            flash("Contatto non valido o privo di email.", "danger")
            return redirect(url_for("malfunctions.send_email", malfunction_id=malfunction_id))

        try:
            send_quote_email(contact["email"], subject, body)
            flash(f"Email inviata a {contact['name']} ({contact['email']})!", "success")
            return redirect(
                url_for("malfunctions.malfunction_detail", malfunction_id=malfunction_id)
            )
        except (ValueError, RuntimeError) as exc:
            flash(str(exc), "danger")
            return render_template(
                "malfunctions/email.html",
                item=item,
                contacts=contacts,
                form=request.form,
            )

    # Pre-fill subject and body from the malfunction data
    car_label = f"{item['make']} {item['model']} ({item.get('license_plate', '')})"
    default_subject = f"Richiesta preventivo – {item['title']} – {car_label}"
    default_body = (
        f"Gentile team,\n\n"
        f"Vi contatto per richiedere un preventivo relativo al seguente problema riscontrato "
        f"sul mio veicolo {car_label}:\n\n"
        f"Problema: {item['title']}\n"
        f"Descrizione: {item.get('description') or 'Non specificata'}\n\n"
        f"Potete fornirmi una stima dei costi e dei tempi di intervento?\n\n"
        f"Cordiali saluti"
    )

    return render_template(
        "malfunctions/email.html",
        item=item,
        contacts=contacts,
        form={"subject": default_subject, "body": default_body},
    )
