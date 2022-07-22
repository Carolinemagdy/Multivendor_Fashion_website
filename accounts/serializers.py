
from rest_framework import serializers
from .models import *

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=65, min_length=8, write_only=True)
    email = serializers.EmailField(max_length=255, min_length=4),
    name = serializers.CharField(max_length=255, min_length=2)
    is_customer=serializers.BooleanField(default=False,read_only=True)
    is_vendor=serializers.BooleanField(default=False,read_only=True)
    class Meta:
        model = User
        fields = ['id','name', 'email', 'password',
                  'is_vendor','is_customer']

    def validate(self, attrs):
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError(
                {'email': ('Email is already in use')})
        return super().validate(attrs)

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

class VendorSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=True)
    rating=serializers.IntegerField(read_only=True)
    class Meta:
        model = Vendor
        fields = ('user','area', 'description', 'address','rating')


    def create(self, validated_data):
        data=validated_data.pop('user')
        UserSerializer.create(UserSerializer(), validated_data=data)
        user = User.objects.get(email=data['email'])
        user.is_vendor=True
        user.save()

        vendor,_=Vendor.objects.update_or_create(user=user,rating=0,
                    area=validated_data.get('area',''),address=validated_data.get('address',''),
                    description=validated_data.get('description',''))
        
        return vendor
    
class CustomerSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=True)
    class Meta:
        model = Customer
        fields = ('user','phone', 'country')


    def create(self, validated_data):
        data=validated_data.pop('user')
        UserSerializer.create(UserSerializer(), validated_data=data)
        user = User.objects.get(email=data['email'])
        user.is_customer=True
        user.save()

        customer,_=Customer.objects.update_or_create(user=user,
                    phone=validated_data.get('phone',''),country=validated_data.get('country',''))
        
        return customer
    

class LoginSerializer(serializers.ModelSerializer):
    
    is_customer = serializers.BooleanField(read_only=True)
    is_vendor = serializers.BooleanField(read_only=True)

    password = serializers.CharField(
        max_length=65, min_length=8, write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password','is_customer','is_vendor']
