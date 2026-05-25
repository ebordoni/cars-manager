import sqlite3
import os
import calendar
from datetime import datetime, date

DB_PATH = "/data/cars_manager.db"
UPLOAD_PATH = "/data/uploads"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Initialize the database schema and required directories."""
    os.makedirs(os.path.join(UPLOAD_PATH, "documents"), exist_ok=True)

    conn = get_db()
    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS cars (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                make           TEXT    NOT NULL,
                model          TEXT    NOT NULL,
                year           INTEGER,
                license_plate  TEXT,
                color          TEXT,
                vin            TEXT,
                fuel_type      TEXT,
                purchase_date  TEXT,
                notes          TEXT,
                created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS mileage_logs (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                car_id     INTEGER NOT NULL,
                mileage    INTEGER NOT NULL,
                date       TEXT    NOT NULL,
                notes      TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (car_id) REFERENCES cars(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS maintenance_events (
                id                 INTEGER PRIMARY KEY AUTOINCREMENT,
                car_id             INTEGER NOT NULL,
                type               TEXT    NOT NULL,
                title              TEXT    NOT NULL,
                due_date           TEXT,
                completed_date     TEXT,
                cost               REAL,
                notes              TEXT,
                status             TEXT DEFAULT 'pending',
                reminder_days      INTEGER DEFAULT 30,
                recurrence_months  INTEGER DEFAULT 0,
                created_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (car_id) REFERENCES cars(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS documents (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                car_id        INTEGER NOT NULL,
                type          TEXT    NOT NULL,
                title         TEXT    NOT NULL,
                filename      TEXT    NOT NULL,
                original_name TEXT    NOT NULL,
                file_size     INTEGER,
                upload_date   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes         TEXT,
                FOREIGN KEY (car_id) REFERENCES cars(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS malfunctions (
                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                car_id           INTEGER NOT NULL,
                title            TEXT    NOT NULL,
                description      TEXT,
                severity         TEXT DEFAULT 'medium',
                date_reported    TEXT    NOT NULL,
                status           TEXT DEFAULT 'open',
                resolved_date    TEXT,
                resolution_notes TEXT,
                cost             REAL,
                created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (car_id) REFERENCES cars(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS contacts (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                name       TEXT NOT NULL,
                type       TEXT NOT NULL,
                address    TEXT,
                phone      TEXT,
                email      TEXT,
                website    TEXT,
                notes      TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        conn.commit()
        # Migrate existing databases
        try:
            conn.execute(
                "ALTER TABLE maintenance_events ADD COLUMN recurrence_months INTEGER DEFAULT 0"
            )
            conn.commit()
        except Exception:
            pass  # column already exists
    finally:
        conn.close()


# ===========================================================================
# CARS
# ===========================================================================


def get_all_cars():
    conn = get_db()
    try:
        rows = conn.execute(
            """
            SELECT c.*,
                   (SELECT mileage FROM mileage_logs
                    WHERE car_id = c.id
                    ORDER BY date DESC, created_at DESC LIMIT 1) AS current_mileage,
                   (SELECT COUNT(*) FROM maintenance_events
                    WHERE car_id = c.id AND status IN ('pending','overdue')) AS pending_maintenance,
                   (SELECT COUNT(*) FROM malfunctions
                    WHERE car_id = c.id AND status = 'open') AS open_malfunctions
            FROM cars c
            ORDER BY c.make, c.model
            """
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_car(car_id):
    conn = get_db()
    try:
        row = conn.execute("SELECT * FROM cars WHERE id = ?", (car_id,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def create_car(make, model, year=None, license_plate=None, color=None,
               vin=None, fuel_type=None, purchase_date=None, notes=None):
    conn = get_db()
    try:
        cur = conn.execute(
            """
            INSERT INTO cars (make, model, year, license_plate, color,
                              vin, fuel_type, purchase_date, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (make, model, year or None, license_plate or None, color or None,
             vin or None, fuel_type or None, purchase_date or None, notes or None),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def update_car(car_id, make, model, year=None, license_plate=None, color=None,
               vin=None, fuel_type=None, purchase_date=None, notes=None):
    conn = get_db()
    try:
        conn.execute(
            """
            UPDATE cars SET make=?, model=?, year=?, license_plate=?, color=?,
                            vin=?, fuel_type=?, purchase_date=?, notes=?
            WHERE id=?
            """,
            (make, model, year or None, license_plate or None, color or None,
             vin or None, fuel_type or None, purchase_date or None, notes or None, car_id),
        )
        conn.commit()
    finally:
        conn.close()


def delete_car(car_id):
    conn = get_db()
    try:
        conn.execute("DELETE FROM cars WHERE id = ?", (car_id,))
        conn.commit()
    finally:
        conn.close()


# ===========================================================================
# MILEAGE
# ===========================================================================


def get_mileage_logs(car_id):
    conn = get_db()
    try:
        rows = conn.execute(
            "SELECT * FROM mileage_logs WHERE car_id = ? ORDER BY date DESC, created_at DESC",
            (car_id,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_latest_mileage(car_id):
    conn = get_db()
    try:
        row = conn.execute(
            "SELECT mileage FROM mileage_logs WHERE car_id = ? ORDER BY date DESC, created_at DESC LIMIT 1",
            (car_id,),
        ).fetchone()
        return row["mileage"] if row else 0
    finally:
        conn.close()


def add_mileage_log(car_id, mileage, log_date, notes=None):
    conn = get_db()
    try:
        cur = conn.execute(
            "INSERT INTO mileage_logs (car_id, mileage, date, notes) VALUES (?, ?, ?, ?)",
            (car_id, mileage, log_date, notes or None),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def delete_mileage_log(log_id):
    conn = get_db()
    try:
        conn.execute("DELETE FROM mileage_logs WHERE id = ?", (log_id,))
        conn.commit()
    finally:
        conn.close()


# ===========================================================================
# MAINTENANCE EVENTS
# ===========================================================================


def get_maintenance_events(car_id=None, status=None, event_type=None):
    conn = get_db()
    try:
        query = """
            SELECT me.*, c.make, c.model, c.license_plate,
                   CAST((julianday(me.due_date) - julianday('now')) AS INTEGER) AS days_remaining
            FROM maintenance_events me
            JOIN cars c ON me.car_id = c.id
            WHERE 1=1
        """
        params = []
        if car_id:
            query += " AND me.car_id = ?"
            params.append(car_id)
        if status:
            query += " AND me.status = ?"
            params.append(status)
        if event_type:
            query += " AND me.type = ?"
            params.append(event_type)
        query += " ORDER BY me.due_date ASC NULLS LAST, me.created_at DESC"
        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_maintenance_event(event_id):
    conn = get_db()
    try:
        row = conn.execute(
            """
            SELECT me.*, c.make, c.model, c.license_plate
            FROM maintenance_events me
            JOIN cars c ON me.car_id = c.id
            WHERE me.id = ?
            """,
            (event_id,),
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def create_maintenance_event(car_id, event_type, title, due_date=None,
                              notes=None, reminder_days=30, recurrence_months=0, cost=None):
    conn = get_db()
    try:
        cur = conn.execute(
            """
            INSERT INTO maintenance_events
                (car_id, type, title, due_date, notes, status, reminder_days, recurrence_months, cost)
            VALUES (?, ?, ?, ?, ?, 'pending', ?, ?, ?)
            """,
            (car_id, event_type, title, due_date or None, notes or None,
             reminder_days, recurrence_months or 0, cost),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def update_maintenance_event(event_id, event_type, title, due_date=None,
                              notes=None, reminder_days=30, recurrence_months=0, cost=None):
    conn = get_db()
    try:
        conn.execute(
            """
            UPDATE maintenance_events
            SET type=?, title=?, due_date=?, notes=?, reminder_days=?, recurrence_months=?, cost=?
            WHERE id=?
            """,
            (event_type, title, due_date or None, notes or None,
             reminder_days, recurrence_months or 0, cost, event_id),
        )
        conn.commit()
    finally:
        conn.close()


def complete_maintenance_event(event_id, completed_date, cost=None, completion_notes=None):
    conn = get_db()
    try:
        event = conn.execute(
            "SELECT * FROM maintenance_events WHERE id = ?", (event_id,)
        ).fetchone()

        conn.execute(
            """
            UPDATE maintenance_events
            SET status='completed', completed_date=?, cost=?,
                notes=CASE WHEN ? IS NOT NULL THEN ? ELSE notes END
            WHERE id=?
            """,
            (completed_date, cost, completion_notes, completion_notes, event_id),
        )

        # Auto-create next occurrence for recurring events
        if event and event['recurrence_months'] and event['due_date']:
            try:
                base = date.fromisoformat(event['due_date'])
                m = event['recurrence_months']
                total_months = base.month - 1 + m
                next_year = base.year + total_months // 12
                next_month = total_months % 12 + 1
                next_day = min(base.day, calendar.monthrange(next_year, next_month)[1])
                next_due = date(next_year, next_month, next_day).isoformat()
                conn.execute(
                    """
                    INSERT INTO maintenance_events
                        (car_id, type, title, due_date, notes, status,
                         reminder_days, recurrence_months)
                    VALUES (?, ?, ?, ?, ?, 'pending', ?, ?)
                    """,
                    (event['car_id'], event['type'], event['title'], next_due,
                     event['notes'], event['reminder_days'], event['recurrence_months']),
                )
            except Exception:
                pass  # Non bloccare il completamento se la creazione fallisce

        conn.commit()
    finally:
        conn.close()


def delete_maintenance_event(event_id):
    conn = get_db()
    try:
        conn.execute("DELETE FROM maintenance_events WHERE id = ?", (event_id,))
        conn.commit()
    finally:
        conn.close()


def refresh_overdue_status():
    """Mark pending events whose due_date has passed as overdue."""
    conn = get_db()
    try:
        conn.execute(
            """
            UPDATE maintenance_events
            SET status='overdue'
            WHERE status='pending' AND due_date IS NOT NULL AND due_date < date('now')
            """
        )
        conn.commit()
    finally:
        conn.close()


def get_upcoming_maintenance(days=60):
    conn = get_db()
    try:
        rows = conn.execute(
            """
            SELECT me.*, c.make, c.model, c.license_plate,
                   CAST((julianday(me.due_date) - julianday('now')) AS INTEGER) AS days_remaining
            FROM maintenance_events me
            JOIN cars c ON me.car_id = c.id
            WHERE me.status IN ('pending','overdue')
              AND me.due_date IS NOT NULL
              AND me.due_date <= date('now', '+' || ? || ' days')
            ORDER BY me.due_date ASC
            """,
            (days,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


# ===========================================================================
# DOCUMENTS
# ===========================================================================


def get_documents(car_id=None, doc_type=None):
    conn = get_db()
    try:
        query = """
            SELECT d.*, c.make, c.model, c.license_plate
            FROM documents d
            JOIN cars c ON d.car_id = c.id
            WHERE 1=1
        """
        params = []
        if car_id:
            query += " AND d.car_id = ?"
            params.append(car_id)
        if doc_type:
            query += " AND d.type = ?"
            params.append(doc_type)
        query += " ORDER BY d.upload_date DESC"
        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_document(doc_id):
    conn = get_db()
    try:
        row = conn.execute(
            """
            SELECT d.*, c.make, c.model
            FROM documents d
            JOIN cars c ON d.car_id = c.id
            WHERE d.id = ?
            """,
            (doc_id,),
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def create_document(car_id, doc_type, title, filename, original_name,
                    file_size=None, notes=None):
    conn = get_db()
    try:
        cur = conn.execute(
            """
            INSERT INTO documents
                (car_id, type, title, filename, original_name, file_size, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (car_id, doc_type, title, filename, original_name, file_size, notes or None),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def delete_document(doc_id):
    conn = get_db()
    try:
        conn.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
        conn.commit()
    finally:
        conn.close()


# ===========================================================================
# MALFUNCTIONS
# ===========================================================================


def get_malfunctions(car_id=None, status=None):
    conn = get_db()
    try:
        query = """
            SELECT m.*, c.make, c.model, c.license_plate
            FROM malfunctions m
            JOIN cars c ON m.car_id = c.id
            WHERE 1=1
        """
        params = []
        if car_id:
            query += " AND m.car_id = ?"
            params.append(car_id)
        if status:
            query += " AND m.status = ?"
            params.append(status)
        query += " ORDER BY m.created_at DESC"
        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_malfunction(malfunction_id):
    conn = get_db()
    try:
        row = conn.execute(
            """
            SELECT m.*, c.make, c.model, c.license_plate
            FROM malfunctions m
            JOIN cars c ON m.car_id = c.id
            WHERE m.id = ?
            """,
            (malfunction_id,),
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def create_malfunction(car_id, title, description=None, severity="medium",
                       date_reported=None):
    conn = get_db()
    try:
        if not date_reported:
            date_reported = date.today().isoformat()
        cur = conn.execute(
            """
            INSERT INTO malfunctions
                (car_id, title, description, severity, date_reported, status)
            VALUES (?, ?, ?, ?, ?, 'open')
            """,
            (car_id, title, description or None, severity, date_reported),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def update_malfunction(malfunction_id, title, description=None, severity="medium",
                       date_reported=None):
    conn = get_db()
    try:
        conn.execute(
            """
            UPDATE malfunctions
            SET title=?, description=?, severity=?, date_reported=?
            WHERE id=?
            """,
            (title, description or None, severity, date_reported, malfunction_id),
        )
        conn.commit()
    finally:
        conn.close()


def resolve_malfunction(malfunction_id, resolved_date, resolution_notes=None, cost=None):
    conn = get_db()
    try:
        conn.execute(
            """
            UPDATE malfunctions
            SET status='resolved', resolved_date=?, resolution_notes=?, cost=?
            WHERE id=?
            """,
            (resolved_date, resolution_notes or None, cost, malfunction_id),
        )
        conn.commit()
    finally:
        conn.close()


def delete_malfunction(malfunction_id):
    conn = get_db()
    try:
        conn.execute("DELETE FROM malfunctions WHERE id = ?", (malfunction_id,))
        conn.commit()
    finally:
        conn.close()


# ===========================================================================
# CONTACTS
# ===========================================================================


def get_contacts(contact_type=None):
    conn = get_db()
    try:
        query = "SELECT * FROM contacts WHERE 1=1"
        params = []
        if contact_type:
            query += " AND type = ?"
            params.append(contact_type)
        query += " ORDER BY name"
        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_contact(contact_id):
    conn = get_db()
    try:
        row = conn.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def create_contact(name, contact_type, address=None, phone=None,
                   email=None, website=None, notes=None):
    conn = get_db()
    try:
        cur = conn.execute(
            """
            INSERT INTO contacts (name, type, address, phone, email, website, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (name, contact_type, address or None, phone or None,
             email or None, website or None, notes or None),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def update_contact(contact_id, name, contact_type, address=None, phone=None,
                   email=None, website=None, notes=None):
    conn = get_db()
    try:
        conn.execute(
            """
            UPDATE contacts
            SET name=?, type=?, address=?, phone=?, email=?, website=?, notes=?
            WHERE id=?
            """,
            (name, contact_type, address or None, phone or None,
             email or None, website or None, notes or None, contact_id),
        )
        conn.commit()
    finally:
        conn.close()


def delete_contact(contact_id):
    conn = get_db()
    try:
        conn.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
        conn.commit()
    finally:
        conn.close()


# ===========================================================================
# REPORTS & DASHBOARD
# ===========================================================================


def get_dashboard_stats():
    conn = get_db()
    try:
        stats = {
            "total_cars": conn.execute("SELECT COUNT(*) FROM cars").fetchone()[0],
            "open_malfunctions": conn.execute(
                "SELECT COUNT(*) FROM malfunctions WHERE status='open'"
            ).fetchone()[0],
            "pending_maintenance": conn.execute(
                "SELECT COUNT(*) FROM maintenance_events WHERE status IN ('pending','overdue')"
            ).fetchone()[0],
            "overdue_maintenance": conn.execute(
                "SELECT COUNT(*) FROM maintenance_events WHERE status='pending' AND due_date < date('now')"
            ).fetchone()[0],
            "total_documents": conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0],
            "total_contacts": conn.execute("SELECT COUNT(*) FROM contacts").fetchone()[0],
        }
        return stats
    finally:
        conn.close()


def get_maintenance_costs_by_type(car_id=None):
    conn = get_db()
    try:
        query = """
            SELECT type, SUM(COALESCE(cost, 0)) AS total_cost, COUNT(*) AS count
            FROM maintenance_events
            WHERE status='completed'
        """
        params = []
        if car_id:
            query += " AND car_id = ?"
            params.append(car_id)
        query += " GROUP BY type ORDER BY total_cost DESC"
        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_malfunction_by_severity(car_id=None):
    conn = get_db()
    try:
        query = """
            SELECT severity, COUNT(*) AS count
            FROM malfunctions
            WHERE 1=1
        """
        params = []
        if car_id:
            query += " AND car_id = ?"
            params.append(car_id)
        query += " GROUP BY severity"
        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_monthly_costs(year=None, car_id=None):
    conn = get_db()
    try:
        if not year:
            year = datetime.now().year
        query = """
            SELECT strftime('%m', completed_date) AS month,
                   SUM(COALESCE(cost, 0)) AS total_cost
            FROM maintenance_events
            WHERE status='completed'
              AND strftime('%Y', completed_date) = ?
        """
        params = [str(year)]
        if car_id:
            query += " AND car_id = ?"
            params.append(car_id)
        query += " GROUP BY month ORDER BY month"
        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_malfunction_stats(car_id=None):
    conn = get_db()
    try:
        query = """
            SELECT
                COUNT(*) AS total,
                SUM(CASE WHEN status='open'     THEN 1 ELSE 0 END) AS open,
                SUM(CASE WHEN status='resolved' THEN 1 ELSE 0 END) AS resolved,
                COALESCE(SUM(cost), 0) AS total_cost
            FROM malfunctions
            WHERE 1=1
        """
        params = []
        if car_id:
            query += " AND car_id = ?"
            params.append(car_id)
        row = conn.execute(query, params).fetchone()
        return dict(row) if row else {}
    finally:
        conn.close()
