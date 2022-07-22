import email
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from accounts.models import *
# # Register your models here.
# admin.site.register(User)
admin.site.register(Customer)
admin.site.register(Vendor)
admin.site.unregister(Group)
admin.site.site_header='Fashion Website'
admin.site.site_title='Multivendor '



class CustomerInline(admin.StackedInline):
    model = Customer
class VendorInline(admin.StackedInline):
    model = Vendor


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    inlines = (CustomerInline,VendorInline )

# class CustomerAdmin(admin.ModelAdmin):
#     fields=('phone','get_email',)
#     def get_email(self, obj):
#         email = obj.user.email
#         return email


# admin.site.register(Customer,CustomerAdmin)
