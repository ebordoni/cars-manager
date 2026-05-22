from .main import main_bp
from .cars import cars_bp
from .maintenance import maintenance_bp
from .documents import documents_bp
from .malfunctions import malfunctions_bp
from .contacts import contacts_bp
from .mileage import mileage_bp
from .reports import reports_bp


def register_routes(app):
    app.register_blueprint(main_bp)
    app.register_blueprint(cars_bp)
    app.register_blueprint(maintenance_bp)
    app.register_blueprint(documents_bp)
    app.register_blueprint(malfunctions_bp)
    app.register_blueprint(contacts_bp)
    app.register_blueprint(mileage_bp)
    app.register_blueprint(reports_bp)
