import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse


# ---------- Fixtures ----------


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def registered_user():
    from accounts.models import User

    return User.objects.create_user(
        email="verified@test.com",
        phone_number="09123456789",
        password="testpass123",
        username="verified1",
        is_verified=True,
    )


@pytest.fixture
def registered_client(api_client, registered_user):
    api_client.force_authenticate(user=registered_user)
    return api_client


@pytest.fixture
def registration_payload():
    return {
        "email": "newuser@test.com",
        "username": "newuser1",
        "phone_number": "09123456780",
        "password": "testpass123",
        "password1": "testpass123",
    }


# ---------- Test: POST /accounts/api/v1/register ----------


@pytest.mark.django_db
class TestRegister:
    def test_register_succeeds(self, api_client, registration_payload):
        response = api_client.post(reverse("accounts:api-v1:register"), registration_payload)
        assert response.status_code == status.HTTP_200_OK
        assert "detail" in response.data

    def test_register_returns_200(self, api_client, registration_payload):
        response = api_client.post(reverse("accounts:api-v1:register"), registration_payload)
        assert response.status_code == status.HTTP_200_OK

    def test_register_missing_email_returns_400(self, api_client):
        payload = {
            "username": "testuser",
            "phone_number": "09123456780",
            "password": "testpass123",
            "password1": "testpass123",
        }
        response = api_client.post(reverse("accounts:api-v1:register"), payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_missing_password_returns_400(self, api_client):
        payload = {
            "email": "test@test.com",
            "username": "testuser",
            "phone_number": "09123456780",
            "password1": "testpass123",
        }
        response = api_client.post(reverse("accounts:api-v1:register"), payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_password_mismatch_returns_400(self, api_client):
        payload = {
            "email": "test@test.com",
            "username": "testuser",
            "phone_number": "09123456780",
            "password": "testpass123",
            "password1": "differentpass",
        }
        response = api_client.post(reverse("accounts:api-v1:register"), payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_duplicate_email_returns_400(self, api_client, registered_user):
        payload = {
            "email": registered_user.email,
            "username": "another",
            "phone_number": "09123456780",
            "password": "testpass123",
            "password1": "testpass123",
        }
        response = api_client.post(reverse("accounts:api-v1:register"), payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_persists_user(self, api_client, registration_payload):
        api_client.post(reverse("accounts:api-v1:register"), registration_payload)
        from accounts.models import User
        assert User.objects.filter(email=registration_payload["email"]).exists()


# ---------- Test: POST /accounts/api/v1/login ----------


@pytest.mark.django_db
class TestLogin:
    def test_login_succeeds(self, api_client, registered_user):
        response = api_client.post(
            reverse("accounts:api-v1:login"),
            {"email": registered_user.email, "password": "testpass123"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert "detail" in response.data

    def test_login_returns_tokens_in_cookies(self, api_client, registered_user):
        response = api_client.post(
            reverse("accounts:api-v1:login"),
            {"email": registered_user.email, "password": "testpass123"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert "access_token" in response.cookies
        assert "refresh_token" in response.cookies

    def test_login_wrong_password_returns_error(self, api_client, registered_user):
        response = api_client.post(
            reverse("accounts:api-v1:login"),
            {"email": registered_user.email, "password": "wrongpassword"},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_nonexistent_email_returns_error(self, api_client):
        response = api_client.post(
            reverse("accounts:api-v1:login"),
            {"email": "nonexistent@test.com", "password": "testpass123"},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_unverified_user_returns_error(self, api_client):
        from accounts.models import User
        user = User.objects.create_user(
            email="unverified@test.com",
            phone_number="09123456781",
            password="testpass123",
            username="unverified1",
            is_verified=False,
        )
        response = api_client.post(
            reverse("accounts:api-v1:login"),
            {"email": user.email, "password": "testpass123"},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST


# ---------- Test: POST /accounts/api/v1/logout ----------


@pytest.mark.django_db
class TestLogout:
    def test_logout_succeeds(self, api_client):
        response = api_client.post(reverse("accounts:api-v1:logout"))
        assert response.status_code == status.HTTP_200_OK
        assert "detail" in response.data

    def test_logout_clears_cookies(self, api_client):
        response = api_client.post(reverse("accounts:api-v1:logout"))
        assert response.status_code == status.HTTP_200_OK


# ---------- Test: POST /accounts/api/v1/change-password ----------


@pytest.mark.django_db
class TestChangePassword:
    def test_anonymous_cannot_change_password(self, api_client):
        response = api_client.post(
            reverse("accounts:api-v1:change_password"),
            {
                "old_password": "testpass123",
                "new_password": "newpass123",
                "new_password1": "newpass123",
            },
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_authenticated_can_change_password(self, registered_client, registered_user):
        response = registered_client.post(
            reverse("accounts:api-v1:change_password"),
            {
                "old_password": "testpass123",
                "new_password": "newpass123",
                "new_password1": "newpass123",
            },
        )
        assert response.status_code == status.HTTP_200_OK
        registered_user.refresh_from_db()
        assert registered_user.check_password("newpass123")

    def test_wrong_old_password_returns_error(self, registered_client):
        response = registered_client.post(
            reverse("accounts:api-v1:change_password"),
            {
                "old_password": "wrongpassword",
                "new_password": "newpass123",
                "new_password1": "newpass123",
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_mismatched_new_passwords_returns_error(self, registered_client):
        response = registered_client.post(
            reverse("accounts:api-v1:change_password"),
            {
                "old_password": "testpass123",
                "new_password": "newpass123",
                "new_password1": "differentpass",
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
