from django.db import models
from accounts.models import *
from django.contrib import messages, admin

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=50)
    description=models.TextField(blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    is_active=models.IntegerField(default=1)
    ordering = models.IntegerField(unique=True,blank=False)

    class Meta:
        ordering = ['ordering']
        
    def __str__(self):
        return self.name
    
class Product(models.Model):
    name = models.CharField(max_length=60)
    price = models.IntegerField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE,related_name='product_category')
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE,related_name='product_vendor')
    description = models.CharField(
        max_length=250, default='', blank=True, null=True)
    product_max_price=models.CharField(max_length=255,blank=True)
    product_discount_price=models.CharField(max_length=255,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    in_stock_total=models.IntegerField(default=1)
    is_active=models.IntegerField(default=1)
    # image = models.ImageField(upload_to='uploads/products/')
    
    def save(self, *args, **kwargs):
        # Make sure this is the first save (pk should be None) and there is no unit_price set
        if self.pk is not None and self.price:
            # self.unit_price = self.item.default_price
        # elif not self.unit_price:
            order_items=OrderItem.objects.filter(product=self) & OrderItem.objects.filter(order__ordered=True)
            for one in order_items:
                one.price = self.price * one.quantity
                print(one.price)
                one.save()
                one.save()
                print(one.price)
        # Call the original save method
        super(Product, self).save(*args, **kwargs)
  
    
    def __str__(self):
        return self.name
  

class Order(models.Model):
    user = models.ForeignKey(Customer, default='', on_delete=models.CASCADE,related_name='customer_order')
    ref_code = models.CharField(max_length=20, blank=True, null=True)
    cumulative_status = models.IntegerField(default=1)
    address = models.CharField(max_length=250)
    city = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    zipcode = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    total_paid = models.DecimalField(max_digits=5, decimal_places=2,null=True)
    billing_status = models.BooleanField(default=False) 
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField(null=True)
    ordered = models.BooleanField(default=False)
    cancelled= models.BooleanField(default=False)
    delivered=models.BooleanField(default=False)
    PAYMENT_CHOICES = (('cash','Cash'),('card','Credit Card'))
    payment_type= models.CharField(max_length=4,choices=PAYMENT_CHOICES,default='cash')



# make the total paid auto calc
# order data from checkout function
# quantity must be less than total stock
    class Meta:
        ordering = ['-created_at',]
    
    def __str__(self):
        return str(self.created_at)

class OrderItem(models.Model):
    STATUS_CHOICES = ((1,'Accepted'),(2,'Preparing'),(3,'Packed'),(4,'On The Way'))

    order = models.ForeignKey(Order,
                              related_name='order_items',
                              on_delete=models.CASCADE)
    product = models.ForeignKey(Product,
                                related_name='items_order',
                                on_delete=models.CASCADE)
    item_status = models.IntegerField(choices=STATUS_CHOICES,default=0)

    price = models.DecimalField(max_digits=5, decimal_places=2,blank=True,null=True)
    quantity = models.PositiveIntegerField(default=1)

# if he update the price of the product we should call this 
    
    def save(self, *args, **kwargs):
        # Make sure this is the first save (pk should be None) and there is no unit_price set
        # if self.pk is None and not self.price:
            # self.unit_price = self.item.default_price
        # elif not self.unit_price:
        self.price = self.product.price * self.quantity
        if self.quantity>self.product.in_stock_total:
            return
        # Call the original save method
        super(OrderItem, self).save(*args, **kwargs)

    def __str__(self):
        return str('order '+self.product.name)


 #guest
    #  first_name = models.CharField(max_length=100)
    # last_name = models.CharField(max_length=100) 
    # email = models.CharField(max_length=100)
    # address = models.CharField(max_length=100)
    # zipcode = models.CharField(max_length=100)
    # place = models.CharField(max_length=100)
    # phone = models.CharField(max_length=100) 
    # created_at = models.DateTimeField(auto_now_add=True)
    # paid_amount = models.DecimalField(max_digits=8, decimal_places=2)
        # class Meta: 
        #     ordering = ['-created_at']

        # def __str__(self):
        #     return self.first_name

# class OrderItem(models.Model):
#     order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
#     product = models.ForeignKey(Product, related_name="items", on_delete=models.CASCADE)
#     vendor = models.ForeignKey(Vendor, related_name="items", on_delete=models.CASCADE)
#     vendor_paid = models.BooleanField(default=False)
#     price = models.DecimalField(max_digits=8, decimal_places=2)
#     quantity = models.IntegerField(default=1)

#     def __str__(self):
#         return str(self.id)

#     def get_total_price(self):
#         return self.price * self.quantity