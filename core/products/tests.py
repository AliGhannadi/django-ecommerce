from django.test import TestCase
import pytest
from products.models import Product
from accounts.models import User
# Create your tests here.
@pytest.fixture
def base_user():
    return User.objects.create_user(username="testuser", email="password123", phone_number="09943439586", password="1234567")

@pytest.mark.django_db
def test_product_creation(base_user):
    product = Product.objects.create(title="Mechanical Keyboard", price=99.99, user=base_user)
    assert product.title == "Mechanical Keyboard"
    assert product.price == 99.99
    assert str(product) == "Mechanical Keyboard"