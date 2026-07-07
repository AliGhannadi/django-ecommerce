from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from cart.permissions import IsOwner
from .models import Transaction, Payment
from orders.models import Order
from django.urls import reverse
from azbankgateways import bankfactories
from azbankgateways.exceptions import AZBankGatewaysException

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsOwner])
def process_payment(request, order_id):
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
           bank.set_client_callback_url(reverse("payment_callback"))
           transaction = Transaction.objects.create(
               user=user,
               description=f"Payment for Order #{order.id}",
               authority=bank_record.tracking_code,
               status="pending"
               
           )
           Payment.objects.create(
               order=order,
               transaction=transaction,
               is_successfull=True
           )
           return bank.redirect_gateway()
       except AZBankGatewaysException as e:
        return Response({"error": e}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)      
    except Order.DoesNotExist: 
        return Response({"error": "No orders found."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

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