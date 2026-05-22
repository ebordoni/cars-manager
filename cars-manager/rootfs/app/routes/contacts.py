from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
import database as db

contacts_bp = Blueprint("contacts", __name__, url_prefix="/contacts")

CONTACT_TYPES = [
    ("mechanic", "Autofficina"),
    ("dealer", "Concessionaria"),
    ("other", "Altro"),
]


@contacts_bp.route("/")
def list_contacts():
    contact_type = request.args.get("type")
    contacts = db.get_contacts(contact_type=contact_type)
    return render_template(
        "contacts/list.html",
        contacts=contacts,
        contact_types=CONTACT_TYPES,
        selected_type=contact_type,
    )


@contacts_bp.route("/new", methods=["GET", "POST"])
def new_contact():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            flash("Il nome è obbligatorio.", "danger")
            return render_template(
                "contacts/form.html", contact=request.form, contact_types=CONTACT_TYPES
            )
        db.create_contact(
            name=name,
            contact_type=request.form.get("type", "mechanic"),
            address=request.form.get("address", "").strip() or None,
            phone=request.form.get("phone", "").strip() or None,
            email=request.form.get("email", "").strip() or None,
            website=request.form.get("website", "").strip() or None,
            notes=request.form.get("notes", "").strip() or None,
        )
        flash(f"Contatto {name} aggiunto!", "success")
        return redirect(url_for("contacts.list_contacts"))

    return render_template("contacts/form.html", contact={}, contact_types=CONTACT_TYPES)


@contacts_bp.route("/<int:contact_id>/edit", methods=["GET", "POST"])
def edit_contact(contact_id):
    contact = db.get_contact(contact_id)
    if not contact:
        abort(404)

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            flash("Il nome è obbligatorio.", "danger")
            return render_template(
                "contacts/form.html", contact=request.form, contact_types=CONTACT_TYPES
            )
        db.update_contact(
            contact_id=contact_id,
            name=name,
            contact_type=request.form.get("type", "mechanic"),
            address=request.form.get("address", "").strip() or None,
            phone=request.form.get("phone", "").strip() or None,
            email=request.form.get("email", "").strip() or None,
            website=request.form.get("website", "").strip() or None,
            notes=request.form.get("notes", "").strip() or None,
        )
        flash("Contatto aggiornato!", "success")
        return redirect(url_for("contacts.list_contacts"))

    return render_template("contacts/form.html", contact=contact, contact_types=CONTACT_TYPES)


@contacts_bp.route("/<int:contact_id>/delete", methods=["POST"])
def delete_contact(contact_id):
    contact = db.get_contact(contact_id)
    if not contact:
        abort(404)
    db.delete_contact(contact_id)
    flash("Contatto eliminato.", "info")
    return redirect(url_for("contacts.list_contacts"))
