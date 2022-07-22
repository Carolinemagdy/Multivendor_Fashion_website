from django.db import models
from accounts.models import *
import uuid
from django.utils.timezone import make_aware
from datetime import datetime
from django.db.models.signals import post_save
from django.dispatch import receiver
# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=50)
    description=models.CharField(max_length=500,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    is_active=models.BooleanField(default=True)
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    in_stock_total=models.IntegerField(default=1)
    is_active=models.BooleanField(default=True)
    def __str__(self):
        return self.name

@receiver(post_save, sender=Product)
def edit_orderItem(sender, instance, created, **kwargs):
    if not created:
        order_items=OrderItem.objects.filter(product=instance) & OrderItem.objects.filter(order__ordered=True)
        for one in order_items:
            one.price = instance.price * one.quantity
            one.save()

class Order(models.Model):
    user = models.ForeignKey(Customer, on_delete=models.CASCADE,related_name='customer_order')
    ref_code = models.CharField(default=uuid.uuid4().hex[:10].upper(), max_length=50, editable=False)
    STATUS_CHOICES = ((1,'Accepted'),(2,'Preparing'),(3,'Packed'),(4,'On The Way'))
    cumulative_status = models.IntegerField(choices=STATUS_CHOICES,null=True,blank=True)
    address = models.CharField(max_length=250)
    city = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    zipcode = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    total_price = models.DecimalField(max_digits=5, decimal_places=2,blank=True,default=0)
    billing_status = models.BooleanField(default=False) 
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField(blank=True,null=True)
    ordered = models.BooleanField(default=False)
    cancelled= models.BooleanField(default=False)
    delivered=models.BooleanField(default=False)
    PAYMENT_CHOICES = (('cash','Cash'),('card','Credit Card'))
    payment_type= models.CharField(max_length=4,choices=PAYMENT_CHOICES,default='cash')



    class Meta:
        ordering = ['-created_at',]
    
    def save(self, *args, **kwargs):
        if self.pk is None :
            self.ordered=False
            self.total_price=0
        if self.pk is None :

            try:
                Order.objects.get(user=self.user,ordered=False)
                return
            except:
                pass
        if self.ordered and not self.ordered_date: 
            self.ordered_date=make_aware(datetime.now())

        # Call the original save method
        super(Order, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.user.email} {self.ref_code}"



class OrderItem(models.Model):
    STATUS_CHOICES = ((1,'Accepted'),(2,'Preparing'),(3,'Packed'),(4,'On The Way'))

    order = models.ForeignKey(Order,
                              related_name='order_items',
                              on_delete=models.CASCADE)
    product = models.ForeignKey(Product,
                                related_name='items_order',
                                on_delete=models.CASCADE)
    item_status = models.IntegerField(choices=STATUS_CHOICES,null=True,blank=True)

    price = models.DecimalField(max_digits=5, decimal_places=2,blank=True)
    quantity = models.PositiveIntegerField(default=1)
    class Meta:

        unique_together = ('order', 'product',)
    
    def save(self, *args, **kwargs):
        self.price = self.product.price * self.quantity
        if self.quantity>self.product.in_stock_total:
            return
        # Call the original save method
        super(OrderItem, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.order} {self.product.name}"
    
@receiver(post_save, sender=OrderItem)
def edit_order(sender, instance, created, **kwargs):
    if not created:
        order_items=OrderItem.objects.filter(order=instance.order,order__ordered=True)
        if order_items:
            order_items.order_by('item_status')
            first=order_items.first()
            instance.order.cumulative_status=first.item_status
            instance.order.save()
        order_items=OrderItem.objects.filter(order=instance.order)
        instance.order.total_price=0
        for one in order_items:
            instance.order.total_price += one.price   
        instance.order.save()