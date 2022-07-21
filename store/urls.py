from django.urls import path
from .views import *

urlpatterns = [
    path('category/', ListCreateCategoryView.as_view()),
    path('category/<int:pk>/', CategoryRetrtieveUpdateDestroyAPIView.as_view()),
    path('category/<int:id>/product/', VendorProductView.as_view()),
    path('category/<int:category_id>/vendor/<int:vendor_id>/product/', AdminProductView.as_view()),
    path('product/<int:pk>/',ProductView.as_view()),
    path('product/',ListProductView.as_view()),
    path('product/<int:id>/order/', ItemOrderView.as_view()),
    path('cart/', CartView.as_view()),
    path('order/checkout/', CheckoutView.as_view()),
    path('order/<int:id>/cancel/', CancelOrderView.as_view()),
    path('order/', OrderView.as_view()),
    path('vendor/product/<int:id>/', VendorOrderView.as_view()),
    path('order/<int:order_id>/product/<int:product_id>/', VendorItemView.as_view()),
    path('orderItem/<int:pk>/', OrderItemView.as_view()),

    


]