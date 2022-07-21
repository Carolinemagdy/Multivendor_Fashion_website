from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import *
from rest_framework import generics , permissions,filters
from rest_framework.response import Response
from rest_framework import status
from core.permissions import *
from django.core.exceptions import ObjectDoesNotExist
from django_filters.rest_framework import DjangoFilterBackend


# Create your views here.

########### Category Views  ##########

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
    
########### Product Views ##############

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
        # if 'price' in request.data:
            # chane all order items price
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
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend,filters.OrderingFilter,filters.SearchFilter]
    filterset_fields=('id','category','name','price','vendor',
                    'created','in_stock_total','is_active','product_discount_price')
    search_fields=['id','category__id','name','price','vendor__user__id',
                      'created','in_stock_total','is_active','product_discount_price']
    ordering_fields = ('id','category','name','price','vendor',
                      'created','in_stock_total','is_active','product_discount_price')
    


########## Order Views ##################
class ItemOrderView(APIView):
    permission_classes = (permissions.IsAuthenticated,IsCustomer)
    serializer_class = OrderItemSerializer

    def post(self, request,id):
        ''' 
        Add to cart API        
        '''
        try:
            product=Product.objects.get(id=id)
        except ObjectDoesNotExist:
            return Response({'Product object not found'},status=status.HTTP_404_NOT_FOUND)

        if product.in_stock_total==0:
            return Response({'Product is out of stock'},status=status.HTTP_405_METHOD_NOT_ALLOWED)
            
        customer=Customer.objects.get(user=request.user)
        order, created=Order.objects.get_or_create(ordered=False,user=customer)
        data=request.data
        if 'quantity' in data:
            if data['quantity']>product.in_stock_total:
                message='exceeded the total stock quantity, max quantity'+ product.in_stock_total         
                data['quantity']=product.in_stock_total
        try:
            order_item=OrderItem.objects.get(product=product,order=order)
            serializer = OrderItemSerializer(order_item,data=data)
            if serializer.is_valid():
                serializer.save()
                try :
                    return Response({message,serializer.data}, status=status.HTTP_201_CREATED)
                except:
                    return Response(serializer.data, status=status.HTTP_201_CREATED)

        except:

            serializer = OrderItemSerializer(data=data)
            if serializer.is_valid():
                serializer.save(order=order,product=product)
                try :
                    return Response({message,serializer.data}, status=status.HTTP_201_CREATED)
                except:
                    return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request,id):
        '''  
        Remove fom cart API
        '''
        try:
            product=Product.objects.get(id=id)
        except ObjectDoesNotExist:
            return Response({'Product object not found'},status=status.HTTP_404_NOT_FOUND)
        try:
            customer=Customer.objects.get(user=request.user)

            order=Order.objects.get(ordered=False,user=customer)

            order_item=OrderItem.objects.get(product=product,order=order)
        except ObjectDoesNotExist:
            return Response({'Product is not in the cart'},status=status.HTTP_404_NOT_FOUND)
        order_item.delete()
        order_items=OrderItem.objects.filter(order=order)
        if not order_items:
            order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def put(self, request,id):
        ''' 
        edit item in cart API
        '''
        try:
            product=Product.objects.get(id=id)
        except ObjectDoesNotExist:
            return Response({'Product object not found'},status=status.HTTP_404_NOT_FOUND)
        try:
            customer=Customer.objects.get(user=request.user)

            order=Order.objects.get(ordered=False,user=customer)

            order_item=OrderItem.objects.get(product=product,order=order)
        except ObjectDoesNotExist:
            return Response({'Product is not in the cart'},status=status.HTTP_404_NOT_FOUND)
        
        serializer = OrderItemSerializer(order_item,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CartView(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,IsCustomer)
    def get(self,request):
        try:
            customer=Customer.objects.get(user=request.user)
            order=Order.objects.get(ordered=False,user=customer)
        except ObjectDoesNotExist:
            return Response({'Cart is Empty'})
        query=order.order_items.all()
        serializer = OrderProductSerializer(query, many=True)
        order=OrderSerializer(order)
        return Response({'order':order.data,'products':serializer.data}, status=status.HTTP_200_OK)       
                
        
class CheckoutView(generics.UpdateAPIView):
    permission_classes = (permissions.IsAuthenticated,IsCustomer)
    def put(self, request):
        ''' 
        edit cart to be an order 
        '''
        try:
            customer=Customer.objects.get(user=request.user)

            order=Order.objects.get(ordered=False,user=customer)

        except ObjectDoesNotExist:
            return Response({'The cart is empty'},status=status.HTTP_404_NOT_FOUND)
        items_list=OrderItem.objects.filter(order=order)
        for one in items_list:  
            if one.quantity>one.product.in_stock_total:
                return Response(('exceeded the total stock quantity, max quantity', one.product.in_stock_total,one.product.name ) )      
        
        data=request.data
        data['ordered']=True
        if 'address' not in data:
            return Response('you must enter the shipping address' )      

        serializer = OrderSerializer(order,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            for one in items_list:  
                one.product.in_stock_total-=one.quantity
                one.product.save()

            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CancelOrderView(generics.UpdateAPIView):

    permission_classes = (permissions.IsAuthenticated,IsCustomer)
    def put(self, request,id):
        ''' 
        cancel an order 
        '''
        try:
            customer=Customer.objects.get(user=request.user)

            order=Order.objects.get(id=id,user=customer)

        except ObjectDoesNotExist:
            return Response({'The Order is not found'},status=status.HTTP_404_NOT_FOUND)

        if order.delivered :
            return Response({'The Order was delivered already'},status=status.HTTP_404_NOT_FOUND)
        if order.cancelled :
            return Response({'The Order was cancelled already'},status=status.HTTP_404_NOT_FOUND)

        items_list=OrderItem.objects.filter(order=order)
        
        data=request.data
        data['cancelled']=True

        serializer = OrderSerializer(order,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            for one in items_list:  
                one.product.in_stock_total+=one.quantity
                one.product.save()

            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OrderView(generics.ListAPIView):
    '''
    get all orders for the requested user 
    '''
    permission_classes = (permissions.IsAuthenticated,IsVendorOrCustomer)
    def get(self,request):
        if request.user.is_customer:
            customer=Customer.objects.get(user=request.user)
            orders=Order.objects.filter(ordered=True,user=customer)
            if not orders:
                return Response({'No orders yet'})
            serializer = OrderSerializer(orders, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif request.user.is_vendor:    
            vendor=Vendor.objects.get(user=request.user)                
            order_items = OrderItem.objects.filter(product__vendor=vendor) & OrderItem.objects.filter(order__ordered=True)
            if not order_items:
                return Response({'No orders yet for this product'})
            
            serializer = OrderItemSerializer(order_items, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)       

            
                   
class VendorOrderView(generics.ListAPIView):
    '''
    get all orders for a product from the requested vendor
    '''
    permission_classes = (permissions.IsAuthenticated,IsVendor)
    def get(self,request,id):
        try:
            product=Product.objects.get(id=id)
        except ObjectDoesNotExist:
            return Response({'Product object not found'},status=status.HTTP_404_NOT_FOUND)
        try:
            vendor=Vendor.objects.get(user=request.user)
            product=Product.objects.get(id=id,vendor=vendor)
        except ObjectDoesNotExist:
            return Response({'vendor is not the owner of this product'},status=status.HTTP_403_FORBIDDEN)
        order_items = OrderItem.objects.filter(product__vendor=vendor,product=product) & OrderItem.objects.filter(order__ordered=True)    
        if not order_items:
            return Response({'No orders yet for this product'})
        serializer = OrderItemSerializer(order_items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)       

class VendorItemView(generics.RetrieveUpdateAPIView):
    permission_classes = (permissions.IsAuthenticated,IsVendor)
    '''
    get and edit product in a specific order
    '''
    def get(self,request,order_id,product_id):
        try:
            product=Product.objects.get(id=product_id)
        except ObjectDoesNotExist:
            return Response({'Product object not found'},status=status.HTTP_404_NOT_FOUND)
        try:
            vendor=Vendor.objects.get(user=request.user)
            product=Product.objects.get(id=product_id,vendor=vendor)
        except ObjectDoesNotExist:
            return Response({'vendor is not the owner of this product'},status=status.HTTP_403_FORBIDDEN)
        try:
            order=Order.objects.get(id=order_id,ordered=True)
        except ObjectDoesNotExist:
            return Response({'Order object not found'},status=status.HTTP_404_NOT_FOUND)
        try:
            orderItem=OrderItem.objects.get(order=order,product=product)
        except ObjectDoesNotExist:
            return Response({'vendor does not have any orders for this product'},status=status.HTTP_403_FORBIDDEN)
            
        serializer = OrderItemSerializer(orderItem)
        return Response(serializer.data, status=status.HTTP_200_OK)   

    def put(self,request,order_id,product_id):
        try:
            product=Product.objects.get(id=product_id)
        except ObjectDoesNotExist:
            return Response({'Product object not found'},status=status.HTTP_404_NOT_FOUND)
        try:
            vendor=Vendor.objects.get(user=request.user)
            product=Product.objects.get(id=product_id,vendor=vendor)
        except ObjectDoesNotExist:
            return Response({'vendor is not the owner of this product'},status=status.HTTP_403_FORBIDDEN)
        try:
            order=Order.objects.get(id=order_id,ordered=True)
        except ObjectDoesNotExist:
            return Response({'Order object not found'},status=status.HTTP_404_NOT_FOUND)
        try:
            orderItem=OrderItem.objects.get(order=order,product=product)
        except ObjectDoesNotExist:
            return Response({'vendor does not have any orders for this product'},status=status.HTTP_403_FORBIDDEN)
            
        serializer = OrderItemSerializer(orderItem,data=request.data,partial=True)
        return Response(serializer.data, status=status.HTTP_200_OK)   
        



class OrderItemView(generics.RetrieveUpdateAPIView):
    permission_classes = (permissions.IsAuthenticated,IsSuperuserOrVendor)
    '''
    get and edit OrderItem
    '''
    def get(self,request,pk):
        try:
            order_item=OrderItem.objects.get(id=pk)
        except ObjectDoesNotExist:
            return Response({'OrderItem object not found'},status=status.HTTP_404_NOT_FOUND)
        if request.user.is_vendor:
            order_item=OrderItem.objects.get(id=pk)
            order=order_item.order
            if order.ordered==False: 
                return Response({'OrderItem object not found'},status=status.HTTP_404_NOT_FOUND)

            vendor=Vendor.objects.get(user=request.user)
            product=order_item.product

            if product.vendor != vendor :
                
                return Response({'vendor is not the owner of this OrderItem'},status=status.HTTP_403_FORBIDDEN)
            
        serializer = OrderItemSerializer(order_item)
        return Response(serializer.data, status=status.HTTP_200_OK)   
    
    def put(self,request,pk):
        try:
            order_item=OrderItem.objects.get(id=pk)
        except ObjectDoesNotExist:
            return Response({'OrderItem object not found'},status=status.HTTP_404_NOT_FOUND)
        if request.user.is_vendor:
            order_item=OrderItem.objects.get(id=pk)
            order=order_item.order
            if order.ordered==False: 
                return Response({'OrderItem object not found'},status=status.HTTP_404_NOT_FOUND)

            vendor=Vendor.objects.get(user=request.user)
            product=order_item.product

            if product.vendor != vendor :
                
                return Response({'vendor is not the owner of this OrderItem'},status=status.HTTP_403_FORBIDDEN)
            
        serializer = OrderItemSerializer(order_item,data=request.data,partial=True)
        return Response(serializer.data, status=status.HTTP_200_OK)   
        

