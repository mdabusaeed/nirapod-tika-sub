from django.shortcuts import render, redirect
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin
from order.models import Cart, CartItem, Order, OrderItem
from order.serializers import CartSerializer, CartItemSerializer, AddCartItemSerializer, UpdateCartItemSerializer, OrderSerializer, CreateOrderSerializer
from order.serializers import UpdateOrderSerializer, EmptyCartSerializer
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import serializers 
from rest_framework.decorators import action
from order.services import OrderService
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from sslcommerz_lib import SSLCOMMERZ 

class CartViewSet(CreateModelMixin,RetrieveModelMixin, DestroyModelMixin,GenericViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]  

    def perform_create(self, serializer):
        if Cart.objects.filter(user=self.request.user).exists():
            raise serializers.ValidationError("You already have a cart.")
        
        serializer.save(user = self.request.user)

    def get_queryset(self):
        return Cart.objects.prefetch_related('items__product').filter(user = self.request.user)
    
    def create(self, request, *args, **kwargs):
        existing_cart = Cart.objects.filter(user=request.user).first()
        if existing_cart:
            serializers = self.get_serializer(existing_cart)
            return Response(serializers.data, status=status.HTTP_200_OK)
        return super().create(request, *args, **kwargs)

    

class CartItemViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemSerializer
        elif self.request.method == 'PATCH':
            return UpdateCartItemSerializer
        return CartItemSerializer   
    
    def get_serializer_context(self):
        return {'cart_id': self.kwargs['cart_pk']}

    def get_queryset(self):
        return CartItem.objects.select_related('product').filter(cart_id = self.kwargs['cart_pk'])
    

class OrderViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    @action(detail=True, methods=['POST'])
    def cancel(self, request, pk=None):
        order = self.get_object()
        OrderService.cancel_order(order = order, user = request.user)
        return Response({'status': 'Order cancelled'})
    

    @action(detail=True, methods=['PATCH'])
    def update_status(self, request,pk=None):
        order = self.get_object()
        
        serializer = UpdateOrderSerializer(order, data=request.data, partial=True) 
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'status': f'Order status updated to {serializer.data["status"]}'})

    def get_permissions(self):
        if self.action in ['destroy', 'update_status']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'cancel':
            return EmptyCartSerializer
        
        if self.action == 'create':
            return CreateOrderSerializer
        elif self.action == 'update_status':
            return UpdateOrderSerializer
        return OrderSerializer
    
    def get_serializer_context(self):
        return {'user_id': self.request.user.id, 'user': self.request.user}

    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.prefetch_related('order_items__product').all()
        return Order.objects.prefetch_related('order_items__product').filter(user = self.request.user)
    
@api_view(['POST'])
def initiate_payment(request):
    amount = request.data.get('amount')
    user = request.user
    order_id = request.data.get('orderId')
    num_items = request.data.get('numItems')

    settings = { 'store_id':'tikac681426db54eb9', 'store_pass':'tikac681426db54eb9@ssl', 'issandbox': True }
    sslcz = SSLCOMMERZ(settings)
    post_body = {}
    post_body['total_amount'] = amount
    post_body['currency'] = "BDT"
    post_body['tran_id'] = f"txn_{order_id}"
    post_body['success_url'] = "http://localhost:5173/payment/success/"
    post_body['fail_url'] = "http://localhost:5173/payment/fail/"
    post_body['cancel_url'] = "http://localhost:5173/payment/cancel/"
    post_body['emi_option'] = 0
    post_body['cus_name'] = user.first_name + " " + user.last_name
    post_body['cus_email'] = user.email
    post_body['cus_phone'] = user.phone_number
    post_body['cus_add1'] = user.address
    post_body['cus_city'] = "Dhaka"
    post_body['cus_country'] = "Bangladesh"
    post_body['shipping_method'] = "NO"
    post_body['multi_card_name'] = ""
    post_body['num_of_item'] = num_items
    post_body['product_name'] = "Tika"
    post_body['product_category'] = "Medicine"
    post_body['product_profile'] = "Tika"


    response = sslcz.createSession(post_body) # API response

    if response.get('status') == 'SUCCESS':
        return Response({'payment_url' : response['GatewayPageURL']})
    else:
        return Response({'error' : 'Payment faild'}, status=status.HTTP_400_BAD_REQUEST)
    
    
