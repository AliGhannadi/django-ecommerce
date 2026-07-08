import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from cart.models import Cart, CartItem
from products.models import Product


# ---------- Fixtures ----------


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def vendor_user():
    from accounts.models import User

    return User.objects.create_user(
        email="vendor@test.com",
        phone_number="09123456789",
        password="testpass123",
        username="vendor1",
        is_vendor=True,
    )


@pytest.fixture
def regular_user():
    from accounts.models import User

    return User.objects.create_user(
        email="user@test.com",
        phone_number="09123456788",
        password="testpass123",
        username="regular1",
    )


@pytest.fixture
def vendor_client(api_client, vendor_user):
    api_client.force_authenticate(user=vendor_user)
    return api_client


@pytest.fixture
def regular_client(api_client, regular_user):
    api_client.force_authenticate(user=regular_user)
    return api_client


@pytest.fixture
def product(vendor_user):
    return Product.objects.create(
        title="Mechanical Keyboard",
        description="A high-quality mechanical keyboard.",
        brief_description="Mechanical keyboard",
        price=150.00,
        user=vendor_user,
    )


@pytest.fixture
def product2(vendor_user):
    return Product.objects.create(
        title="Gaming Mouse",
        description="An ergonomic gaming mouse.",
        brief_description="Gaming mouse",
        price=75.00,
        user=vendor_user,
    )


@pytest.fixture
def cart(vendor_user):
    return Cart.objects.create(user=vendor_user)


@pytest.fixture
def cart_with_items(vendor_user, product, product2):
    cart = Cart.objects.create(user=vendor_user)
    CartItem.objects.create(cart=cart, product=product, quantity=2)
    CartItem.objects.create(cart=cart, product=product2, quantity=1)
    return cart


# ---------- Test: GET /cart/ ----------


@pytest.mark.django_db
class TestCartList:
    def test_anonymous_cannot_list(self, api_client):
        response = api_client.get(reverse("cart:cart-list"))
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_authenticated_can_list(self, vendor_client, cart):
        response = vendor_client.get(reverse("cart:cart-list"))
        assert response.status_code == status.HTTP_200_OK

    def test_list_returns_own_cart_only(self, vendor_client, cart, regular_user):
        regular_client = APIClient()
        regular_client.force_authenticate(user=regular_user)
        Cart.objects.create(user=regular_user)

        response = vendor_client.get(reverse("cart:cart-list"))
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)

    def test_list_returns_expected_keys(self, vendor_client, cart_with_items):
        response = vendor_client.get(reverse("cart:cart-list"))
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)
        cart_data = response.data[0]
        assert "user" in cart_data
        assert "cartitems" in cart_data
        assert "total_price" in cart_data


# ---------- Test: PATCH /cart/update_item/ ----------


@pytest.mark.django_db
class TestCartUpdateItem:
    def test_anonymous_cannot_update_item(self, api_client, cart_with_items):
        item = cart_with_items.cartitems.first()
        response = api_client.patch(
            reverse("cart:cart-update-item"),
            {"item_id": item.pk, "quantity": 5},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_authenticated_can_update_item(self, vendor_client, cart_with_items):
        item = cart_with_items.cartitems.first()
        response = vendor_client.patch(
            reverse("cart:cart-update-item"),
            {"item_id": item.pk, "quantity": 5},
        )
        assert response.status_code == status.HTTP_200_OK
        item.refresh_from_db()
        assert item.quantity == 5

    def test_update_item_persists_change(self, vendor_client, cart_with_items):
        item = cart_with_items.cartitems.first()
        old_quantity = item.quantity
        vendor_client.patch(
            reverse("cart:cart-update-item"),
            {"item_id": item.pk, "quantity": old_quantity + 3},
        )
        item.refresh_from_db()
        assert item.quantity == old_quantity + 3


# ---------- Test: DELETE /cart/delete_item/ ----------


@pytest.mark.django_db
class TestCartDeleteItem:
    def test_anonymous_cannot_delete_item(self, api_client, cart_with_items):
        item = cart_with_items.cartitems.first()
        response = api_client.delete(
            reverse("cart:cart-delete-item"),
            {"item_id": item.pk},
            format="json",
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_authenticated_can_delete_item(self, vendor_client, cart_with_items):
        item = cart_with_items.cartitems.first()
        item_id = item.pk
        response = vendor_client.delete(
            reverse("cart:cart-delete-item"),
            {"item_id": item_id},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert not CartItem.objects.filter(pk=item_id).exists()

    def test_delete_item_removes_from_cart(self, vendor_client, cart_with_items):
        initial_count = cart_with_items.cartitems.count()
        item = cart_with_items.cartitems.first()
        vendor_client.delete(
            reverse("cart:cart-delete-item"),
            {"item_id": item.pk},
            format="json",
        )
        cart_with_items.refresh_from_db()
        assert cart_with_items.cartitems.count() == initial_count - 1


# ---------- Test: DELETE /cart/clear/ ----------


@pytest.mark.django_db
class TestCartClear:
    def test_anonymous_cannot_clear(self, api_client, cart_with_items):
        response = api_client.delete(reverse("cart:cart-clear"))
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_authenticated_can_clear(self, vendor_client, cart_with_items):
        response = vendor_client.delete(reverse("cart:cart-clear"))
        assert response.status_code == status.HTTP_200_OK

    def test_clear_removes_all_items(self, vendor_client, cart_with_items):
        assert cart_with_items.cartitems.count() > 0
        vendor_client.delete(reverse("cart:cart-clear"))
        cart_with_items.refresh_from_db()
        assert cart_with_items.cartitems.count() == 0
