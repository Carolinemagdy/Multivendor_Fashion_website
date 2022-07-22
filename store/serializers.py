from accounts.serializers import *
from rest_framework import serializers
from .models import *

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        extra_kwargs={'category': {'read_only': True}, 'vendor': {'read_only': True}}
        
class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'
        extra_kwargs={'user': {'read_only': True}}
         
class OrderItemSerializer(serializers.ModelSerializer):
    # order=OrderSerializer(read_only=True)
    # product=ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = '__all__'
        extra_kwargs={'order': {'read_only': True}, 'product': {'read_only': True}}
        
class OrderProductSerializer(serializers.ModelSerializer):
    product= ProductSerializer(read_only=True)
    class Meta:
        model = OrderItem
        fields = '__all__'

class CancelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields =['cancelled']
        