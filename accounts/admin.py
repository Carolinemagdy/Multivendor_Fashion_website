import email
from django.contrib import admin
from django.contrib.auth.models import Group
from store.admin import ProductInline
from .models import *
from store.models import *
from django.contrib import messages

# # Register your models here.

admin.site.unregister(Group)
admin.site.site_header='Fashion Website'
admin.site.site_title='Multivendor '

class OrderInline(admin.StackedInline):
    model = Order
    extra=1
    max_num=1

class CustomerInline(admin.StackedInline):
    model = Customer
class VendorInline(admin.StackedInline):
    model = Vendor
# fields(,) -> same line 

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    inlines = (CustomerInline,VendorInline )
    list_display=['pk','email','is_vendor','is_customer','is_superuser','is_verified','created_at']
    list_filter=['is_customer','is_vendor','is_verified','created_at']
    list_display_links=['pk','email']
    search_fields=['pk','email','name']
    
class CustomerAdmin(admin.ModelAdmin):
    inlines=(OrderInline,)
    list_display=['pk','get_email','phone','country']
    list_display_links=['pk','get_email']
    search_fields=['pk','phone','country']

    def get_email(self, obj):
        email = obj.user.email
        return email


class VendorAdmin(admin.ModelAdmin):
    inlines=(ProductInline,)
    list_display=['pk','get_email','rating','area','description']
    list_display_links=['pk','get_email']
    search_fields=['pk','rating','area','description','address']

    def get_email(self, obj):
        email = obj.user.email
        return email

admin.site.register(Customer,CustomerAdmin)
admin.site.register(Vendor,VendorAdmin)
