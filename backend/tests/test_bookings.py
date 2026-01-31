"""Tests for booking management endpoints."""

import pytest
from datetime import date, timedelta


def _future(days=1):
    return (date.today() + timedelta(days=days)).isoformat()


class TestListBookings:
    """GET /api/v1/bookings"""

    def test_list_bookings_empty(self, client, auth_headers, hotel):
        response = client.get(
            f"/api/v1/bookings?hotel_id={hotel.id}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json() == []


class TestCreateBooking:
    """POST /api/v1/bookings"""

    def test_create_booking(self, client, auth_headers, hotel, room, guest):
        response = client.post("/api/v1/bookings", json={
            "hotel_id": hotel.id,
            "room_id": room.id,
            "guest_id": guest.id,
            "check_in_date": _future(1),
            "check_out_date": _future(3),
            "adults": 2,
            "children": 0,
            "extra_beds": 0,
            "source": "direct",
        }, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["guest_id"] == guest.id
        assert data["room_id"] == room.id
        assert data["status"] == "pending"
        assert "booking_ref" in data
        assert float(data["total_amount"]) > 0

    def test_create_booking_checkout_before_checkin(self, client, auth_headers, hotel, room, guest):
        response = client.post("/api/v1/bookings", json={
            "hotel_id": hotel.id,
            "room_id": room.id,
            "guest_id": guest.id,
            "check_in_date": _future(5),
            "check_out_date": _future(2),
            "adults": 1,
        }, headers=auth_headers)
        assert response.status_code == 400
        assert "after check-in" in response.json()["detail"].lower()

    def test_create_booking_same_dates(self, client, auth_headers, hotel, room, guest):
        d = _future(1)
        response = client.post("/api/v1/bookings", json={
            "hotel_id": hotel.id,
            "room_id": room.id,
            "guest_id": guest.id,
            "check_in_date": d,
            "check_out_date": d,
            "adults": 1,
        }, headers=auth_headers)
        assert response.status_code == 400

    def test_create_booking_overlapping(self, client, auth_headers, hotel, room, guest):
        # First booking
        client.post("/api/v1/bookings", json={
            "hotel_id": hotel.id,
            "room_id": room.id,
            "guest_id": guest.id,
            "check_in_date": _future(10),
            "check_out_date": _future(15),
            "adults": 1,
        }, headers=auth_headers)

        # Overlapping booking
        response = client.post("/api/v1/bookings", json={
            "hotel_id": hotel.id,
            "room_id": room.id,
            "guest_id": guest.id,
            "check_in_date": _future(12),
            "check_out_date": _future(17),
            "adults": 1,
        }, headers=auth_headers)
        assert response.status_code == 400
        assert "not available" in response.json()["detail"].lower()

    def test_create_booking_invalid_room(self, client, auth_headers, hotel, guest):
        response = client.post("/api/v1/bookings", json={
            "hotel_id": hotel.id,
            "room_id": 99999,
            "guest_id": guest.id,
            "check_in_date": _future(1),
            "check_out_date": _future(3),
            "adults": 1,
        }, headers=auth_headers)
        assert response.status_code == 404

    def test_create_booking_no_auth(self, client, hotel, room, guest):
        response = client.post("/api/v1/bookings", json={
            "hotel_id": hotel.id,
            "room_id": room.id,
            "guest_id": guest.id,
            "check_in_date": _future(1),
            "check_out_date": _future(3),
            "adults": 1,
        })
        assert response.status_code == 403


class TestGetBooking:
    """GET /api/v1/bookings/{booking_id}"""

    def test_get_booking(self, client, auth_headers, hotel, room, guest):
        create = client.post("/api/v1/bookings", json={
            "hotel_id": hotel.id,
            "room_id": room.id,
            "guest_id": guest.id,
            "check_in_date": _future(1),
            "check_out_date": _future(3),
            "adults": 1,
        }, headers=auth_headers)
        booking_id = create.json()["id"]

        response = client.get(f"/api/v1/bookings/{booking_id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["id"] == booking_id

    def test_get_booking_not_found(self, client, auth_headers):
        response = client.get("/api/v1/bookings/99999", headers=auth_headers)
        assert response.status_code == 404


class TestCheckIn:
    """POST /api/v1/bookings/{booking_id}/check-in"""

    def test_check_in(self, client, auth_headers, hotel, room, guest):
        create = client.post("/api/v1/bookings", json={
            "hotel_id": hotel.id,
            "room_id": room.id,
            "guest_id": guest.id,
            "check_in_date": date.today().isoformat(),
            "check_out_date": _future(2),
            "adults": 1,
        }, headers=auth_headers)
        booking_id = create.json()["id"]

        response = client.post(
            f"/api/v1/bookings/{booking_id}/check-in",
            json={},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["status"] == "checked_in"
        assert response.json()["actual_check_in"] is not None

    def test_check_in_already_checked_in(self, client, auth_headers, hotel, room, guest):
        create = client.post("/api/v1/bookings", json={
            "hotel_id": hotel.id,
            "room_id": room.id,
            "guest_id": guest.id,
            "check_in_date": date.today().isoformat(),
            "check_out_date": _future(2),
            "adults": 1,
        }, headers=auth_headers)
        booking_id = create.json()["id"]

        # First check-in
        client.post(f"/api/v1/bookings/{booking_id}/check-in", json={}, headers=auth_headers)

        # Duplicate check-in
        response = client.post(f"/api/v1/bookings/{booking_id}/check-in", json={}, headers=auth_headers)
        assert response.status_code == 400


class TestCheckOut:
    """POST /api/v1/bookings/{booking_id}/check-out"""

    def test_check_out(self, client, auth_headers, hotel, room, guest):
        create = client.post("/api/v1/bookings", json={
            "hotel_id": hotel.id,
            "room_id": room.id,
            "guest_id": guest.id,
            "check_in_date": date.today().isoformat(),
            "check_out_date": _future(2),
            "adults": 1,
        }, headers=auth_headers)
        booking_id = create.json()["id"]

        # Check in first
        client.post(f"/api/v1/bookings/{booking_id}/check-in", json={}, headers=auth_headers)

        # Check out
        response = client.post(
            f"/api/v1/bookings/{booking_id}/check-out",
            json={},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["status"] == "checked_out"
        assert response.json()["actual_check_out"] is not None

    def test_check_out_not_checked_in(self, client, auth_headers, hotel, room, guest):
        create = client.post("/api/v1/bookings", json={
            "hotel_id": hotel.id,
            "room_id": room.id,
            "guest_id": guest.id,
            "check_in_date": _future(1),
            "check_out_date": _future(3),
            "adults": 1,
        }, headers=auth_headers)
        booking_id = create.json()["id"]

        response = client.post(f"/api/v1/bookings/{booking_id}/check-out", json={}, headers=auth_headers)
        assert response.status_code == 400


class TestCancelBooking:
    """POST /api/v1/bookings/{booking_id}/cancel"""

    def test_cancel_booking(self, client, auth_headers, hotel, room, guest):
        create = client.post("/api/v1/bookings", json={
            "hotel_id": hotel.id,
            "room_id": room.id,
            "guest_id": guest.id,
            "check_in_date": _future(5),
            "check_out_date": _future(7),
            "adults": 1,
        }, headers=auth_headers)
        booking_id = create.json()["id"]

        response = client.post(
            f"/api/v1/bookings/{booking_id}/cancel?reason=Changed+plans",
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["status"] == "cancelled"

    def test_cancel_already_cancelled(self, client, auth_headers, hotel, room, guest):
        create = client.post("/api/v1/bookings", json={
            "hotel_id": hotel.id,
            "room_id": room.id,
            "guest_id": guest.id,
            "check_in_date": _future(5),
            "check_out_date": _future(7),
            "adults": 1,
        }, headers=auth_headers)
        booking_id = create.json()["id"]

        client.post(f"/api/v1/bookings/{booking_id}/cancel", headers=auth_headers)
        response = client.post(f"/api/v1/bookings/{booking_id}/cancel", headers=auth_headers)
        assert response.status_code == 400
