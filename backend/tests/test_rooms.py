"""Tests for room management endpoints."""

import pytest


class TestListRooms:
    """GET /api/v1/rooms"""

    def test_list_rooms(self, client, auth_headers, room):
        response = client.get(
            f"/api/v1/rooms?hotel_id={room.hotel_id}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert data[0]["room_number"] == "101"

    def test_list_rooms_filter_by_status(self, client, auth_headers, room):
        response = client.get(
            f"/api/v1/rooms?hotel_id={room.hotel_id}&status=available",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert all(r["status"] == "available" for r in data)

    def test_list_rooms_no_auth(self, client, room):
        response = client.get(f"/api/v1/rooms?hotel_id={room.hotel_id}")
        assert response.status_code == 403


class TestCreateRoom:
    """POST /api/v1/rooms"""

    def test_create_room(self, client, auth_headers, hotel, room_type):
        response = client.post("/api/v1/rooms", json={
            "hotel_id": hotel.id,
            "room_type_id": room_type.id,
            "room_number": "202",
            "floor": 2,
        }, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["room_number"] == "202"
        assert data["floor"] == 2
        assert data["status"] == "available"

    def test_create_room_duplicate_number(self, client, auth_headers, room, hotel, room_type):
        response = client.post("/api/v1/rooms", json={
            "hotel_id": hotel.id,
            "room_type_id": room_type.id,
            "room_number": "101",  # already exists
            "floor": 1,
        }, headers=auth_headers)
        assert response.status_code in [400, 409, 500]

    def test_create_room_missing_fields(self, client, auth_headers):
        response = client.post("/api/v1/rooms", json={
            "room_number": "999",
        }, headers=auth_headers)
        assert response.status_code == 422


class TestUpdateRoomStatus:
    """PUT /api/v1/rooms/{room_id}/status"""

    def test_update_room_status(self, client, auth_headers, room):
        response = client.put(
            f"/api/v1/rooms/{room.id}/status?status=maintenance",
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["status"] == "maintenance"

    def test_update_room_status_not_found(self, client, auth_headers):
        response = client.put(
            "/api/v1/rooms/99999/status?status=available",
            headers=auth_headers,
        )
        assert response.status_code == 404


class TestRoomTypes:
    """GET /api/v1/rooms/types"""

    def test_list_room_types(self, client, auth_headers, room_type):
        response = client.get(
            f"/api/v1/rooms/types?hotel_id={room_type.hotel_id}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert data[0]["name"] == "Standard"
        assert float(data[0]["base_price"]) == 100.0
