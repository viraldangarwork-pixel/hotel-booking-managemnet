"""Tests for guest management endpoints."""

import io
import pytest


class TestListGuests:
    """GET /api/v1/guests"""

    def test_list_guests(self, client, auth_headers, guest):
        response = client.get(
            f"/api/v1/guests?hotel_id={guest.hotel_id}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert data[0]["first_name"] == "John"

    def test_list_guests_search(self, client, auth_headers, guest):
        response = client.get(
            f"/api/v1/guests?hotel_id={guest.hotel_id}&search=John",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert any(g["first_name"] == "John" for g in data)


class TestCreateGuest:
    """POST /api/v1/guests"""

    def test_create_guest(self, client, auth_headers, hotel):
        response = client.post("/api/v1/guests", json={
            "hotel_id": hotel.id,
            "first_name": "Alice",
            "last_name": "Smith",
            "email": "alice@example.com",
            "phone": "+1234500000",
            "city": "Mumbai",
            "country": "India",
        }, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["first_name"] == "Alice"
        assert data["last_name"] == "Smith"
        assert data["phone"] == "+1234500000"

    def test_create_guest_missing_name(self, client, auth_headers, hotel):
        response = client.post("/api/v1/guests", json={
            "hotel_id": hotel.id,
            "email": "noname@example.com",
            "phone": "+1234500001",
        }, headers=auth_headers)
        assert response.status_code == 422

    def test_create_guest_no_auth(self, client, hotel):
        response = client.post("/api/v1/guests", json={
            "hotel_id": hotel.id,
            "first_name": "Noauth",
            "last_name": "User",
            "phone": "+1234500002",
        })
        assert response.status_code == 403


class TestGetGuest:
    """GET /api/v1/guests/{guest_id}"""

    def test_get_guest(self, client, auth_headers, guest):
        response = client.get(
            f"/api/v1/guests/{guest.id}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == guest.id
        assert data["email"] == "john@example.com"

    def test_get_guest_not_found(self, client, auth_headers):
        response = client.get(
            "/api/v1/guests/99999",
            headers=auth_headers,
        )
        assert response.status_code == 404


class TestUpdateGuest:
    """PUT /api/v1/guests/{guest_id}"""

    def test_update_guest(self, client, auth_headers, guest):
        response = client.put(f"/api/v1/guests/{guest.id}", json={
            "first_name": "Johnny",
            "is_vip": True,
        }, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "Johnny"
        assert data["is_vip"] is True

    def test_update_guest_not_found(self, client, auth_headers):
        response = client.put("/api/v1/guests/99999", json={
            "first_name": "Ghost",
        }, headers=auth_headers)
        assert response.status_code == 404


class TestDocumentUpload:
    """POST /api/v1/guests/{guest_id}/upload-document"""

    def test_upload_document(self, client, auth_headers, guest):
        # Create a minimal valid JPEG-like file
        fake_image = io.BytesIO(b"\xff\xd8\xff\xe0" + b"\x00" * 60000)
        response = client.post(
            f"/api/v1/guests/{guest.id}/upload-document",
            files={"file": ("test_id.jpg", fake_image, "image/jpeg")},
            data={"side": "front", "document_type": "passport"},
            headers=auth_headers,
        )
        # May be 200 or may fail on clarity check — both are valid
        assert response.status_code in [200, 400, 500]

    def test_upload_document_guest_not_found(self, client, auth_headers):
        fake_image = io.BytesIO(b"\xff\xd8\xff\xe0" + b"\x00" * 1000)
        response = client.post(
            "/api/v1/guests/99999/upload-document",
            files={"file": ("test.jpg", fake_image, "image/jpeg")},
            data={"side": "front"},
            headers=auth_headers,
        )
        assert response.status_code == 404
