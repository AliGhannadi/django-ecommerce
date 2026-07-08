from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from rest_framework.response import Response
from .models import Transaction, Payment
from orders.models import Order
from django.urls import reverse
from azbankgateways import bankfactories
from azbankgateways.exceptions import AZBankGatewaysException
from azbankgateways import (
    bankfactories,
    models as bank_models,
    default_settings as settings,
)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def process_payment(request):
    user = request.user
    try:
       order = Order.objects.get(user=user)
       amount = order.total_price
       phone_number = order.user.phone_number
       factory = bankfactories.BankFactory()
       try:
           bank = factory.auto_create()
           bank.set_request(request)
           bank.set_amount(amount)
           bank_record = bank.ready()
           bank.set_client_callback_url(reverse("payments:payment_callback"))
           transaction = Transaction.objects.create(
               user=user,
               description=f"Payment for Order #{order.id} - Total Price: {amount}",
               authority=bank_record.tracking_code,
               status="pending"
               
           )
           Payment.objects.create(
               order=order,
               transaction=transaction,
               is_successful=False
           )
           return bank.redirect_gateway()
       
       except AZBankGatewaysException as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)      
    except Order.DoesNotExist: 
        return Response({"error": "No orders found."}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([AllowAny])
def callback_getaway_view(request):
    tracking_code = request.GET.get(settings.TRACKING_CODE_QUERY_PARAM, None)
    if not tracking_code:
        return Response({"error": "This tracking code is not valid"}, status=status.HTTP_404_NOT_FOUND)
    
    try:
        bank_record = bank_models.Bank.objects.get(tracking_code=tracking_code)
        transaction = Transaction.objects.get(authority=tracking_code)
    except (bank_models.Bank.DoesNotExist, Transaction.DoesNotExist):
        return Response({"error": "Transaction or Bank record not found."}, status=status.HTTP_404_NOT_FOUND)
    factory = bankfactories.BankFactory()
    try:
        bank = factory.create(bank_record.bank_type)
        bank.verify_from_gateaway(request)
        if bank.get_result().is_success:
            payment = Payment.objects.get(transaction=transaction)
            payment.is_successful = True
            payment.save()
            
            transaction.status="completed"
            transaction.save()
            
            return Response({"ok": "Payment processed successfully"}, status=status.HTTP_200_OK)
        else:
            transaction.status="failed"
            transaction.save()
            return Response({"error": "Payment is not valid"}, status=status.HTTP_400_BAD_REQUEST)
    except AZBankGatewaysException as e:
        transaction.status = "failed"
        transaction.save()
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# Create your views here.
# View For payment
### creates a transaction
##### email and phone number == null
##### description = a detailed which saves in databasre
### create a signal for each transaction
### with is_successfull false
### authority 
### status

###### exceptions:
####### if there is no order
####### if error occured during

# View For payment verification