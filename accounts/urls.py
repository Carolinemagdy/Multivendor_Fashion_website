from django.urls import path
from .views import *

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('register/vendor/', VendorRegisterView.as_view()),
    path('register/customer/', CustomerRegisterView.as_view()),
    path('login/', LoginView.as_view()),
    path('', ListUserAPIView.as_view()),
    path('customer/', ListCustomerAPIView.as_view()),
    path('vendor/', ListVendorAPIView.as_view()),
    path('<int:pk>/', UserRetrtieveUpdateDestroyAPIView.as_view()),
    path('customer/<int:pk>/', CustomerRetrtieveUpdateDestroyAPIView.as_view()),
    path('vendor/<int:pk>/', VendorRetrtieveUpdateDestroyAPIView.as_view()),

]