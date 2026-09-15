from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_duplicate_reservation_is_rejected():
    first_response = client.post(
        "/reservations",
        json={
            "user_id": 1,
            "event_id": 1,
            "seat_id": 1
        }
    )

    second_response = client.post(
        "/reservations",
        json={
            "user_id": 1,
            "event_id": 1,
            "seat_id": 1
        }
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 400
    assert second_response.json() == {
        "detail": "Seat is already reserved"
    }