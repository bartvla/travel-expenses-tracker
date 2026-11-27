import os

os.environ["DATABASE_URL"] = "sqlite:///:memory:"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import database
import models
from main import app
from routers import trips

test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@event.listens_for(test_engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


TestingSessionLocal = sessionmaker(bind=test_engine)

database.engine = test_engine
database.SessionLocal = TestingSessionLocal


class FakeRedis:
    def get(self, key):
        return None

    def set(self, key, value, ex=None):
        pass

    def delete(self, key):
        pass


@pytest.fixture(autouse=True)
def setup_clean_db():
    models.Base.metadata.drop_all(bind=test_engine)
    models.Base.metadata.create_all(bind=test_engine)
    trips.cache = FakeRedis()
    yield


client = TestClient(app)

def test_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json() == {"db": "ok"}

def test_trips_crud():
    payload = {
        "name": "Lizbona 2026",
        "destination": "Portugalia",
        "start_date": "2026-04-12",
        "end_date": "2026-04-19",
        "currency": "EUR",
        "budget": "2400.00",
        "notes": "Testowa podróż",
    }
    res_create = client.post("/api/trips", json=payload)
    assert res_create.status_code == 201
    created = res_create.json()
    trip_id = created["id"]
    assert created["name"] == "Lizbona 2026"
    assert created["currency"] == "EUR"

    res_list = client.get("/api/trips")
    assert res_list.status_code == 200
    assert len(res_list.json()) == 1

    res_get = client.get(f"/api/trips/{trip_id}")
    assert res_get.status_code == 200
    assert res_get.json()["destination"] == "Portugalia"

    updated_payload = {**payload, "name": "Porto 2026", "budget": "3000.00"}
    res_put = client.put(f"/api/trips/{trip_id}", json=updated_payload)
    assert res_put.status_code == 200
    assert res_put.json()["name"] == "Porto 2026"

    res_del = client.delete(f"/api/trips/{trip_id}")
    assert res_del.status_code == 200
    assert client.get(f"/api/trips/{trip_id}").status_code == 404

def test_trip_not_found_404():
    assert client.get("/api/trips/9999").status_code == 404
    assert (
        client.put(
            "/api/trips/9999",
            json={
                "name": "Brak",
                "start_date": "2026-05-01",
                "currency": "PLN",
            },
        ).status_code
        == 404
    )
    assert client.delete("/api/trips/9999").status_code == 404


def test_trip_validation_errors():
    res_dates = client.post(
        "/api/trips",
        json={
            "name": "Złe daty",
            "start_date": "2026-05-10",
            "end_date": "2026-05-05",
            "currency": "PLN",
        },
    )
    assert res_dates.status_code == 422

    res_currency = client.post(
        "/api/trips",
        json={
            "name": "Zła waluta",
            "start_date": "2026-05-10",
            "currency": "PL",
        },
    )
    assert res_currency.status_code == 422

    res_budget = client.post(
        "/api/trips",
        json={
            "name": "Ujemny budżet",
            "start_date": "2026-05-10",
            "currency": "PLN",
            "budget": "-100.00",
        },
    )
    assert res_budget.status_code == 422

def test_expenses_crud():
    trip_res = client.post(
        "/api/trips",
        json={
            "name": "Tatry",
            "start_date": "2026-06-01",
            "currency": "PLN",
        },
    )
    trip_id = trip_res.json()["id"]

    exp_res = client.post(
        f"/api/trips/{trip_id}/expenses",
        json={
            "amount": "150.50",
            "spent_on": "2026-06-01",
            "description": "Schronisko",
        },
    )
    assert exp_res.status_code == 201
    expense_id = exp_res.json()["id"]
    assert exp_res.json()["description"] == "Schronisko"

    list_res = client.get(f"/api/trips/{trip_id}/expenses")
    assert list_res.status_code == 200
    assert len(list_res.json()) == 1

    put_res = client.put(
        f"/api/expenses/{expense_id}",
        json={
            "amount": "200.00",
            "spent_on": "2026-06-02",
            "description": "Schronisko + wyżywienie",
        },
    )
    assert put_res.status_code == 200
    assert put_res.json()["amount"] == "200.00"

    del_res = client.delete(f"/api/expenses/{expense_id}")
    assert del_res.status_code == 200
    assert client.get(f"/api/trips/{trip_id}/expenses").json() == []

def test_expenses_errors_404_and_validation():
    assert client.get("/api/trips/9999/expenses").status_code == 404
    assert (
        client.post(
            "/api/trips/9999/expenses",
            json={"amount": "50.00", "spent_on": "2026-06-01"},
        ).status_code
        == 404
    )

    assert (
        client.put(
            "/api/expenses/9999",
            json={"amount": "50.00", "spent_on": "2026-06-01"},
        ).status_code
        == 404
    )
    assert client.delete("/api/expenses/9999").status_code == 404

    trip_id = client.post(
        "/api/trips",
        json={"name": "Test", "start_date": "2026-06-01", "currency": "PLN"},
    ).json()["id"]

    res_zero = client.post(
        f"/api/trips/{trip_id}/expenses",
        json={"amount": "0.00", "spent_on": "2026-06-01"},
    )
    assert res_zero.status_code == 422

    res_negative = client.post(
        f"/api/trips/{trip_id}/expenses",
        json={"amount": "-15.00", "spent_on": "2026-06-01"},
    )
    assert res_negative.status_code == 422

def test_put_validation_and_cascade_delete():
    trip_id = client.post(
        "/api/trips",
        json={"name": "Rzym", "start_date": "2026-07-01", "currency": "EUR"},
    ).json()["id"]
    expense_id = client.post(
        f"/api/trips/{trip_id}/expenses",
        json={"amount": "100.00", "spent_on": "2026-07-01", "description": "Bilet"},
    ).json()["id"]

    assert (
        client.put(
            f"/api/trips/{trip_id}",
            json={"name": "", "start_date": "2026-07-01", "currency": "EUR"},
        ).status_code
        == 422
    )
    assert (
        client.put(
            f"/api/expenses/{expense_id}",
            json={"amount": "-5.00", "spent_on": "2026-07-01"},
        ).status_code
        == 422
    )

    assert client.delete(f"/api/trips/{trip_id}").status_code == 200
    assert (
        client.put(
            f"/api/expenses/{expense_id}",
            json={"amount": "50.00", "spent_on": "2026-07-01"},
        ).status_code   
        == 404
    )

# TODO:
# def test_history_entry_on_change():
