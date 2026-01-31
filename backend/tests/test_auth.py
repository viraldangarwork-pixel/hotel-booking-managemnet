"""Tests for authentication endpoints."""

import pytest


class TestRegister:
    """POST /api/v1/auth/register"""

    def test_register_success(self, client, hotel):
        response = client.post("/api/v1/auth/register", json={
            "email": "newuser@test.com",
            "password": "NewUser@123",
            "full_name": "New User",
            "phone": "+1112223333",
            "role": "staff",
            "hotel_id": hotel.id,
        })
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@test.com"
        assert data["full_name"] == "New User"
        assert "hashed_password" not in data

    def test_register_duplicate_email(self, client, admin_user, hotel):
        user, _ = admin_user
        response = client.post("/api/v1/auth/register", json={
            "email": user.email,
            "password": "Test@123",
            "full_name": "Duplicate",
            "phone": "+1112223333",
            "role": "staff",
            "hotel_id": hotel.id,
        })
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]

    def test_register_missing_fields(self, client):
        response = client.post("/api/v1/auth/register", json={
            "email": "incomplete@test.com",
        })
        assert response.status_code == 422


class TestLogin:
    """POST /api/v1/auth/login"""

    def test_login_success(self, client, admin_user):
        user, password = admin_user
        response = client.post("/api/v1/auth/login", json={
            "email": user.email,
            "password": password,
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    def test_login_wrong_password(self, client, admin_user):
        user, _ = admin_user
        response = client.post("/api/v1/auth/login", json={
            "email": user.email,
            "password": "WrongPassword",
        })
        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]

    def test_login_nonexistent_email(self, client):
        response = client.post("/api/v1/auth/login", json={
            "email": "nobody@test.com",
            "password": "Test@123",
        })
        assert response.status_code == 401

    def test_login_inactive_user(self, client, db, hotel):
        from app.core.security import get_password_hash
        from app.models.user import User, UserRole

        user = User(
            email="inactive@test.com",
            hashed_password=get_password_hash("Test@123"),
            full_name="Inactive",
            role=UserRole.staff,
            hotel_id=hotel.id,
            is_active=False,
        )
        db.add(user)
        db.commit()

        response = client.post("/api/v1/auth/login", json={
            "email": "inactive@test.com",
            "password": "Test@123",
        })
        assert response.status_code == 403


class TestMe:
    """GET /api/v1/auth/me"""

    def test_get_current_user(self, client, auth_headers, admin_user):
        user, _ = admin_user
        response = client.get("/api/v1/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == user.email
        assert data["full_name"] == user.full_name

    def test_get_current_user_no_token(self, client):
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 403

    def test_get_current_user_invalid_token(self, client):
        response = client.get("/api/v1/auth/me", headers={
            "Authorization": "Bearer invalidtoken123"
        })
        assert response.status_code == 401
