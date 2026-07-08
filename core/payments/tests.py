import pytest
from unittest.mock import MagicMock
from decimal import Decimal
from rest_framework.test import APIClient
from rest_framework import status
from django.http import HttpResponse
from django.urls import reverse
from payments.models import Transaction, Payment
from orders.models import Order
from cart.models import Cart, CartItem
from products.models import Product


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
def vendor_client(api_client, vendor_user):
    api_client.force_authenticate(user=vendor_user)
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
def order_with_cart(vendor_user, product):
    cart = Cart.objects.create(user=vendor_user)
    CartItem.objects.create(cart=cart, product=product, quantity=2)
    order = Order.objects.create(
        user=vendor_user,
        country="IR",
        city="Tehran",
        address="12345678901234567890",
        zipcode="123456789012",
        total_price=Decimal("300.00"),
        cart=cart,
    )
    return order


@pytest.fixture
def transaction(vendor_user, order_with_cart):
    return Transaction.objects.create(
        user=vendor_user,
        description=f"Payment for Order #{order_with_cart.id}",
        authority="test_tracking_code_123",
        status="pending",
    )


@pytest.fixture
def payment(order_with_cart, transaction):
    return Payment.objects.create(
        order=order_with_cart,
        transaction=transaction,
        is_successful=False,
    )


@pytest.mark.django_db
class TestProcessPayment:
    def _setup_bank_mock(self, monkeypatch, tracking_code="auth_123"):
        mock_bank = MagicMock()
        mock_bank.ready.return_value = MagicMock(tracking_code=tracking_code)
        mock_bank.redirect_gateway.return_value = HttpResponse(status=302)

        mock_factory_instance = MagicMock()
        mock_factory_instance.auto_create.return_value = mock_bank
        monkeypatch.setattr("payments.views.bankfactories.BankFactory", lambda: mock_factory_instance)
        return mock_bank

    def test_anonymous_cannot_process(self, api_client):
        response = api_client.post(reverse("payments:payment_process"))
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_no_order_returns_404(self, vendor_client):
        response = vendor_client.post(reverse("payments:payment_process"))
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_creates_transaction(self, vendor_client, vendor_user, order_with_cart, monkeypatch):
        self._setup_bank_mock(monkeypatch, tracking_code="auth_tx")
        vendor_client.post(reverse("payments:payment_process"))
        assert Transaction.objects.filter(user=vendor_user, authority="auth_tx").exists()

    def test_creates_payment(self, vendor_client, vendor_user, order_with_cart, monkeypatch):
        self._setup_bank_mock(monkeypatch, tracking_code="auth_pay")
        vendor_client.post(reverse("payments:payment_process"))
        transaction = Transaction.objects.get(authority="auth_pay")
        assert Payment.objects.filter(order=order_with_cart, transaction=transaction).exists()

    def test_transaction_status_is_pending(self, vendor_client, order_with_cart, monkeypatch):
        self._setup_bank_mock(monkeypatch, tracking_code="auth_pend")
        vendor_client.post(reverse("payments:payment_process"))
        transaction = Transaction.objects.get(authority="auth_pend")
        assert transaction.status == "pending"

    def test_payment_is_not_successful_initially(self, vendor_client, order_with_cart, monkeypatch):
        self._setup_bank_mock(monkeypatch, tracking_code="auth_succ")
        vendor_client.post(reverse("payments:payment_process"))
        transaction = Transaction.objects.get(authority="auth_succ")
        payment = Payment.objects.get(transaction=transaction)
        assert payment.is_successful is False

    def test_bank_exception_returns_500(self, vendor_client, order_with_cart, monkeypatch):
        from azbankgateways.exceptions import AZBankGatewaysException
        mock_bank = MagicMock()
        mock_bank.ready.side_effect = AZBankGatewaysException("Bank error")

        mock_factory_instance = MagicMock()
        mock_factory_instance.auto_create.return_value = mock_bank
        monkeypatch.setattr("payments.views.bankfactories.BankFactory", lambda: mock_factory_instance)

        response = vendor_client.post(reverse("payments:payment_process"))
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


