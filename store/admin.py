from pickle import NONE
from tkinter.messagebox import NO
from django.contrib import admin
from .models import *
from django.contrib.admin import SimpleListFilter
from django.contrib import messages

# Register your models here.

class OrderItemInline(admin.StackedInline):
    model = OrderItem
    extra=1

class PriceFilter(SimpleListFilter):
    title = 'price Filter'
    parameter_name='total_price'
    def lookups(self, request, model_admin):
        return [
            (1, '0-500'),
            (2, '500-100'),
            (3, '1000-5000'),
            (4, '5000-20000')
        ]
    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        filt_price = request.GET.get('parameter_name')
        return queryset.filter(
                    total_price__range=self.total_price_dict[filt_price]
                )

class OrderAdmin(admin.ModelAdmin):
    inlines=(OrderItemInline,)
    list_display=['pk','__str__','ref_code','user','cumulative_status','ordered','cancelled','delivered',
                  'created_at','customer_email','total_price','payment_type','billing_status']
    list_filter=['user','cancelled','ordered','delivered','total_price',
                 'payment_type','billing_status','cumulative_status',PriceFilter]
    list_display_links=['pk','__str__','ref_code','customer_email']

    search_fields=['pk','ref_code','cumulative_status','total_price',
                   'payment_type','address','city','zipcode']

    def customer_email(self, obj):
        email = obj.user.user.email
        return email

    def message_user(self, *args):
        pass

    def save_model(self, request, obj, form, change):
        if not change:
            try:
                Order.objects.get(user=obj.user,ordered=False)
                messages.set_level(request, messages.ERROR)
                messages.error(request,
                'No changes are permitted, Order can not be created the customer already has a not Ordered One \'Cart\'')
                return
            except:
                messages.success(request, "Changes made succeffuly!")
        messages.success(request, "Changes made succeffuly!")

        super(OrderAdmin, self).save_model(request, obj, form, change)
admin.site.register(Order,OrderAdmin)
            

class ProductInline(admin.StackedInline):
    model = Product
    extra=1

class CategoryAdmin(admin.ModelAdmin):
    inlines=(ProductInline,)
    list_display=['pk','name','is_active','ordering','created_at','description']
    list_display_links=['pk','name']
    list_filter=['is_active','created_at']
    search_fields=['pk','name','ordering','description']

class StockFilter(SimpleListFilter):
    title = 'stock Filter'
    parameter_name='in_stock_total'
    def lookups(self, request, model_admin):
        return [
            (1, '0-5'),
            (2, '5-20'),
            (3, '20-50'),
            (4, '50-500')
        ]
    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        filt_stock = request.GET.get('parameter_name')
        return queryset.filter(
                    in_stock_total__range=self.in_stock_total_dict[filt_stock])

class ProductAdmin(admin.ModelAdmin):
    inlines=(OrderItemInline,)
    list_display=['pk','name','price','vendor','category','created_at','is_active','in_stock_total']    
    list_filter=['category','vendor','is_active','created_at',StockFilter,PriceFilter]
    list_display_links=['pk','name']
    search_fields=['pk','name','description']

class OrderItemAdmin(admin.ModelAdmin):
    list_display=['pk','__str__','order','product','item_status','price','quantity']
    list_display_links=['pk','__str__']
    list_filter=['order','product','item_status','price','quantity',PriceFilter]
    search_fields=['pk','quantity','item_status']

admin.site.register(Category,CategoryAdmin)
admin.site.register(Product,ProductAdmin)
admin.site.register(OrderItem,OrderItemAdmin)
