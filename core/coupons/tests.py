import pytest
from datetime import timedelta
from decimal import Decimal
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from django.utils import timezone
from coupons.models import Coupon, UserCoupon


# ---------- Fixtures ----------


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def verified_user():
    from accounts.models import User

    return User.objects.create_user(
        email="verified@test.com",
        phone_number="09123456789",
        password="testpass123",
        username="verified1",
        is_verified=True,
    )


@pytest.fixture
def verified_client(api_client, verified_user):
    api_client.force_authenticate(user=verified_user)
    return api_client


@pytest.fixture
def staff_user():
    from accounts.models import User

    return User.objects.create_user(
        email="staff@test.com",
        phone_number="09123456780",
        password="testpass123",
        username="staff1",
        is_verified=True,
        is_staff=True,
    )


@pytest.fixture
def staff_client(api_client, staff_user):
    api_client.force_authenticate(user=staff_user)
    return api_client


@pytest.fixture
def active_coupon():
    return Coupon.objects.create(
        code="SAVE20",
        discount_percent=Decimal("5.00"),
        expiration_date=timezone.now() + timedelta(days=30),
        max_global_usage=10,
        is_general=True,
    )


@pytest.fixture
def expired_coupon():
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO coupons_coupon (code, discount_percent, expiration_date, max_global_usage, current_usages, max_usage_per_user, is_general, created_date, updated_date) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW()) RETURNING id",
            ("OLD20", "5.00", timezone.now() - timedelta(days=1), 10, 0, 1, True),
        )
        pk = cursor.fetchone()[0]
    return Coupon.objects.get(pk=pk)


@pytest.fixture
def fully_used_coupon():
    coupon = Coupon.objects.create(
        code="FULL05",
        discount_percent=Decimal("5.00"),
        expiration_date=timezone.now() + timedelta(days=30),
        max_global_usage=1,
        is_general=True,
    )
    Coupon.objects.filter(pk=coupon.pk).update(current_usages=1)
    coupon.refresh_from_db()
    return coupon


@pytest.fixture
def assigned_coupon(verified_user):
    coupon = Coupon.objects.create(
        code="PERSONAL5",
        discount_percent=Decimal("5.00"),
        expiration_date=timezone.now() + timedelta(days=30),
        max_global_usage=5,
        is_general=False,
    )
    UserCoupon.objects.create(user=verified_user, coupon=coupon)
    return coupon


# ---------- Test: Coupon Model ----------


@pytest.mark.django_db
class TestCouponModel:
    def test_is_valid_active_coupon(self, active_coupon):
        assert active_coupon.is_valid() is True

    def test_is_valid_expired_coupon(self, expired_coupon):
        assert expired_coupon.is_valid() is False

    def test_is_valid_fully_used_coupon(self, fully_used_coupon):
        assert fully_used_coupon.is_valid() is False

    def test_redeem_increments_usage(self, active_coupon):
        active_coupon.redeem()
        active_coupon.refresh_from_db()
        assert active_coupon.current_usages == 1

    def test_redeem_at_limit_raises(self, fully_used_coupon):
        from django.core.exceptions import ValidationError

        with pytest.raises(ValidationError):
            fully_used_coupon.redeem()


# ---------- Test: UserCoupon Model ----------


@pytest.mark.django_db
class TestUserCouponModel:
    def test_assign_welcome_coupon(self, verified_user):
        user_coupon = UserCoupon.objects.assign_unique_welcome_coupon(verified_user)
        assert user_coupon.user == verified_user
        assert user_coupon.is_used is False

    def test_welcome_coupon_expires_in_30_days(self, verified_user):
        user_coupon = UserCoupon.objects.assign_unique_welcome_coupon(verified_user)
        expected = timezone.now() + timedelta(days=30)
        diff = user_coupon.coupon.expiration_date - expected
        assert abs(diff.total_seconds()) < 60


# ---------- Test: CouponManager ----------


@pytest.mark.django_db
class TestCouponManager:
    def test_find_active_coupon(self, active_coupon):
        found = Coupon.objects.find_active_coupon("SAVE20")
        assert found == active_coupon

    def test_find_active_coupon_expired(self, expired_coupon):
        found = Coupon.objects.find_active_coupon("OLD20")
        assert found is None

    def test_find_active_coupon_nonexistent(self):
        found = Coupon.objects.find_active_coupon("DOESNOTEXIST")
        assert found is None

    def test_get_all_active_coupons(self, active_coupon, expired_coupon, fully_used_coupon):
        active = Coupon.objects.get_all_active_coupons()
        assert active_coupon in active
        assert expired_coupon not in active
        assert fully_used_coupon not in active


# ---------- Test: GET /api/v1/coupons/ ----------


@pytest.mark.django_db
class TestCouponList:
    def test_anonymous_cannot_list(self, api_client):
        response = api_client.get(reverse("coupons:coupon-list"))
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unverified_user_cannot_list(self, api_client):
        from accounts.models import User

        user = User.objects.create_user(
            email="unverified@test.com",
            phone_number="09123456781",
            password="testpass123",
            username="unverified1",
            is_verified=False,
        )
        api_client.force_authenticate(user=user)
        response = api_client.get(reverse("coupons:coupon-list"))
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_verified_user_can_list(self, verified_client, active_coupon):
        response = verified_client.get(reverse("coupons:coupon-list"))
        assert response.status_code == status.HTTP_200_OK

    def test_list_returns_active_general_coupons(self, verified_client, active_coupon):
        response = verified_client.get(reverse("coupons:coupon-list"))
        codes = [c["code"] for c in response.data]
        assert "SAVE20" in codes

    def test_list_excludes_expired(self, verified_client, expired_coupon):
        response = verified_client.get(reverse("coupons:coupon-list"))
        codes = [c["code"] for c in response.data]
        assert "OLD20" not in codes

    def test_list_excludes_assigned_non_general(self, verified_client, assigned_coupon):
        response = verified_client.get(reverse("coupons:coupon-list"))
        codes = [c["code"] for c in response.data]
        assert "PERSONAL5" in codes


# ---------- Test: GET /api/v1/coupons/{pk}/ ----------


@pytest.mark.django_db
class TestCouponDetail:
    def test_anonymous_cannot_retrieve(self, api_client, active_coupon):
        response = api_client.get(reverse("coupons:coupon-detail", kwargs={"pk": active_coupon.pk}))
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_verified_user_can_retrieve(self, verified_client, active_coupon):
        response = verified_client.get(reverse("coupons:coupon-detail", kwargs={"pk": active_coupon.pk}))
        assert response.status_code == status.HTTP_200_OK

    def test_retrieve_returns_expected_keys(self, verified_client, active_coupon):
        response = verified_client.get(reverse("coupons:coupon-detail", kwargs={"pk": active_coupon.pk}))
        expected_keys = {"id", "code", "discount_percent", "expiration_date",
                         "max_global_usage", "current_usages", "max_usage_per_user",
                         "is_general", "is_valid_coupon"}
        assert set(response.data.keys()) == expected_keys

    def test_retrieve_nonexistent_returns_404(self, verified_client):
        response = verified_client.get(reverse("coupons:coupon-detail", kwargs={"pk": 9999}))
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_is_valid_coupon_field_active(self, verified_client, active_coupon):
        response = verified_client.get(reverse("coupons:coupon-detail", kwargs={"pk": active_coupon.pk}))
        assert response.data["is_valid_coupon"] is True
