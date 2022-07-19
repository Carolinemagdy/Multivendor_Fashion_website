from django.urls import path
from .views import *

urlpatterns = [
    path('category/', ListCreateCategoryView.as_view()),
    path('category/<int:pk>/', CategoryRetrtieveUpdateDestroyAPIView.as_view()),
    path('category/<int:id>/product', VendorProductView.as_view()),
    path('category/<int:category_id>/vendor/<int:vendor_id>/product', AdminProductView.as_view()),
    path('product/<int:pk>',ProductView.as_view()),
    path('product/',ListProductView.as_view()),


]