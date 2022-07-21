from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)

# from django.contrib import messages, admin

# class ExampleAdmin(admin.ModelAdmin):
#     def message_user(self, *args):
#         pass

#     def save_model(self, request, obj, form, change):
#         super(ExampleAdmin, self).save_model(request, obj, form, change)
#         if obj.status == "OK":
#             messages.success(request, "OK!")
#         elif obj.status == "NO":
#             messages.error(request, "REALLY NOT OK!")

# def save_model(self, request, obj, form, change):
#     messages.set_level(request, messages.ERROR)
#     messages.error(request, 'No changes are permitted ..')

