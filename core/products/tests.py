import pytest
from decimal import Decimal
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
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
def product_payload():
    return {
        "title": "Gaming Mouse",
        "description": "Ergonomic gaming mouse with RGB lighting.",
        "brief_description": "RGB gaming mouse",
        "price": "75.00",
    }


# ---------- Test: GET /products/ ----------


@pytest.mark.django_db
class TestProductList:
    def test_anonymous_can_list(self, api_client, product):
        response = api_client.get(reverse("products-list"))
        assert response.status_code == status.HTTP_200_OK

    def test_authenticated_can_list(self, vendor_client, product):
        response = vendor_client.get(reverse("products-list"))
        assert response.status_code == status.HTTP_200_OK

    def test_list_returns_list_of_products(self, api_client, product):
        response = api_client.get(reverse("products-list"))
        assert isinstance(response.data, list)
        assert len(response.data) >= 1


# ---------- Test: POST /products/ ----------


@pytest.mark.django_db
class TestProductCreate:
    def test_anonymous_cannot_create(self, api_client, product_payload):
        response = api_client.post(reverse("products-list"), product_payload)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_non_vendor_cannot_create(self, regular_client, product_payload):
        response = regular_client.post(reverse("products-list"), product_payload)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_vendor_can_create(self, vendor_client, product_payload):
        response = vendor_client.post(reverse("products-list"), product_payload)
        assert response.status_code == status.HTTP_201_CREATED

    def test_create_returns_expected_keys(self, vendor_client, product_payload):
        response = vendor_client.post(reverse("products-list"), product_payload)
        assert response.status_code == status.HTTP_201_CREATED
        assert "id" in response.data
        assert "title" in response.data
        assert "price" in response.data
        assert "user" in response.data
        assert "absolute_url" in response.data

    def test_create_missing_title_returns_400(self, vendor_client, product_payload):
        product_payload.pop("title")
        response = vendor_client.post(reverse("products-list"), product_payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_missing_price_returns_400(self, vendor_client, product_payload):
        product_payload.pop("price")
        response = vendor_client.post(reverse("products-list"), product_payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_persists_product(self, vendor_client, product_payload):
        vendor_client.post(reverse("products-list"), product_payload)
        assert Product.objects.filter(title="Gaming Mouse").exists()

    def test_create_sets_user_to_requester(self, vendor_client, vendor_user, product_payload):
        response = vendor_client.post(reverse("products-list"), product_payload)
        product = Product.objects.get(pk=response.data["id"])
        assert product.user == vendor_user


# ---------- Test: GET /products/{id}/ ----------


@pytest.mark.django_db
class TestProductRetrieve:
    def test_anonymous_can_retrieve(self, api_client, product):
        response = api_client.get(reverse("products-detail", kwargs={"pk": product.pk}))
        assert response.status_code == status.HTTP_200_OK

    def test_retrieve_returns_expected_keys(self, api_client, product):
        response = api_client.get(reverse("products-detail", kwargs={"pk": product.pk}))
        assert "id" in response.data
        assert response.data["title"] == product.title
        assert "price" in response.data

    def test_retrieve_non_existent_returns_404(self, api_client):
        response = api_client.get(reverse("products-detail", kwargs={"pk": 9999}))
        assert response.status_code == status.HTTP_404_NOT_FOUND


# ---------- Test: PUT /products/{id}/ ----------


@pytest.mark.django_db
class TestProductUpdate:
    def test_anonymous_cannot_update(self, api_client, product):
        response = api_client.put(
            reverse("products-detail", kwargs={"pk": product.pk}),
            {"title": "Hacked"},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_non_owner_cannot_update(self, regular_client, product):
        response = regular_client.put(
            reverse("products-detail", kwargs={"pk": product.pk}),
            {"title": "Hacked", "description": "x", "brief_description": "x", "price": "1"},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_owner_can_update(self, vendor_client, product):
        response = vendor_client.put(
            reverse("products-detail", kwargs={"pk": product.pk}),
            {
                "title": "Updated Keyboard",
                "description": product.description,
                "brief_description": product.brief_description,
                "price": "200.00",
            },
        )
        assert response.status_code == status.HTTP_200_OK
        product.refresh_from_db()
        assert product.title == "Updated Keyboard"
        assert product.price == Decimal("200.00")

    def test_owner_can_partial_update(self, vendor_client, product):
        response = vendor_client.patch(
            reverse("products-detail", kwargs={"pk": product.pk}),
            {"price": "99.99"},
        )
        assert response.status_code == status.HTTP_200_OK
        product.refresh_from_db()
        assert product.price == Decimal("99.99")


# ---------- Test: DELETE /products/{id}/ ----------


@pytest.mark.django_db
class TestProductDelete:
    def test_anonymous_cannot_delete(self, api_client, product):
        response = api_client.delete(reverse("products-detail", kwargs={"pk": product.pk}))
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_non_owner_cannot_delete(self, regular_client, product):
        response = regular_client.delete(reverse("products-detail", kwargs={"pk": product.pk}))
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_owner_can_delete(self, vendor_client, product):
        response = vendor_client.delete(reverse("products-detail", kwargs={"pk": product.pk}))
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Product.objects.filter(pk=product.pk).exists()


# ---------- Test: POST /products/{id}/add_to_cart/ ----------


@pytest.mark.django_db
class TestProductAddToCart:
    def test_anonymous_cannot_add_to_cart(self, api_client, product):
        response = api_client.post(
            reverse("products-add-to-cart", kwargs={"pk": product.pk})
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_authenticated_can_add_to_cart(self, vendor_client, product):
        response = vendor_client.post(
            reverse("products-add-to-cart", kwargs={"pk": product.pk}),
            {"quantity": 2},
        )
        assert response.status_code == status.HTTP_201_CREATED

    def test_add_to_cart_with_invalid_quantity_returns_400(self, vendor_client, product):
        response = vendor_client.post(
            reverse("products-add-to-cart", kwargs={"pk": product.pk}),
            {"quantity": 0},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_add_to_cart_with_non_numeric_quantity_returns_400(self, vendor_client, product):
        response = vendor_client.post(
            reverse("products-add-to-cart", kwargs={"pk": product.pk}),
            {"quantity": "abc"},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_add_to_cart_defaults_quantity_to_one(self, vendor_client, product):
        response = vendor_client.post(
            reverse("products-add-to-cart", kwargs={"pk": product.pk})
        )
        assert response.status_code == status.HTTP_201_CREATED

    def test_add_to_cart_creates_cart_item(self, vendor_client, product, vendor_user):
        vendor_client.post(
            reverse("products-add-to-cart", kwargs={"pk": product.pk}),
            {"quantity": 1},
        )
        from cart.models import CartItem
        assert CartItem.objects.filter(cart__user=vendor_user, product=product).exists()
