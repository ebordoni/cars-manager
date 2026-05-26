import os
import uuid
from flask import (Blueprint, render_template, request, redirect,
                   url_for, flash, abort, send_from_directory, current_app)
from werkzeug.utils import secure_filename
import database as db

documents_bp = Blueprint("documents", __name__, url_prefix="/documents")

ALLOWED_EXTENSIONS = {"pdf", "jpg", "jpeg", "png", "docx", "xlsx", "doc", "xls"}

DOC_TYPES = [
    ("libretto", "Libretto di circolazione"),
    ("assicurazione", "Certificato assicurativo"),
    ("fattura", "Fattura / Ricevuta"),
    ("revisione", "Verbale di revisione"),
    ("altro", "Altro"),
]


def _allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@documents_bp.route("/")
def list_documents():
    car_id = request.args.get("car_id", type=int)
    doc_type = request.args.get("type")
    docs = db.get_documents(car_id=car_id, doc_type=doc_type)
    cars = db.get_all_cars()
    return render_template(
        "documents/list.html",
        docs=docs,
        cars=cars,
        doc_types=DOC_TYPES,
        selected_car=car_id,
        selected_type=doc_type,
    )


@documents_bp.route("/upload", methods=["GET", "POST"])
def upload_document():
    cars = db.get_all_cars()
    preselect_car = request.args.get("car_id", type=int)

    if request.method == "POST":
        car_id = request.form.get("car_id", type=int)
        title = request.form.get("title", "").strip()
        file = request.files.get("file")

        if not car_id or not title:
            flash("Auto e titolo sono obbligatori.", "danger")
            return render_template(
                "documents/upload.html",
                cars=cars,
                doc_types=DOC_TYPES,
                form=request.form,
            )

        if not file or file.filename == "":
            flash("Seleziona un file da caricare.", "danger")
            return render_template(
                "documents/upload.html",
                cars=cars,
                doc_types=DOC_TYPES,
                form=request.form,
            )

        if not _allowed_file(file.filename):
            flash(
                f"Tipo di file non consentito. Formati accettati: {', '.join(ALLOWED_EXTENSIONS)}",
                "danger",
            )
            return render_template(
                "documents/upload.html",
                cars=cars,
                doc_types=DOC_TYPES,
                form=request.form,
            )

        original_name = secure_filename(file.filename)
        ext = original_name.rsplit(".", 1)[1].lower()
        stored_name = f"{uuid.uuid4().hex}.{ext}"
        upload_folder = current_app.config["UPLOAD_FOLDER"]
        os.makedirs(upload_folder, exist_ok=True)
        save_path = os.path.join(upload_folder, stored_name)
        file.save(save_path)
        file_size = os.path.getsize(save_path)

        db.create_document(
            car_id=car_id,
            doc_type=request.form.get("type", "altro"),
            title=title,
            filename=stored_name,
            original_name=original_name,
            file_size=file_size,
            notes=request.form.get("notes", "").strip() or None,
            cost=request.form.get("cost", type=float) or None,
        )
        flash("Documento caricato con successo!", "success")
        return redirect(url_for("documents.list_documents"))

    return render_template(
        "documents/upload.html",
        cars=cars,
        doc_types=DOC_TYPES,
        form={"car_id": preselect_car},
    )


@documents_bp.route("/<int:doc_id>/download")
def download_document(doc_id):
    doc = db.get_document(doc_id)
    if not doc:
        abort(404)
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    return send_from_directory(
        upload_folder,
        doc["filename"],
        as_attachment=True,
        download_name=doc["original_name"],
    )


@documents_bp.route("/<int:doc_id>/edit", methods=["GET", "POST"])
def edit_document(doc_id):
    doc = db.get_document(doc_id)
    if not doc:
        abort(404)

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        if not title:
            flash("Il titolo è obbligatorio.", "danger")
            return render_template(
                "documents/edit.html",
                doc=doc,
                doc_types=DOC_TYPES,
            )

        file = request.files.get("file")
        new_filename = None
        new_original_name = None
        new_file_size = None

        if file and file.filename != "":
            if not _allowed_file(file.filename):
                flash(
                    f"Tipo di file non consentito. Formati accettati: {', '.join(ALLOWED_EXTENSIONS)}",
                    "danger",
                )
                return render_template(
                    "documents/edit.html",
                    doc=doc,
                    doc_types=DOC_TYPES,
                )
            new_original_name = secure_filename(file.filename)
            ext = new_original_name.rsplit(".", 1)[1].lower()
            new_filename = f"{uuid.uuid4().hex}.{ext}"
            upload_folder = current_app.config["UPLOAD_FOLDER"]
            os.makedirs(upload_folder, exist_ok=True)
            save_path = os.path.join(upload_folder, new_filename)
            file.save(save_path)
            new_file_size = os.path.getsize(save_path)
            # Remove old file
            old_path = os.path.join(upload_folder, doc["filename"])
            if os.path.exists(old_path):
                os.remove(old_path)

        db.update_document(
            doc_id=doc_id,
            doc_type=request.form.get("type", "altro"),
            title=title,
            notes=request.form.get("notes", "").strip() or None,
            cost=request.form.get("cost", type=float) or None,
            filename=new_filename,
            original_name=new_original_name,
            file_size=new_file_size,
        )
        flash("Documento aggiornato con successo!", "success")
        return redirect(url_for("documents.list_documents"))

    return render_template(
        "documents/edit.html",
        doc=doc,
        doc_types=DOC_TYPES,
    )


@documents_bp.route("/<int:doc_id>/delete", methods=["POST"])
def delete_document(doc_id):
    doc = db.get_document(doc_id)
    if not doc:
        abort(404)
    # Remove file from disk
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    file_path = os.path.join(upload_folder, doc["filename"])
    if os.path.exists(file_path):
        os.remove(file_path)
    db.delete_document(doc_id)
    flash("Documento eliminato.", "info")
    return redirect(url_for("documents.list_documents"))
