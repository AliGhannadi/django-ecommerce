import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from orders.models import Order
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
def cart_with_items(vendor_user, product):
    cart = Cart.objects.create(user=vendor_user)
    CartItem.objects.create(cart=cart, product=product, quantity=2)
    return cart


@pytest.fixture
def order_payload():
    return {
        "country": "IR",
        "city": "Tehran",
        "address": "12345678901234567890",
        "zipcode": "123456789012",
    }


# ---------- Test: GET /orders/ ----------


@pytest.mark.django_db
class TestOrderList:
    def test_anonymous_cannot_list(self, api_client):
        response = api_client.get(reverse("orders-list"))
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_authenticated_can_list(self, vendor_client):
        response = vendor_client.get(reverse("orders-list"))
        assert response.status_code == status.HTTP_200_OK


# ---------- Test: POST /orders/ ----------


@pytest.mark.django_db
class TestOrderCreate:
    def test_anonymous_cannot_create(self, api_client, order_payload):
        response = api_client.post(reverse("orders-list"), order_payload)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_without_cart_returns_error(self, vendor_client, order_payload):
        response = vendor_client.post(reverse("orders-list"), order_payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_with_empty_cart_returns_error(self, vendor_client, vendor_user, order_payload):
        Cart.objects.create(user=vendor_user)
        response = vendor_client.post(reverse("orders-list"), order_payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_with_cart_succeeds(self, vendor_client, cart_with_items, order_payload):
        response = vendor_client.post(reverse("orders-list"), order_payload)
        assert response.status_code == status.HTTP_201_CREATED

    def test_create_returns_expected_keys(self, vendor_client, cart_with_items, order_payload):
        response = vendor_client.post(reverse("orders-list"), order_payload)
        assert response.status_code == status.HTTP_201_CREATED
        assert "id" in response.data
        assert "country" in response.data
        assert "city" in response.data
        assert "address" in response.data
        assert "total_price" in response.data

    def test_create_persists_order(self, vendor_client, cart_with_items, order_payload):
        vendor_client.post(reverse("orders-list"), order_payload)
        assert Order.objects.filter(city="Tehran").exists()

    def test_create_sets_user_to_requester(self, vendor_client, vendor_user, cart_with_items, order_payload):
        response = vendor_client.post(reverse("orders-list"), order_payload)
        order = Order.objects.get(pk=response.data["id"])
        assert order.user == vendor_user

    def test_create_sets_cart(self, vendor_client, cart_with_items, order_payload):
        response = vendor_client.post(reverse("orders-list"), order_payload)
        order = Order.objects.get(pk=response.data["id"])
        assert order.cart == cart_with_items


# ---------- Test: GET /orders/{id}/ ----------


@pytest.mark.django_db
class TestOrderRetrieve:
    def test_anonymous_cannot_retrieve(self, api_client, vendor_user, cart_with_items, order_payload):
        vendor_client = APIClient()
        vendor_client.force_authenticate(user=vendor_user)
        response = vendor_client.post(reverse("orders-list"), order_payload)
        order_id = response.data["id"]

        api_client = APIClient()
        response = api_client.get(reverse("orders-detail", kwargs={"pk": order_id}))
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_non_owner_cannot_retrieve(self, regular_client, vendor_user, cart_with_items, order_payload):
        vendor_client = APIClient()
        vendor_client.force_authenticate(user=vendor_user)
        response = vendor_client.post(reverse("orders-list"), order_payload)
        order_id = response.data["id"]

        response = regular_client.get(reverse("orders-detail", kwargs={"pk": order_id}))
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_owner_can_retrieve(self, vendor_client, cart_with_items, order_payload):
        response = vendor_client.post(reverse("orders-list"), order_payload)
        order_id = response.data["id"]

        response = vendor_client.get(reverse("orders-detail", kwargs={"pk": order_id}))
        assert response.status_code == status.HTTP_200_OK

    def test_retrieve_non_existent_returns_404(self, vendor_client):
        response = vendor_client.get(reverse("orders-detail", kwargs={"pk": 9999}))
        assert response.status_code == status.HTTP_404_NOT_FOUND


# ---------- Test: PUT /orders/{id}/ ----------


@pytest.mark.django_db
class TestOrderUpdate:
    def test_anonymous_cannot_update(self, api_client, vendor_user, cart_with_items, order_payload):
        vendor_client = APIClient()
        vendor_client.force_authenticate(user=vendor_user)
        response = vendor_client.post(reverse("orders-list"), order_payload)
        order_id = response.data["id"]

        response = api_client.put(
            reverse("orders-detail", kwargs={"pk": order_id}),
            {"country": "US", "city": "New York", "address": "12345678901234567890", "zipcode": "123456789012"},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_non_owner_cannot_update(self, regular_client, vendor_user, cart_with_items, order_payload):
        vendor_client = APIClient()
        vendor_client.force_authenticate(user=vendor_user)
        response = vendor_client.post(reverse("orders-list"), order_payload)
        order_id = response.data["id"]

        response = regular_client.put(
            reverse("orders-detail", kwargs={"pk": order_id}),
            {"country": "US", "city": "New York", "address": "12345678901234567890", "zipcode": "123456789012"},
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_owner_can_update(self, vendor_client, cart_with_items, order_payload):
        response = vendor_client.post(reverse("orders-list"), order_payload)
        order_id = response.data["id"]

        response = vendor_client.put(
            reverse("orders-detail", kwargs={"pk": order_id}),
            {"country": "US", "city": "New York", "address": "12345678901234567890", "zipcode": "123456789012"},
        )
        assert response.status_code == status.HTTP_200_OK
        order = Order.objects.get(pk=order_id)
        assert order.city == "New York"

    def test_owner_can_partial_update(self, vendor_client, cart_with_items, order_payload):
        response = vendor_client.post(reverse("orders-list"), order_payload)
        order_id = response.data["id"]

        response = vendor_client.patch(
            reverse("orders-detail", kwargs={"pk": order_id}),
            {"city": "Isfahan"},
        )
        assert response.status_code == status.HTTP_200_OK
        order = Order.objects.get(pk=order_id)
        assert order.city == "Isfahan"


# ---------- Test: DELETE /orders/{id}/ ----------


@pytest.mark.django_db
class TestOrderDelete:
    def test_anonymous_cannot_delete(self, api_client, vendor_user, cart_with_items, order_payload):
        vendor_client = APIClient()
        vendor_client.force_authenticate(user=vendor_user)
        response = vendor_client.post(reverse("orders-list"), order_payload)
        order_id = response.data["id"]

        response = api_client.delete(reverse("orders-detail", kwargs={"pk": order_id}))
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_non_owner_cannot_delete(self, regular_client, vendor_user, cart_with_items, order_payload):
        vendor_client = APIClient()
        vendor_client.force_authenticate(user=vendor_user)
        response = vendor_client.post(reverse("orders-list"), order_payload)
        order_id = response.data["id"]

        response = regular_client.delete(reverse("orders-detail", kwargs={"pk": order_id}))
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_owner_can_delete(self, vendor_client, cart_with_items, order_payload):
        response = vendor_client.post(reverse("orders-list"), order_payload)
        order_id = response.data["id"]

        response = vendor_client.delete(reverse("orders-detail", kwargs={"pk": order_id}))
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Order.objects.filter(pk=order_id).exists()
