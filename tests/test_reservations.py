from calendar import firstweekday

import pytest
import uuid
from fastapi.testclient import TestClient

from app.main import app
from app.database import SessionLocal
from app import models
from sqlalchemy import select


client = TestClient(app)

@pytest.fixture
def test_user():
    db = SessionLocal()

    user = models.User(
        name="Test User",
        email = f"testuser-{uuid.uuid4()}@example.com"
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    user_id = user.id

    yield user

    db.query(models.Reservation).filter(
        models.Reservation.user_id == user_id
    ).delete()

    db.query(models.User).filter(
        models.User.id == user_id
    ).delete()

    db.commit()
    db.close()

@pytest.fixture
def test_venue():
    db = SessionLocal()

    venue = models.Venue(
        name = "Test Venue",
        address = "123 Test Street"
    )

    db.add(venue)
    db.commit()
    db.refresh(venue)

    venue_id = venue.id

    yield venue

    db.query(models.Venue).filter(
        models.Venue.id == venue_id
    ).delete()

    db.commit()
    db.close()

@pytest.fixture
def test_event(test_venue):
    db = SessionLocal()

    event =models.Event(
        name = "Test Event",
        venue_id = test_venue.id
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    event_id = event.id

    yield event

    db.query(models.Event).filter(
        models.Event.id == event_id
    ).delete()

    db.commit()
    db.close()

@pytest.fixture
def test_seat(test_event):
    db = SessionLocal()

    seat = models.Seat(
        section = "101",
        row = "A",
        number = 1,
        event_id = test_event.id
    )

    db.add(seat)
    db.commit()
    db.refresh(seat)

    seat_id = seat.id

    yield seat

    db.query(models.Reservation).filter(
        models.Reservation.seat_id == seat_id
    ).delete()

    db.query(models.Seat).filter(
        models.Seat.id == seat_id
    ).delete()

    db.commit()
    db.close()

@pytest.fixture
def second_event(test_venue):
    db = SessionLocal()

    event = models.Event(
        name="Second Test Event",
        venue_id = test_venue.id
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    event_id = event.id

    yield event

    db.query(models.Event).filter(
        models.Event.id == event_id
    ).delete()

    db.commit()
    db.close()

@pytest.fixture
def second_event_seat(second_event):
    db = SessionLocal()

    seat = models.Seat(
        section = "202",
        row = "B",
        number = 2,
        event_id = second_event.id
    )

    db.add(seat)
    db.commit()
    db.refresh(seat)

    seat_id = seat.id

    yield seat

    db.query(models.Reservation).filter(
        models.Reservation.seat_id == seat_id
    ).delete()

    db.query(models.Seat).filter(
        models.Seat.id == seat_id
    ).delete()

    db.commit()
    db.close()

def test_duplicate_reservation_is_rejected(
        test_user,
        test_event,
        test_seat
):
    first_response = client.post(
        "/reservations",
        json={
            "user_id": test_user.id,
            "event_id": test_event.id,
            "seat_id": test_seat.id
        }
    )

    second_response = client.post(
        "/reservations",
        json={
            "user_id": test_user.id,
            "event_id": test_event.id,
            "seat_id": test_seat.id
        }
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 400
    assert second_response.json() == {
        "detail": "Seat is already reserved"
    }

def test_reservation_with_nonexistent_user_is_rejected(
        test_event,
        test_seat
):
    response = client.post(
        "/reservations",
        json={
            "user_id": 999999,
            "event_id": test_event.id,
            "seat_id": test_seat.id
        }
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "User not found"
    }

def test_reservation_with_nonexistent_event_is_rejected(
        test_user,
        test_seat
):
    response = client.post(
        "/reservations",
        json ={
            "user_id": test_user.id,
            "event_id": 999999,
            "seat_id": test_seat.id
        }
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Event not found"
    }

def test_reservation_with_non_existent_seat_is_rejected(
        test_user,
        test_event
):
    response = client.post(
        "/reservations",
        json = {
            "user_id": test_user.id,
            "event_id": test_event.id,
            "seat_id": 999999
        }
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Seat not found"
    }

def test_reservation_with_seat_from_wrong_event_is_rejected(
        test_user,
        test_event,
        second_event_seat
):
    response = client.post(
        "/reservations",
        json={
            "user_id": test_user.id,
            "event_id": test_event.id,
            "seat_id": second_event_seat.id
        }
    )

    assert response.status_code ==400
    assert response.json() == {
        "detail": "Seat does not belong to this event"
    }

def test_get_user_returns_user(test_user):
    response = client.get(f"/users/{test_user.id}")

    assert response.status_code == 200
    assert response.json() == {
        "id": test_user.id,
        "name": test_user.name,
        "email": test_user.email
    }

def test_get_nonexistent_user_returns_404():
    db = SessionLocal()

    max_id = (
        db.query(models.User.id)
        .order_by(models.User.id.desc())
        .first()
    )

    db.close()

    non_existent_id = 1 if max_id is None else max_id[0] + 1

    response = client.get(f"/users/{non_existent_id}")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "User not found"
    }

def test_get_reservation_returns_reservation(
        test_user,
        test_event,
        test_seat
):
    create_response = client.post(
        "/reservations",
        json = {
            "user_id": test_user.id,
            "event_id": test_event.id,
            "seat_id": test_seat.id
        }
    )

    assert create_response.status_code == 200

    reservation_id = create_response.json()["id"]

    get_response = client.get(
        f"/reservations/{reservation_id}"
    )

    assert get_response.status_code == 200
    assert get_response.json() == {
        "id": reservation_id,
        "user_id": test_user.id,
        "event_id": test_event.id,
        "seat_id": test_seat.id
    }

def test_get_nonexistent_reservation_returns_404():
    db = SessionLocal()

    max_id = (db.query(models.Reservation.id)
                       .order_by(models.Reservation.id.desc())
                       .first()
                       )

    db.close()

    non_existent_id = 1 if max_id is None else max_id[0] + 1

    response = client.get(f"/reservations/{non_existent_id}")

    assert response.status_code == 404
    assert response.json() =={
        "detail": "Reservation not found"
    }

def test_get_user_reservations_returns_reservations(
        test_user,
        test_event,
        test_seat
):
    create_response = client.post(
        "/reservations",
        json = {
            "user_id": test_user.id,
            "event_id": test_event.id,
            "seat_id": test_seat.id
        }
    )

    assert create_response.status_code == 200

    response = client.get(
        f"/users/{test_user.id}/reservations"
    )

    print(response.status_code)
    print(response.json())

    assert response.status_code == 200

    reservations = response.json()

    assert len(reservations) == 1
    assert reservations[0] == {
        "id": create_response.json()["id"],
        "user_id": test_user.id,
        "event_id": test_event.id,
        "seat_id": test_seat.id

    }

def test_get_reservations_for_nonexistent_user_returns_404():
    db = SessionLocal()

    max_id = db.scalar(
        select(models.User.id)
        .order_by(models.User.id.desc())
        .limit(1)
    )

    db.close()

    non_existent_id = 1 if max_id is None else max_id + 1

    response = client.get(f"/users/{non_existent_id}/reservations")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "User not found"
    }