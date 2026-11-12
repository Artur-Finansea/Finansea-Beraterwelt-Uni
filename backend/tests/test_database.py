from datetime import date, datetime, timezone
from pathlib import Path
import sys

import pytest
from sqlalchemy import inspect, text
from werkzeug.security import generate_password_hash


BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app import Consultation, Customer, Task, User, create_app, db


@pytest.fixture
def app():
    return create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "DATABASE_PATH": None,
    })


def test_existing_status_endpoint_remains_available(app):
    response = app.test_client().get("/api/status")

    assert response.status_code == 200
    assert response.get_json() == {
        "projekt": "Finansea-Beraterwelt",
        "status": "Backend läuft erfolgreich",
        "version": "1.0",
    }


def test_init_db_creates_all_tables_and_enables_foreign_keys(app):
    result = app.test_cli_runner().invoke(args=["init-db"])

    assert result.exit_code == 0
    assert "Datenbanktabellen wurden angelegt" in result.output

    with app.app_context():
        table_names = set(inspect(db.engine).get_table_names())
        foreign_keys_enabled = db.session.execute(
            text("PRAGMA foreign_keys")
        ).scalar_one()

    assert table_names == {"consultations", "customers", "tasks", "users"}
    assert foreign_keys_enabled == 1


def test_model_relationships_and_optional_customer_task(app):
    fictional_password = "NurFuerDenFiktivenTest-42!"

    with app.app_context():
        db.create_all()

        admin = User(
            full_name="Ada Beispiel",
            email="ada.admin@example.invalid",
            password_hash=generate_password_hash(fictional_password),
            role="admin",
        )
        advisor = User(
            full_name="Bert Beratung",
            email="bert.berater@example.invalid",
            password_hash=generate_password_hash(fictional_password),
            role="berater",
        )
        customer = Customer(
            first_name="Clara",
            last_name="Fiktiv",
            email="clara.kunde@example.invalid",
            phone="+49 000 000000",
            advisor=advisor,
        )
        consultation = Consultation(
            customer=customer,
            advisor=advisor,
            consultation_type="Erstgespräch",
            meeting_at=datetime(2030, 1, 15, 10, 0, tzinfo=timezone.utc),
            subject="Fiktives Erstgespräch",
            notes="Ausschließlich fiktive Testnotiz.",
            status="geplant",
        )
        customer_task = Task(
            title="Fiktive Unterlagen prüfen",
            description="Testaufgabe ohne reale Kundendaten.",
            due_date=date(2030, 1, 20),
            status="offen",
            priority="mittel",
            assignee=advisor,
            creator=admin,
            customer=customer,
        )
        general_task = Task(
            title="Fiktive interne Aufgabe",
            status="offen",
            priority="niedrig",
            assignee=advisor,
            creator=admin,
        )

        db.session.add_all([
            admin,
            advisor,
            customer,
            consultation,
            customer_task,
            general_task,
        ])
        db.session.commit()

        assert customer.advisor is advisor
        assert customer in advisor.customers
        assert consultation.customer is customer
        assert consultation.advisor is advisor
        assert customer_task.assignee is advisor
        assert customer_task.creator is admin
        assert customer_task.customer is customer
        assert general_task.customer is None
        assert customer_task in customer.tasks
        assert advisor.password_hash != fictional_password
        assert advisor.created_at is not None


def test_init_db_is_repeatable_and_preserves_existing_rows(app):
    runner = app.test_cli_runner()
    first_result = runner.invoke(args=["init-db"])

    assert first_result.exit_code == 0

    with app.app_context():
        user = User(
            full_name="Dora Datenbanktest",
            email="dora.test@example.invalid",
            password_hash=generate_password_hash("FiktivUndNichtGespeichert-42!"),
            role="berater",
        )
        db.session.add(user)
        db.session.commit()

    second_result = runner.invoke(args=["init-db"])

    assert second_result.exit_code == 0
    with app.app_context():
        assert db.session.scalar(
            db.select(db.func.count(User.id))
        ) == 1
