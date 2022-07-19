from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import *
from rest_framework import generics , permissions
from rest_framework.response import Response
from rest_framework import status
from core.permissions import *
from django.core.exceptions import ObjectDoesNotExist


# Create your views here.
# class ListCategoryView(generics.ListAPIView):
#     queryset = Category.objects.all()
#     serializer_class = CategorySerializer
    
class ListCreateCategoryView(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,IsSuperuser)
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    def get_permissions(self):
        if self.request.method == 'POST':
            return [permission() for permission in self.permission_classes]
        return [permissions.AllowAny()]


class CategoryRetrtieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (permissions.IsAuthenticated,IsSuperuser)
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    #PUT
    def put(self, request,pk):
        try:
            query_set = Category.objects.get(id=pk)
        except ObjectDoesNotExist:
            return Response({'Category object not found'},status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(query_set,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def get_permissions(self):
        if self.request.method == 'GET' :
            return [permissions.AllowAny()]
        return [permission() for permission in self.permission_classes]
    
class VendorProductView(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,IsVendor)
    def post(self, request,id):
        try:
            category=Category.objects.get(id=id)
        except ObjectDoesNotExist:
            return Response({'Category object not found'},status=status.HTTP_404_NOT_FOUND)
        try:
            vendor=Vendor.objects.get(user=request.user)
        except:
            return Response({'vendor object not found'},status=status.HTTP_404_NOT_FOUND)

        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(category=category,vendor=vendor)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def get(self, request,id):
        try:
            category=Category.objects.get(id=id)
        except ObjectDoesNotExist:
            return Response({'error':'Category object not found'},status=status.HTTP_404_NOT_FOUND)
        try:
            vendor=Vendor.objects.get(user=request.user)
        except:
            return Response({'error':'vendor object not found'},status=status.HTTP_404_NOT_FOUND)
        query_set=Product.objects.filter(vendor=vendor,category=category)
        serializer=ProductSerializer(query_set,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

class AdminProductView(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,IsSuperuser)
    def post(self, request,category_id,vendor_id):
        try:
            category=Category.objects.get(id=category_id)
        except ObjectDoesNotExist:
            return Response({'Category object not found'},status=status.HTTP_404_NOT_FOUND)
        try:
            vendor=Vendor.objects.get(user=vendor_id)
        except:
            return Response({'vendor object not found'},status=status.HTTP_404_NOT_FOUND)

        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(category=category,vendor=vendor)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProductView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (permissions.IsAuthenticated,IsSuperuserOrVendor)
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def put(self, request,pk):
        try:
            product=Product.objects.get(id=pk)
        except ObjectDoesNotExist:
            return Response({'Product object not found'},status=status.HTTP_404_NOT_FOUND)
        if request.user.is_vendor:            
            try:
                vendor=Vendor.objects.get(user=request.user)
                product=Product.objects.get(id=pk,vendor=vendor)
            except:
                return Response({'vendor is not the owner of this product'},status=status.HTTP_403_FORBIDDEN)

        serializer = self.serializer_class(product,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request,pk):
        try:
            product=Product.objects.get(id=pk)
        except ObjectDoesNotExist:
            return Response({'Product object not found'},status=status.HTTP_404_NOT_FOUND)
        if request.user.is_vendor:            
            try:
                vendor=Vendor.objects.get(user=request.user)
                product=Product.objects.get(id=pk,vendor=vendor)
            except:
                return Response({'vendor is not the owner of this product'},status=status.HTTP_403_FORBIDDEN)

        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    def get_permissions(self):
        if self.request.method == 'GET' :
            return [permissions.AllowAny()]
        return [permission() for permission in self.permission_classes]


class ListProductView(generics.ListAPIView):
    def get(self,request):
        vendor=request.query_params.get("vendor")
        category=request.query_params.get("category")
        if vendor and category:
            try:
                category=Category.objects.get(id=category)
            except ObjectDoesNotExist:
                return Response({'error':'Category object not found'},status=status.HTTP_404_NOT_FOUND)
            try:
                vendor=Vendor.objects.get(user=vendor)
            except:
                return Response({'error':'vendor object not found'},status=status.HTTP_404_NOT_FOUND)
            query_set=Product.objects.filter(vendor=vendor,category=category)
            serializer=ProductSerializer(query_set,many=True)
            return Response(serializer.data,status=status.HTTP_200_OK)  
        elif vendor :
            try:
                vendor=Vendor.objects.get(user=vendor)
            except:
                return Response({'error':'vendor object not found'},status=status.HTTP_404_NOT_FOUND)
            query_set=Product.objects.filter(vendor=vendor)
            serializer=ProductSerializer(query_set,many=True)
            return Response(serializer.data,status=status.HTTP_200_OK)  

        elif category:            
            try:
                category=Category.objects.get(id=category)
            except ObjectDoesNotExist:
                return Response({'error':'Category object not found'},status=status.HTTP_404_NOT_FOUND)
            query_set=Product.objects.filter(category=category)
            serializer=ProductSerializer(query_set,many=True)
            return Response(serializer.data,status=status.HTTP_200_OK)  
        else:
            query_set=Product.objects.all()
            serializer=ProductSerializer(query_set,many=True)
            return Response(serializer.data,status=status.HTTP_200_OK)  