@pytest.mark.django_db
class TestPaymentCallback:
    def _setup_callback_mock(self, monkeypatch, is_success=True, raise_exception=False):
        mock_bank = MagicMock()
        mock_result = MagicMock()
        mock_result.is_success = is_success
        mock_bank.get_result.return_value = mock_result
        mock_bank.verify_from_gateaway.return_value = None

        mock_factory_instance = MagicMock()
        mock_factory_instance.create.return_value = mock_bank
        monkeypatch.setattr("payments.views.bankfactories.BankFactory", lambda: mock_factory_instance)

        mock_bank_record = MagicMock()
        mock_bank_record.bank_type = "test"

        mock_bank_models = MagicMock()
        mock_bank_models.Bank.objects.get.return_value = mock_bank_record
        mock_bank_models.Bank.DoesNotExist = type("DoesNotExist", (Exception,), {})
        if raise_exception:
            mock_bank.verify_from_gateaway.side_effect = type(
                "AZBankGatewaysException", (Exception,), {}
            )("Bank error")
            monkeypatch.setattr(
                "payments.views.AZBankGatewaysException",
                mock_bank.verify_from_gateaway.side_effect.__class__,
            )
        monkeypatch.setattr("payments.views.bank_models", mock_bank_models)

    def test_missing_tracking_code_returns_404(self, api_client):
        response = api_client.get(reverse("payments:payment_callback"))
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_invalid_tracking_code_returns_404(self, api_client):
        response = api_client.get(
            reverse("payments:payment_callback"),
            {"tc": "nonexistent"},
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_successful_payment(self, api_client, transaction, payment, monkeypatch):
        self._setup_callback_mock(monkeypatch, is_success=True)
        response = api_client.get(
            reverse("payments:payment_callback"),
            {"tc": transaction.authority},
        )
        assert response.status_code == status.HTTP_200_OK

    def test_successful_payment_updates_transaction(self, api_client, transaction, payment, monkeypatch):
        self._setup_callback_mock(monkeypatch, is_success=True)
        api_client.get(
            reverse("payments:payment_callback"),
            {"tc": transaction.authority},
        )
        transaction.refresh_from_db()
        assert transaction.status == "completed"

    def test_successful_payment_updates_payment(self, api_client, transaction, payment, monkeypatch):
        self._setup_callback_mock(monkeypatch, is_success=True)
        api_client.get(
            reverse("payments:payment_callback"),
            {"tc": transaction.authority},
        )
        payment.refresh_from_db()
        assert payment.is_successful is True

    def test_failed_payment(self, api_client, transaction, payment, monkeypatch):
        self._setup_callback_mock(monkeypatch, is_success=False)
        response = api_client.get(
            reverse("payments:payment_callback"),
            {"tc": transaction.authority},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_failed_payment_updates_transaction(self, api_client, transaction, payment, monkeypatch):
        self._setup_callback_mock(monkeypatch, is_success=False)
        api_client.get(
            reverse("payments:payment_callback"),
            {"tc": transaction.authority},
        )
        transaction.refresh_from_db()
        assert transaction.status == "failed"

    def test_bank_exception_returns_500(self, api_client, transaction, payment, monkeypatch):
        from azbankgateways.exceptions import AZBankGatewaysException

        mock_bank = MagicMock()
        mock_bank.verify_from_gateaway.side_effect = AZBankGatewaysException("Bank error")

        mock_factory_instance = MagicMock()
        mock_factory_instance.create.return_value = mock_bank
        monkeypatch.setattr("payments.views.bankfactories.BankFactory", lambda: mock_factory_instance)

        mock_bank_record = MagicMock()
        mock_bank_record.bank_type = "test"
        mock_bank_models = MagicMock()
        mock_bank_models.Bank.objects.get.return_value = mock_bank_record
        mock_bank_models.Bank.DoesNotExist = type("DoesNotExist", (Exception,), {})
        monkeypatch.setattr("payments.views.bank_models", mock_bank_models)

        response = api_client.get(
            reverse("payments:payment_callback"),
            {"tc": transaction.authority},
        )
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    def test_bank_exception_sets_transaction_failed(self, api_client, transaction, payment, monkeypatch):
        from azbankgateways.exceptions import AZBankGatewaysException

        mock_bank = MagicMock()
        mock_bank.verify_from_gateaway.side_effect = AZBankGatewaysException("Bank error")

        mock_factory_instance = MagicMock()
        mock_factory_instance.create.return_value = mock_bank
        monkeypatch.setattr("payments.views.bankfactories.BankFactory", lambda: mock_factory_instance)

        mock_bank_record = MagicMock()
        mock_bank_record.bank_type = "test"
        mock_bank_models = MagicMock()
        mock_bank_models.Bank.objects.get.return_value = mock_bank_record
        mock_bank_models.Bank.DoesNotExist = type("DoesNotExist", (Exception,), {})
        monkeypatch.setattr("payments.views.bank_models", mock_bank_models)

        api_client.get(
            reverse("payments:payment_callback"),
            {"tc": transaction.authority},
        )
        transaction.refresh_from_db()
        assert transaction.status == "failed"
