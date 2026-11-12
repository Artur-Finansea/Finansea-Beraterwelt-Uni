import os
import sqlite3
from pathlib import Path

import click
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.engine import Engine


db = SQLAlchemy()


@event.listens_for(Engine, "connect")
def enable_sqlite_foreign_keys(dbapi_connection, _connection_record):
    """Aktiviert die Fremdschlüsselprüfung für jede SQLite-Verbindung."""
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


class User(db.Model):
    __tablename__ = "users"
    __table_args__ = (
        db.CheckConstraint(
            "role IN ('admin', 'berater')",
            name="ck_users_role",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="berater")
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        server_default=db.func.now(),
    )

    customers = db.relationship(
        "Customer",
        foreign_keys="Customer.advisor_id",
        back_populates="advisor",
    )
    consultations = db.relationship(
        "Consultation",
        foreign_keys="Consultation.advisor_id",
        back_populates="advisor",
    )
    assigned_tasks = db.relationship(
        "Task",
        foreign_keys="Task.assigned_to",
        back_populates="assignee",
    )
    created_tasks = db.relationship(
        "Task",
        foreign_keys="Task.created_by",
        back_populates="creator",
    )


class Customer(db.Model):
    __tablename__ = "customers"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255))
    phone = db.Column(db.String(50))
    advisor_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    is_archived = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        server_default=db.func.now(),
    )

    advisor = db.relationship(
        "User",
        foreign_keys=[advisor_id],
        back_populates="customers",
    )
    consultations = db.relationship(
        "Consultation",
        back_populates="customer",
    )
    tasks = db.relationship(
        "Task",
        back_populates="customer",
        passive_deletes=True,
    )


class Consultation(db.Model):
    __tablename__ = "consultations"
    __table_args__ = (
        db.CheckConstraint(
            "consultation_type IN ('Erstgespräch', 'Beratung')",
            name="ck_consultations_type",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(
        db.Integer,
        db.ForeignKey("customers.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    advisor_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    consultation_type = db.Column(db.String(30), nullable=False)
    meeting_at = db.Column(db.DateTime(timezone=True), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    notes = db.Column(db.Text)
    status = db.Column(db.String(50), nullable=False, default="geplant")
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        server_default=db.func.now(),
    )

    customer = db.relationship(
        "Customer",
        foreign_keys=[customer_id],
        back_populates="consultations",
    )
    advisor = db.relationship(
        "User",
        foreign_keys=[advisor_id],
        back_populates="consultations",
    )


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.Date)
    status = db.Column(db.String(50), nullable=False, default="offen")
    priority = db.Column(db.String(20), nullable=False, default="mittel")
    assigned_to = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    created_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    customer_id = db.Column(
        db.Integer,
        db.ForeignKey("customers.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        server_default=db.func.now(),
    )

    assignee = db.relationship(
        "User",
        foreign_keys=[assigned_to],
        back_populates="assigned_tasks",
    )
    creator = db.relationship(
        "User",
        foreign_keys=[created_by],
        back_populates="created_tasks",
    )
    customer = db.relationship(
        "Customer",
        foreign_keys=[customer_id],
        back_populates="tasks",
    )


def create_app(test_config=None):
    backend_directory = Path(__file__).resolve().parent
    instance_directory = backend_directory / "instance"
    app = Flask(
        __name__,
        instance_path=str(instance_directory),
        instance_relative_config=True,
    )
    database_path = instance_directory / "finansea.db"

    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{database_path.as_posix()}",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        DATABASE_PATH=str(database_path),
    )

    if test_config:
        app.config.update(test_config)

    db.init_app(app)

    @app.route("/")
    def home():
        return "Willkommen bei der Finansea-Beraterwelt!"

    @app.route("/api/status")
    def status():
        return jsonify({
            "projekt": "Finansea-Beraterwelt",
            "status": "Backend läuft erfolgreich",
            "version": "1.0",
        })

    @app.cli.command("init-db")
    def init_db_command():
        """Legt fehlende Datenbanktabellen an, ohne vorhandene Daten zu löschen."""
        configured_path = app.config.get("DATABASE_PATH")
        if configured_path:
            Path(configured_path).parent.mkdir(parents=True, exist_ok=True)

        db.create_all()
        click.echo("Datenbanktabellen wurden angelegt oder waren bereits vorhanden.")

    return app


app = create_app()


if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
    app.run(debug=debug_mode)
